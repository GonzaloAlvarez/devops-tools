#!/bin/bash

BASE_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ENV_PATH="$BASE_PATH/.env"
if [ ! -d $ENV_PATH ]; then
    echo "Creatin the virtual environment..."
    VIRTUALENV=$(which virtualenv)
    if [ -z "$VIRTUALENV" ]; then
        PIP=$(which pip)
        if [ -z "$PIP" ]; then
            echo "FATAL: pip is missing, but required. Exiting."
            exit 1
        fi
        sudo $PIP install virtualenv
        VIRTUALENV=$(which virtualenv)
    fi
    $VIRTUALENV $ENV_PATH
    $ENV_PATH/bin/pip install -r packages.pip
fi


