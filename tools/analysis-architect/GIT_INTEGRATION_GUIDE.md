# Git Integration Setup Guide
**Analysis Architect - Distributed Team Collaboration**

---

## 🎯 What This Does

Git integration enables your distributed team to collaborate on project tracking without manual git commands. The Streamlit UI automatically:

- **Pulls** latest changes when you open a project
- **Commits & pushes** your changes when you click "Save"
- **Warns** about conflicts before overwriting others' work
- **Shows** who last updated the project and when

No git commands needed - just use the UI normally!

---

## 🚀 One-Time Setup for Team Members

### Step 1: Clone the Repository

```bash
# Clone the repo to your local machine
git clone https://github.com/AstraeaBio/astraea-ops.git
cd astraea-ops/tools
```

### Step 2: Install Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt
```

### Step 3: Configure Git User

**Option A: Via Streamlit UI (Easiest)**

1. Run the app: `streamlit run project_tracker_ui.py`
2. Look for the "⚠️ Git Setup Required" section in the sidebar
3. Follow the instructions shown (copy the git config commands)

**Option B: Via Command Line**

```bash
# Configure your name and email for commits
git config user.name "Your Full Name"
git config user.email "your.email@example.com"
```

**Option C: Via Streamlit Secrets File**

```bash
# Copy the example secrets file
cd /mnt/t/0_Organizational/astraea-ops/tools
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit secrets.toml with your information
nano .streamlit/secrets.toml
```

Edit the file:
```toml
[git]
user_name = "Sharon Chen"  # Your actual name
user_email = "sharon@astraeabio.com"  # Your actual email
auto_pull = true
auto_push = true
```

### Step 4: Test the Integration

1. Open Streamlit app: `streamlit run project_tracker_ui.py`
2. Select a project from the dropdown
3. Go to "Update Components" tab
4. Make a small change (e.g., update a note)
5. Click "Save Changes"
6. You should see: "✅ Saved and synced: [Component Name]"

✅ **Setup complete!** You're ready to collaborate.

---

## 📋 Daily Workflow

### Starting Your Day

1. Open the Streamlit app:
   ```bash
   cd /mnt/t/0_Organizational/astraea-ops/tools
   streamlit run project_tracker_ui.py
   ```

2. The app **automatically pulls** latest changes from GitHub

3. Check the sidebar for "📝 Last Updated" to see who worked on the project recently

### Making Updates

1. Select your project from the dropdown
2. Navigate to the "Update Components" tab
3. Select the component you're working on
4. Make your updates:
   - Change status (not_started → in_progress → completed)
   - Update time used
   - Add notes about your progress
5. Click "💾 Save Changes"
6. The app will:
   - ✅ Save the file locally
   - 🔍 Check for conflicts with remote
   - 📝 Create a commit with a descriptive message
   - ⬆️ Push to GitHub automatically

### Understanding Sync Status

Check the sidebar for your project's sync status:

- 🟢 **Up to date** - Your local copy matches GitHub
- 🔵 **Local changes** - You have commits not yet pushed
- 🟡 **Pull available** - Someone else made changes, pull to get them
- 🔴 **Conflict** - Your changes and remote changes overlap

### Manual Sync Options

If you need to manually sync:

- **⬇️ Pull** button: Get latest changes from GitHub
- **⬆️ Push** button: Push your local commits (rarely needed)

---

## ⚠️ Handling Conflicts

### What is a Conflict?

A conflict happens when:
1. You open a project
2. A teammate updates the same project
3. You try to save your changes

### How to Resolve

**The app will warn you:**
> ⚠️ Someone else modified this file. Pull their changes first.

**Steps to resolve:**

1. **Note your changes** - Copy your updates or take a screenshot
2. **Pull latest** - Click "⬇️ Pull" button in sidebar
3. **Re-apply your changes** - Make your updates again in the fresh copy
4. **Save** - Click "Save Changes" again

**Why this happens:**
- You and a teammate edited the same `project.toml` file
- Git doesn't know which version to keep

**How to avoid:**
- Communicate in Slack about what you're working on
- Make frequent small saves (not one big update at end of day)
- Check "Last Updated" before making major changes

---

## 🛠️ Troubleshooting

### Issue: "Git user name not configured"

**Problem:** Git doesn't know who you are

**Solution:**
```bash
git config user.name "Your Full Name"
git config user.email "your.email@example.com"
```

Or create `.streamlit/secrets.toml` (see Step 3 above)

---

### Issue: "Network error - working offline"

**Problem:** Cannot reach GitHub (no internet or VPN issue)

**Solution:**
- Your changes are saved locally - don't worry!
- The app will sync when you're back online
- You can continue working offline

**To sync later:**
- Reconnect to internet
- Click "⬇️ Pull" then make any edit and "Save" to trigger push

---

### Issue: "Permission denied - contact repository admin"

**Problem:** You don't have write access to the repository

**Solution:**
- Contact Trevor or repository admin
- They need to add you as a collaborator on GitHub

**Check your access:**
```bash
git remote -v
# Should show: https://github.com/AstraeaBio/astraea-ops.git
```

---

### Issue: "Push rejected - remote has changes"

**Problem:** Someone pushed changes while you were working

**Solution:**
1. Click "⬇️ Pull" to get their changes
2. Your changes may be overwritten - check the file
3. Re-apply any lost changes
4. Click "Save Changes" again

---

### Issue: Seeing "🔵 Local changes (not pushed)"

**Problem:** You have commits that aren't on GitHub yet

**Solution:**
- Click "Save Changes" on any component to trigger a push
- Or manually run: `git push origin main` in terminal

---

### Issue: App is slow or freezing

**Problem:** Git operations taking too long

**Possible causes:**
- Slow network connection
- Large repository
- GitHub is down

**Solution:**
- Check your internet speed
- Try again in a few minutes
- Disable auto-push temporarily:
  - Edit `.streamlit/secrets.toml`
  - Set `auto_push = false`
  - Use manual "Push" button when ready

---

## 🔍 Advanced: Understanding Git Status

### Sidebar Information

**📝 Last Updated**
- Shows who last committed changes
- Shows when they committed (e.g., "2 hours ago")

**📜 Recent Changes**
- Click to expand
- See last 5 commits
- Review what changed and when

**Sync Status**
- Updated every time you interact with the app
- Fetches from GitHub in the background

---

## 💡 Best Practices

### 1. Pull Before Major Work

Before starting a big update session:
- Click "⬇️ Pull" to get latest changes
- Check "Last Updated" to see if anyone else is working

### 2. Save Frequently

Don't wait until end of day:
- Save after each component update
- Small frequent commits are better than one big one
- Easier to resolve conflicts

### 3. Use Descriptive Notes

When updating components:
- Add notes about what you did
- Helps teammates understand your work
- Commit messages are auto-generated from this

### 4. Communicate

Use Slack/email to coordinate:
- "I'm updating the Mayo Liver project now"
- Reduces chance of conflicts
- Team works more efficiently

### 5. Check Recent Changes

Before editing a project:
- Expand "📜 Recent Changes" in sidebar
- See if anyone edited recently
- Coordinate if needed

---

## 🔐 Security Notes

### What Gets Committed

**Included in git:**
- `project.toml` files (project tracking data)
- All project metadata and component status

**NOT included in git:**
- `.streamlit/secrets.toml` (your personal config)
- Any files in `.gitignore`

### Your GitHub Credentials

- Git uses SSH keys or HTTPS tokens
- Never share your GitHub password
- Use personal access tokens for HTTPS

### Repository Permissions

- Only team members with write access can push
- Contact admin if you get permission errors
- Repository is private (not public)

---

## 📚 Additional Resources

### Git Basics

If you want to understand git better:
- [Git Tutorial](https://git-scm.com/docs/gittutorial)
- [GitHub Guides](https://guides.github.com/)

### Streamlit

Understanding the UI framework:
- [Streamlit Docs](https://docs.streamlit.io/)

### Getting Help

**For git integration issues:**
- Check this guide first
- Ask in team Slack channel
- Contact Trevor for technical help

**For project tracking issues:**
- See main README.md
- See CLAUDE.md for development docs

---

## 🎓 Training Video

*Coming soon: Screen recording of complete workflow*

---

## 📞 Support

**Questions?** Contact:
- **Git Integration**: Trevor McKee
- **Project Tracking**: Trang Vu
- **General Support**: Team Slack #analysis-architect

---

**Last Updated:** 2024-12-24
**Version:** 1.0
