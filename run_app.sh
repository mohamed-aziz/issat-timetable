#!/bin/bash

fuser -k $1/tcp

export WORKON_HOME="/home/webuser/.virtualenvs"

source /usr/share/virtualenvwrapper/virtualenvwrapper.sh

echo "Running issat api on port $1"

workon issatso-api

# cd /home/webuser/Projects/devslack-landing/devslack-landing

pip install -r requirements_dev.txt

gunicorn -b 127.0.0.1:$1 web:application
