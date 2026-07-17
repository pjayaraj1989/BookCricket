# BookCricket

A simulation of the classic "book cricket" game. Play a full limited-overs or
Test match either in your **web browser** (with live scorecards, animated
pop-ups, DRS, super overs and more) or in a plain **terminal**.

---

## 1. Prerequisites

You need these installed before anything else:

- **Python 3.10, 3.11, or 3.12.**
  Do **not** use Python 3.13 yet — the pinned `numpy` version doesn't build on
  it. Check your version with `python --version` (or `python3 --version`).
- **pip** (ships with Python).
- **A modern web browser** (Chrome, Firefox, Edge, Safari) — only for the
  browser UI.

Get Python from [python.org/downloads](https://www.python.org/downloads/).
On Windows, tick **"Add Python to PATH"** in the installer.

---

## 2. First-time setup

Download the project (via `git clone` or the GitHub "Download ZIP" button),
open a terminal **in the project folder**, then create an isolated environment
and install the dependencies. Do this once.

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Windows — PowerShell

```powershell
py -3.12 -m venv venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> If PowerShell blocks the activation script with a "running scripts is
> disabled" error, run this once in the same window and try again:
> `Set-ExecutionPolicy -Scope Process -Bypass`

### Windows — Command Prompt (cmd.exe)

```cmd
py -3.12 -m venv venv
venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Once the environment is **activated** (you'll see `(venv)` in the prompt), you
won't reinstall anything again — just re-activate it each new terminal session
before running the game (`source venv/bin/activate` on Linux/macOS,
`venv\Scripts\Activate.ps1` on Windows).

---

## 3. Run the game

There are two ways to play. **Activate the virtual environment first** (see
above) in every new terminal.

### Option A — Browser UI (recommended)

Start the local server:

**Linux / macOS**

```bash
python web/app.py
```

**Windows** (PowerShell or cmd)

```powershell
python web\app.py
```

Then open **[http://127.0.0.1:5050](http://127.0.0.1:5050)** in your browser
and play. Press `Ctrl+C` in the terminal to stop the server.

**Change the port**, e.g. to 5059:

| Shell | Command |
|-------|---------|
| Linux / macOS (bash/zsh) | `PORT=5059 python web/app.py` |
| Windows PowerShell | `$env:PORT=5059; python web\app.py` |
| Windows cmd.exe | `set PORT=5059 && python web\app.py` |

**Let other devices on your Wi-Fi join** (phone, another laptop): also set
`HOST=0.0.0.0`, then visit `http://<your-computer-ip>:5050` from the other
device. For example in PowerShell:
`$env:HOST="0.0.0.0"; $env:PORT=5059; python web\app.py`.

### Option B — Terminal / CLI

Play the whole match as text in the terminal:

**Linux / macOS**

```bash
python BookCricket.py
```

**Windows**

```powershell
python BookCricket.py
```

Follow the prompts to pick the league, format, teams and venue.

**Auto-play** (the computer simulates a whole match on its own):

```bash
python BookCricket.py autoplay <overs> [test] [fast]
```

- `<overs>` — overs per side, e.g. `20`. Use `0` together with `test` for a
  Test match.
- `test` — play a Test match instead of limited-overs.
- `fast` — skip the per-ball pauses.

Example: `python BookCricket.py autoplay 20 fast`.

> Note: auto-play validates player names against Wikipedia, so it needs an
> internet connection. Normal interactive play (the prompt-driven CLI and the
> browser UI) works fully offline.

---

## 4. Hosting it on the internet (Render.com free tier)

The repo contains a `render.yaml` blueprint, so deploying is point-and-click:

1. Push this repo to GitHub (public or private).
2. Sign up at [render.com](https://render.com) (free, can sign in with GitHub).
3. In the Render dashboard: **New +** → **Blueprint** → connect this repo.
   Render reads `render.yaml` and creates the service automatically.
4. Wait for the first build (a few minutes). Your game is then live at
   `https://your-app-name.onrender.com` — share the link with anyone.

Every `git push` to the connected branch redeploys automatically.

Notes for the hosted version:

- The Stop Server button and `/shutdown` endpoint are disabled (`PUBLIC=1`).
- At most `MAX_SESSIONS` (default 20) matches can run at once.
- Free-tier instances sleep after ~15 idle minutes: the next visitor waits
  ~30s for a cold start, and matches in progress are lost when it sleeps.

---

## 5. Teams and rosters

Teams live in `data/teams_*.json` — edit those files to create or update
squads.

A league can ship separate Test-match squads in a file named
`teams_<league>_test.json` (e.g. `teams_International_test.json`). When you pick
that league and then choose "Test match", those rosters are used instead;
leagues without a `_test` file fall back to their regular rosters.

Player photos, team flags, umpire/commentator pictures and misc event images
are optional — drop them into the folders under `resources/` (each has a
`README.md` explaining the naming convention). Anything missing falls back to
initials or an emoji.

---

## 6. Troubleshooting

- **`python: command not found`** — try `python3` (Linux/macOS) or `py`
  (Windows).
- **`pip install` fails building numpy** — you're almost certainly on Python
  3.13. Install Python 3.12 and recreate the venv with it (`py -3.12 -m venv
  venv` on Windows, `python3.12 -m venv venv` on Linux/macOS).
- **Port already in use** — start with a different `PORT` (see the table
  above).
- **`PORT=5059 python ...` "not recognized" on Windows** — that inline syntax
  is Linux/macOS only; use the PowerShell/cmd forms in the port table.
