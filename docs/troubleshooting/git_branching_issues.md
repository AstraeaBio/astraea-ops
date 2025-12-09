# Git Branching Issues and Non-Fast-Forward Push Errors

## Overview

Common issues encountered with Git branching, merging, and workflow management.

## Symptoms

- Typical error:
> ! [rejected] main -> main (non-fast-forward)  
> error: failed to push some refs  
> hint: Updates were rejected because the tip of your current branch is behind its remote counterpart.
- `error: src refspec main does not match any`
- fatal: not a git repository (or any of the parent directories): .git`
- Merge conflicts
- Merge conflicts
- Detached HEAD state
- Unable to push to remote
- Branch synchronization problems
- Lost commits

## Diagnosis

- Local `main` is behind remote.
- You’re trying to push without updating.
- Sometimes mixed with uncommitted local changes.
- The hidden `.git` folder is missing (raw files only) or the local branch name does not match the remote (`master` vs `main`).

## Common Causes

1. **Divergent branch histories**: Local and remote branches have diverged
2. **Uncommitted changes blocking operations**: Working directory not clean
3. **Incorrect branch checkout**: Working on wrong branch
4. **Merge conflicts**: Concurrent changes to same files
5. **Empty Repository / No Commits**: Trying to push a branch that has no history yet
6. **Branch Name Mismatch**: Local is `master`, remote is `main`

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

## 8: Initializing a Copied Repository (Fatal: not a git repository)
If you copied files but lost the git history, you must initialize and force a merge of unrelated histories.
```bash
# Initialize new repo
git init

# Set default branch name
git branch -M main

# Add remote
git remote add origin [https://github.com/AstraeaBio/astraea-ops](https://github.com/AstraeaBio/astraea-ops)

# Sync history (Crucial step for copied repos)
git pull origin main --allow-unrelated-histories

# Push changes
git add .
git commit -m "Merging local copied changes"
git push -u origin main
```

### 9: Fix 'src refspec main does not match any'
This error occurs if you haven't committed yet (branch doesn't exist) or if your local branch is named master.
```bash
# 1. Ensure changes are staged
git add .

# 2. Ensure at least one commit exists
git commit -m "Saving work before push"

# 3. Force branch name to 'main'
git branch -M main

# 4. Push
git push -u origin main
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

2025-12-09
