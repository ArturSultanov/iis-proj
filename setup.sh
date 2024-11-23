# Create .venv and install dependencies
python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

./start.sh