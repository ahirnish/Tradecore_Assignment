#!/bin/bash

# create virtualenv for python 3.6
echo 'Creating virtual environment for python3.6'
virtualenv --python=python3 venv

# activate python3 virtual environment
echo 'Activating python3 virtual environment'
source venv/bin/activate

# install pip requirements
echo 'Installing requirements...'
pip install -r requirements.txt

# move to project directory
echo 'Jumping into project directory: tradecore'
cd tradecore/

# migrate database
echo 'Migrating database...'
echo 'python manage.py migrate'
python manage.py migrate

# Load fixtures
echo 'Loading fixtures...'
echo 'python manage.py loaddata api/fixtures/initial_data.json'
python manage.py loaddata api/fixtures/initial_data.json

# Run server
echo 'start server'
echo 'python manage.py runserver'
python manage.py runserver