
# accept arguments workspace name, and overs
# usage: ./run.sh <workspace_name> <overs>

WORKSPACE=$1
OVERS=$2

cd $WORKSPACE
python -m pip install --upgrade pip
# virtual environment is created by default in GitHub Actions
pip install -r requirements.txt
python3 BookCricket.py autoplay $OVERS