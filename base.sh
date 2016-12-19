#!/bin/bash
BASE_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ENV_PATH="$BASE_PATH/.env"
PACKAGES_FILE="$BASE_PATH/packages.pip"
VIRTUALENV_GIT="https://github.com/pypa/virtualenv.git"
VIRTUALENV_PATH="$ENV_PATH/virtualenv"
VIRTUALENV="$VIRTUALENV_PATH/virtualenv.py"
if [ ! -d $ENV_PATH ]; then
    echo "Creatin the virtual environment..."
    mkdir -p "$ENV_PATH"
    PYTHON=$(which python)
    GIT=$(which git)
    $GIT clone --depth 1 "$VIRTUALENV_GIT" "$VIRTUALENV_PATH"
    $PYTHON "$VIRTUALENV" "$ENV_PATH"
    if [ -r "$PACKAGES_FILE" ]; then
        $ENV_PATH/bin/pip install -r "$PACKAGES_FILE"
    fi
fi
