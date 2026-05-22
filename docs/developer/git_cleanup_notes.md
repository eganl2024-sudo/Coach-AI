# Git cleanup steps for Coach AI

Run these commands from PowerShell in the project root:

```powershell
# 1) See current status
git status

# 2) Unstage everything if something was staged
git reset

# 3) Stop tracking the virtualenv folder, but keep it on disk
git rm -r --cached .venv

# 4) Optionally, remove other accidentally tracked junk using --cached
# (uncomment and adjust if you see other folders you want to untrack)
# git rm -r --cached .streamlit
# git rm -r --cached .ipynb_checkpoints

# 5) Stage only the real project files
git add app.py pages src data tests requirements.txt *.md *.csv

# 6) Make a clean initial commit
git commit -m "Initial commit for Coach AI app (without .venv)"

# 7) Optional: configure line endings to avoid LF/CRLF warnings
git config core.autocrlf true
```
