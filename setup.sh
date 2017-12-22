#!/bin/bash

echo 'Beginning installation...'

# Create myndpool_main virtualenv and switch to it
echo 'Creating virtual environment for myndpool_main...'
virtualenv myndpool_main
source myndpool_main/bin/activate

# Install requirements.txt
echo 'Installing Python packages...'
pip install -r requirements.txt
python -m spacy download en

# Train Rasa.AI chatbot
echo 'Training Rasa chatbot...'
./train_dialogue.sh
./train_nlu.sh

# Install MongoDB (assuming Ubuntu 16.04)
echo 'Installing MongoDB...'
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo service mongod start

echo 'myndpool_main successfully installed!'


# Create sense_server virtual environment and switch to it
echo 'Creating virtual environment for sense_server'
deactivate # Exit from myndpool_main
virtualenv sense_server
source sense_server/bin/activate

# Install sense_server Python dependencies
echo 'Installing '
pip install -r requirements.txt
