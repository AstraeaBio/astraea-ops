# Git Branching Issues and Non-Fast-Forward Push Errors

## Overview

Common issues encountered with Git branching, merging, and workflow management.

## Symptoms

- Typical error:
> ! [rejected] main -> main (non-fast-forward)  
> error: failed to push some refs  
> hint: Updates were rejected because the tip of your current branch is behind its remote counterpart.
- Merge conflicts
- Detached HEAD state
- Unable to push to remote
- Branch synchronization problems
- Lost commits

## Diagnosis

- Local `main` is behind remote.
- You’re trying to push without updating.
- Sometimes mixed with uncommitted local changes.

## Common Causes

1. **Divergent branch histories**: Local and remote branches have diverged
2. **Uncommitted changes blocking operations**: Working directory not clean
3. **Incorrect branch checkout**: Working on wrong branch
4. **Merge conflicts**: Concurrent changes to same files

## Solutions

###  1: Resolve Merge Conflicts

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

###  2: Fix Detached HEAD

Recover from detached HEAD state:

```bash
# Create a branch from current position
git checkout -b new-branch-name

# Or return to an existing branch
git checkout main
```

###  3: Sync with Remote

Update your local branch with remote changes:

```bash
# Fetch latest changes
git fetch origin

# Rebase your changes on top
git rebase origin/main

# Or merge remote changes
git merge origin/main
```

###  4: Recover Lost Commits

Use reflog to find lost commits:

```bash
git reflog
git checkout <commit-hash>
```

## 5: Update from remote with rebase
```bash
git pull origin main --rebase
```
Resolve conflicts if present.

### 6. Push
```bash
git push origin main
```
## 7: If pulling a feature branch
```bash
git checkout trevor-spatial-additions
git status   # clean working tree required
git pull origin trevor-spatial-additions --rebase
git push origin trevor-spatial-additions
```
## Verification
- git status shows clean.
- git log --oneline --graph --decorate --all shows a linear history.
- 

## Prevention / Notes

- Never work directly on main for complex changes.
- Use feature branches:
  - git checkout -b feature/<short-desc>
  - Use PRs, not direct pushes to main.
- Pull/rebase before starting new work
- Create feature branches for all changes
- Commit frequently with descriptive messages
- Keep branches short-lived

## Related Resources

- [Git Documentation](https://git-scm.com/doc)

## Last Updated

2025-12-05
