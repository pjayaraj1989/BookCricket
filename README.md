# BookCricket
This emulates the good old book cricket game
Requires python3 to run.

Required python packages: colorama, numpy

To install them, run the command
pip install -r requirements.txt

On Linux:
# To run the program, run 
python3 BookCricket.py

On Windows (experimental):
Run the batch script CreateWindowsExe.bat
This will generate BookCricket.exe executable.
Just run it.

## Play in the browser (local)

Run `python3 web/app.py`, then open <http://127.0.0.1:5050>.

## Host it on the internet (Render.com free tier)

The repo contains a `render.yaml` blueprint, so deploying is point-and-click:

1. Push this repo to GitHub (public or private).
2. Sign up at <https://render.com> (free, can sign in with GitHub).
3. In the Render dashboard: New + -> Blueprint -> connect this repo.
   Render reads `render.yaml` and creates the service automatically.
4. Wait for the first build (a few minutes). Your game is then live at
   `https://your-app-name.onrender.com` - share the link with anyone.

Every `git push` to the connected branch redeploys automatically.

Notes for the hosted version:

- The Stop Server button and /shutdown endpoint are disabled (PUBLIC=1).
- At most MAX_SESSIONS (default 20) matches can run at once.
- Free-tier instances sleep after ~15 idle minutes: the next visitor waits
  ~30s for a cold start, and matches in progress are lost when it sleeps.

## Create new or update your existing teams here

data/*.json
