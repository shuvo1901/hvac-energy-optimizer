# Upload to GitHub — https://github.com/shuvo1901/Sabbir-Hossain

I could not push directly (no git/gh credentials in this environment).
Do ONE of the options below — takes ~2 minutes.

## Option A — GitHub Desktop / web (easiest, no CLI install)

1. Go to https://github.com/shuvo1901/Sabbir-Hossain (it is currently EMPTY).
2. Click **Add file → Upload files**.
3. Drag in ALL files from `D:\Python research project` EXCEPT `.github`
   (web UI can't create dot-folders reliably — upload the rest first).
4. Commit as `feat: hvac energy optimizer v0.1.0`.
5. Then create `.github/workflows/ci.yml` via web: **Add file → Create new file**,
   paste the contents of the local `.github/workflows/ci.yml`, commit.

## Option B — Command line (full history + CI)

1. Install Git: https://git-scm.com/download/win and Python: https://www.python.org/downloads/
   (tick "Add python.exe to PATH"), then restart terminal.
2. Run:

```powershell
cd "D:\Python research project"
git init
git add .
git commit -m "feat: hvac energy optimizer v0.1.0"
git branch -M main
git remote add origin https://github.com/shuvo1901/Sabbir-Hossain.git
git push -u origin main
```

If push asks for login: use a **Personal Access Token** (GitHub → Settings →
Developer settings → PAT classic, scope `repo`) as the password.

## Verify

- Repo shows README with results table.
- `pytest -q` passes locally after `pip install -r requirements.txt`.
- Actions tab runs `ci` green.

## After upload (recommended)

- Add a release: GitHub → Releases → `v0.1.0`.
- Add topics: `hvac energy-optimization machine-learning ashrae mpc`.
- To publish: replace `data/synthetic_hvac.csv` with measured BMS data and
  re-run `python examples/run_demo.py`.
