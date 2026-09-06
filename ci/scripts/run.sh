
# accept arguments workspace name, overs, and optional extra BookCricket.py
# autoplay flags ("test", "fast", "skipnames")
# usage: ./run.sh <workspace_name> <overs> [test] [fast] [skipnames]
#
# "skipnames" bypasses the autoplay Wikipedia roster check. That check makes
# one request per player, so several matches in a row get HTTP 429 and the run
# dies on an unrelated network limit - always pass it when running more than
# one match in a job.

WORKSPACE=$1
OVERS=$2
shift 2
EXTRA_ARGS="$@"

cd $WORKSPACE
python -m pip install --upgrade pip
# virtual environment is created by default in GitHub Actions
pip install -r requirements.txt
python3 BookCricket.py autoplay $OVERS $EXTRA_ARGS