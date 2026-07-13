
# accept arguments workspace name, overs, and optional extra BookCricket.py
# autoplay flags ("test", "fast")
# usage: ./run.sh <workspace_name> <overs> [test] [fast]

WORKSPACE=$1
OVERS=$2
shift 2
EXTRA_ARGS="$@"

cd $WORKSPACE
python -m pip install --upgrade pip
# virtual environment is created by default in GitHub Actions
pip install -r requirements.txt
python3 BookCricket.py autoplay $OVERS $EXTRA_ARGS