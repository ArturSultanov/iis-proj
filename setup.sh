# Create .venv and install dependencies

sudo apt install python3.12-venv

python3.12 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

deactivate

./setup_mysql.sh

./start.sh