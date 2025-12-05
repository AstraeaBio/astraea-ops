# Git Branching Issues

## Overview

Common issues encountered with Git branching, merging, and workflow management.

## Symptoms

- Merge conflicts
- Detached HEAD state
- Unable to push to remote
- Branch synchronization problems
- Lost commits

## Common Causes

1. **Divergent branch histories**: Local and remote branches have diverged
2. **Uncommitted changes blocking operations**: Working directory not clean
3. **Incorrect branch checkout**: Working on wrong branch
4. **Merge conflicts**: Concurrent changes to same files

## Solutions

### Solution 1: Resolve Merge Conflicts

When encountering merge conflicts:

```bash
# View conflicting files
git status

# Edit conflicting files to resolve conflicts
# Look for conflict markers: <<<<<<<, =======, >>>>>>>

# After resolving, stage the files
git add <resolved-file>

# Complete the merge
git commit
```

### Solution 2: Fix Detached HEAD

Recover from detached HEAD state:

```bash
# Create a branch from current position
git checkout -b new-branch-name

# Or return to an existing branch
git checkout main
```

### Solution 3: Sync with Remote

Update your local branch with remote changes:

```bash
# Fetch latest changes
git fetch origin

# Rebase your changes on top
git rebase origin/main

# Or merge remote changes
git merge origin/main
```

### Solution 4: Recover Lost Commits

Use reflog to find lost commits:

```bash
git reflog
git checkout <commit-hash>
```

## Prevention

- Pull/rebase before starting new work
- Create feature branches for all changes
- Commit frequently with descriptive messages
- Keep branches short-lived

## Related Resources

- [Git Documentation](https://git-scm.com/doc)

## Last Updated

2025-12-05
