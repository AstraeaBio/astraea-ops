"""
Git Operations Module for Analysis Architect
=============================================
Handles all git operations for distributed team collaboration.

Key Features:
- Automatic pull on app load
- Automatic commit and push on save
- Conflict detection before push
- User-friendly error messages
- No external dependencies (uses subprocess + git CLI)

Author: Analysis Architect Team
Version: 1.0
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from functools import lru_cache
import time

# TOML imports
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class GitManager:
    """
    Manages git operations for project.toml files.

    Uses subprocess to call git CLI directly - no external Python dependencies.
    All operations fail gracefully with user-friendly error messages.
    """

    def __init__(self, repo_path: Path):
        """
        Initialize GitManager.

        Args:
            repo_path: Path to git repository root
        """
        self.repo_path = Path(repo_path).resolve()
        self.is_git_repo = self._check_is_git_repo()
        self.user_config = self._load_user_config()
        self._last_fetch_time = 0
        self._fetch_interval = 60  # Fetch at most once per minute

    def _check_is_git_repo(self) -> bool:
        """Check if directory is a git repository."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--is-inside-work-tree'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return False

    def _load_user_config(self) -> Dict:
        """
        Load user's git configuration.

        Priority order:
        1. Streamlit secrets (.streamlit/secrets.toml)
        2. Git config (user.name and user.email)
        3. Empty dict (user needs to configure)

        Returns:
            Dict with user_name, user_email, auto_pull, auto_push
        """
        config = {
            'user_name': '',
            'user_email': '',
            'auto_pull': True,
            'auto_push': True
        }

        # Try to load from Streamlit secrets
        secrets_path = self.repo_path / 'tools' / '.streamlit' / 'secrets.toml'
        if secrets_path.exists():
            try:
                with open(secrets_path, 'rb') as f:
                    secrets = tomllib.load(f)
                    if 'git' in secrets:
                        config['user_name'] = secrets['git'].get('user_name', '')
                        config['user_email'] = secrets['git'].get('user_email', '')
                        config['auto_pull'] = secrets['git'].get('auto_pull', True)
                        config['auto_push'] = secrets['git'].get('auto_push', True)
                        return config
            except Exception:
                pass  # Fall through to git config

        # Fall back to git config
        try:
            name_result = subprocess.run(
                ['git', 'config', 'user.name'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if name_result.returncode == 0:
                config['user_name'] = name_result.stdout.strip()

            email_result = subprocess.run(
                ['git', 'config', 'user.email'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if email_result.returncode == 0:
                config['user_email'] = email_result.stdout.strip()
        except Exception:
            pass

        return config

    def _run_git_command(self, args: List[str], timeout: int = 30) -> Tuple[bool, str, str]:
        """
        Run a git command and return results.

        Args:
            args: Git command arguments (e.g., ['pull', 'origin', 'main'])
            timeout: Command timeout in seconds

        Returns:
            (success: bool, stdout: str, stderr: str)
        """
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return (result.returncode == 0, result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            return (False, '', 'Command timed out')
        except FileNotFoundError:
            return (False, '', 'Git command not found. Please install git.')
        except Exception as e:
            return (False, '', str(e))

    def _smart_fetch(self) -> bool:
        """
        Fetch from remote, but only if enough time has passed.

        Returns:
            True if fetch succeeded or was skipped, False if failed
        """
        current_time = time.time()
        if current_time - self._last_fetch_time < self._fetch_interval:
            return True  # Skip fetch, too soon

        success, _, _ = self._run_git_command(['fetch', 'origin'], timeout=15)
        if success:
            self._last_fetch_time = current_time
        return success

    def validate_user_config(self) -> Tuple[bool, List[str]]:
        """
        Validate that user has git configured properly.

        Returns:
            (is_valid: bool, issues: List[str])
        """
        issues = []

        if not self.user_config['user_name']:
            issues.append('Git user name not configured')

        if not self.user_config['user_email']:
            issues.append('Git user email not configured')

        # Check if remote is configured
        if self.is_git_repo:
            success, stdout, _ = self._run_git_command(['remote', '-v'], timeout=5)
            if not success or not stdout.strip():
                issues.append('No git remote configured')

        return (len(issues) == 0, issues)

    def auto_pull_on_load(self) -> Tuple[bool, str]:
        """
        Pull latest changes from remote before loading project.

        Returns:
            (success: bool, message: str)
        """
        if not self.is_git_repo:
            return (True, '')

        if not self.user_config.get('auto_pull', True):
            return (True, 'Auto-pull disabled')

        # Fetch first
        if not self._smart_fetch():
            return (False, 'Could not reach remote repository')

        # Check if behind remote
        success, stdout, _ = self._run_git_command(
            ['rev-list', 'HEAD..origin/main', '--count'],
            timeout=5
        )

        if not success:
            # Might be on a different branch or no remote tracking
            return (True, '')

        commits_behind = int(stdout.strip() or 0)
        if commits_behind == 0:
            return (True, '')

        # Pull changes
        success, stdout, stderr = self._run_git_command(
            ['pull', '--rebase', 'origin', 'main'],
            timeout=30
        )

        if success:
            return (True, f'Pulled {commits_behind} change(s) from remote')
        else:
            # Check for specific error types
            error_msg = stderr.lower()
            if 'conflict' in error_msg:
                return (False, 'Merge conflict detected. Please resolve manually.')
            elif 'network' in error_msg or 'could not resolve host' in error_msg:
                return (False, 'Network error - working offline')
            else:
                return (False, f'Pull failed: {stderr[:100]}')

    def auto_commit_and_push(self, filepath: Path, commit_message: Optional[str] = None) -> Tuple[bool, str]:
        """
        Commit and push changes after save.

        Args:
            filepath: Path to file that was saved
            commit_message: Optional custom message (auto-generated if not provided)

        Returns:
            (success: bool, message: str)
        """
        if not self.is_git_repo:
            return (True, 'Not a git repository')

        if not self.user_config.get('auto_push', True):
            return (True, 'Auto-push disabled')

        # Make filepath relative to repo root
        try:
            rel_filepath = Path(filepath).relative_to(self.repo_path)
        except ValueError:
            return (False, 'File is outside repository')

        # Check if file has changes
        success, stdout, _ = self._run_git_command(
            ['diff', '--name-only', str(rel_filepath)],
            timeout=5
        )

        if success and not stdout.strip():
            # No changes to commit
            return (True, 'No changes to commit')

        # Stage the file
        success, _, stderr = self._run_git_command(
            ['add', str(rel_filepath)],
            timeout=5
        )

        if not success:
            return (False, f'Could not stage file: {stderr}')

        # Generate commit message if not provided
        if not commit_message:
            commit_message = f'Update {rel_filepath.name}'

        # Commit
        success, _, stderr = self._run_git_command(
            ['commit', '-m', commit_message],
            timeout=10
        )

        if not success:
            if 'nothing to commit' in stderr.lower():
                return (True, 'No changes to commit')
            return (False, f'Commit failed: {stderr}')

        # Push to remote
        success, _, stderr = self._run_git_command(
            ['push', 'origin', 'main'],
            timeout=30
        )

        if success:
            return (True, 'Changes synced successfully')
        else:
            error_msg = stderr.lower()
            if 'network' in error_msg or 'could not resolve host' in error_msg:
                return (False, 'Network error - changes saved locally but not synced')
            elif 'permission denied' in error_msg or 'authentication failed' in error_msg:
                return (False, 'Permission denied - contact repository admin')
            elif 'rejected' in error_msg:
                return (False, 'Push rejected - remote has changes. Pull first.')
            else:
                return (False, f'Push failed: {stderr[:100]}')

    def check_for_conflicts(self, filepath: Path) -> Tuple[bool, str]:
        """
        Check if remote has conflicting changes before push.

        Args:
            filepath: Path to file to check

        Returns:
            (has_conflicts: bool, message: str)
        """
        if not self.is_git_repo:
            return (False, '')

        # Fetch latest changes
        if not self._smart_fetch():
            return (False, '')  # Network issue, but not a conflict

        # Make filepath relative to repo root
        try:
            rel_filepath = Path(filepath).relative_to(self.repo_path)
        except ValueError:
            return (False, '')

        # Check if remote has changes to this file
        success, stdout, _ = self._run_git_command(
            ['diff', 'HEAD..origin/main', '--name-only', '--', str(rel_filepath)],
            timeout=5
        )

        if success and stdout.strip():
            return (
                True,
                'Someone else modified this file. Pull latest changes first to avoid conflicts.'
            )

        return (False, '')

    def get_git_status(self, filepath: Optional[Path] = None) -> Dict:
        """
        Get git status information for display in UI.

        Args:
            filepath: Optional specific file to check

        Returns:
            Dict with status information
        """
        status = {
            'last_commit_author': 'Unknown',
            'last_commit_date': 'Unknown',
            'last_commit_message': '',
            'is_modified': False,
            'is_up_to_date': True,
            'sync_status': 'unknown'
        }

        if not self.is_git_repo:
            return status

        # Get last commit info
        args = ['log', '-1', '--pretty=format:%an|%ar|%s']
        if filepath:
            try:
                rel_filepath = Path(filepath).relative_to(self.repo_path)
                args.extend(['--', str(rel_filepath)])
            except ValueError:
                pass

        success, stdout, _ = self._run_git_command(args, timeout=5)
        if success and stdout:
            parts = stdout.split('|', 2)
            if len(parts) == 3:
                status['last_commit_author'] = parts[0]
                status['last_commit_date'] = parts[1]
                status['last_commit_message'] = parts[2]

        # Check if file is modified
        if filepath:
            try:
                rel_filepath = Path(filepath).relative_to(self.repo_path)
                success, stdout, _ = self._run_git_command(
                    ['status', '--porcelain', str(rel_filepath)],
                    timeout=5
                )
                status['is_modified'] = bool(success and stdout.strip())
            except ValueError:
                pass

        # Check sync status (ahead/behind/diverged)
        self._smart_fetch()

        # Commits ahead
        success, stdout, _ = self._run_git_command(
            ['rev-list', 'origin/main..HEAD', '--count'],
            timeout=5
        )
        ahead = int(stdout.strip() or 0) if success else 0

        # Commits behind
        success, stdout, _ = self._run_git_command(
            ['rev-list', 'HEAD..origin/main', '--count'],
            timeout=5
        )
        behind = int(stdout.strip() or 0) if success else 0

        # Determine sync status
        if ahead > 0 and behind > 0:
            status['sync_status'] = 'diverged'
        elif ahead > 0:
            status['sync_status'] = 'ahead'
        elif behind > 0:
            status['sync_status'] = 'behind'
        else:
            status['sync_status'] = 'synced'

        status['is_up_to_date'] = (behind == 0)

        return status

    def get_commit_history(self, filepath: Optional[Path] = None, limit: int = 10) -> List[Dict]:
        """
        Get recent commit history.

        Args:
            filepath: Optional file to get history for
            limit: Maximum number of commits to return

        Returns:
            List of commit dicts with hash, author, date, message
        """
        if not self.is_git_repo:
            return []

        args = ['log', f'-{limit}', '--pretty=format:%h|%an|%ar|%s']
        if filepath:
            try:
                rel_filepath = Path(filepath).relative_to(self.repo_path)
                args.extend(['--', str(rel_filepath)])
            except ValueError:
                pass

        success, stdout, _ = self._run_git_command(args, timeout=10)
        if not success or not stdout:
            return []

        commits = []
        for line in stdout.strip().split('\n'):
            parts = line.split('|', 3)
            if len(parts) == 4:
                commits.append({
                    'hash': parts[0],
                    'author': parts[1],
                    'date': parts[2],
                    'message': parts[3]
                })

        return commits


def generate_commit_message(filepath: Path, project_data: Dict) -> str:
    """
    Auto-generate meaningful commit message from project data.

    Args:
        filepath: Path to project.toml file
        project_data: Loaded project data dict

    Returns:
        Commit message string
    """
    project_id = project_data.get('project_id', 'Unknown')
    project_name = project_data.get('project_name', 'Unknown Project')

    # Simple message for now - can be enhanced later
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    return f"Update {project_id}: {project_name} - {timestamp}"


def is_network_error(error_msg: str) -> bool:
    """Check if error message indicates network issue."""
    error_lower = error_msg.lower()
    network_keywords = [
        'network', 'could not resolve host', 'connection refused',
        'timeout', 'unable to access', 'failed to connect'
    ]
    return any(keyword in error_lower for keyword in network_keywords)


def format_git_error_for_user(error_msg: str) -> str:
    """
    Convert git error to user-friendly message.

    Args:
        error_msg: Raw git error message

    Returns:
        User-friendly error message
    """
    error_lower = error_msg.lower()

    if is_network_error(error_msg):
        return "Cannot reach GitHub. Check your internet connection. Changes are saved locally."

    if 'conflict' in error_lower:
        return "Someone else modified this file. Pull their changes first, then try again."

    if 'permission denied' in error_lower or 'authentication failed' in error_lower:
        return "You don't have permission to push to this repository. Contact your admin."

    if 'not a git repository' in error_lower:
        return "This directory is not a git repository. Initialize git first."

    # Default: return first 150 chars of error
    return error_msg[:150] + ('...' if len(error_msg) > 150 else '')
