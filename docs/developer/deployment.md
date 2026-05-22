# Coach AI - Deployment Guide

## Quick Start: Edit → Push → Live

Once set up, your workflow is:

```bash
# Make changes to your code, then:
git add .
git commit -m "Description of changes"
git push
```

That's it! Railway auto-deploys when you push.

---

## Initial Setup (One-Time)

### 1. Create GitHub Repository

```bash
# If you haven't already, initialize git
cd "C:\Users\ljega\Downloads\Coach AI"
git init

# Create a new repo on GitHub (github.com/new), then:
git remote add origin https://github.com/YOUR_USERNAME/coach-ai.git
git branch -M main
git add .
git commit -m "Initial commit"
git push -u origin main
```

### 2. Deploy to Railway

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `coach-ai` repository
4. Railway will auto-detect Streamlit and deploy

### 3. Set Your Password (Important!)

In Railway dashboard:
1. Go to your project → Variables tab
2. Add: `COACH_AI_PASSWORD` = `your-secure-password`
3. Railway will auto-redeploy with the new password

---

## Daily Workflow

### Making Changes

```bash
# 1. Edit your files locally
# 2. Test locally
streamlit run app.py

# 3. Commit and push
git add .
git commit -m "Added new drill category"
git push

# 4. Railway auto-deploys in ~2 minutes
```

### Checking Deployment Status

- Railway dashboard shows build logs
- Your app URL: `https://your-app-name.up.railway.app`

---

## Environment Variables

| Variable | Description | Where to Set |
|----------|-------------|--------------|
| `COACH_AI_PASSWORD` | App login password | Railway Variables |
| `PORT` | Server port (auto-set by Railway) | Auto |

### Local Development

Local development uses the fallback password `Coach_AI_2025` unless you set
`COACH_AI_PASSWORD` in your environment.

If you need to bypass auth temporarily on your own machine, set:
```powershell
$env:COACH_AI_DISABLE_AUTH="1"
```

To use a different local password instead:
```powershell
$env:COACH_AI_PASSWORD="your-local-password"
```

---

## Troubleshooting

### Build Fails
- Check `requirements.txt` has all dependencies
- Check Railway build logs for specific errors

### App Crashes
- Check Railway logs (Deployments → View Logs)
- Usually a missing import or file path issue

### Password Not Working
- Make sure `COACH_AI_PASSWORD` is set in Railway Variables
- Redeploy after changing variables

---

## File Structure

```
Coach AI/
├── app.py                 # Main entry point
├── pages/                 # Streamlit pages
├── src/                   # Backend modules
│   └── auth.py           # Authentication (password here)
├── data/                  # CSV data files
├── .streamlit/
│   └── config.toml       # Streamlit settings
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment command
└── .gitignore            # Files to exclude from git
```

---

## Useful Commands

```bash
# Check git status
git status

# See recent commits
git log --oneline -5

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Pull latest from GitHub
git pull

# Check current branch
git branch
```
