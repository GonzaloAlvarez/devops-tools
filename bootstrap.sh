#!/bin/bash
BASE_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ENV_PATH="$BASE_PATH/.env"
PYTHON_PACKAGES="$BASE_PATH/packages.pip"
VIRTUALENV_GIT="https://github.com/pypa/virtualenv.git"
VIRTUALENV_PATH="$ENV_PATH/virtualenv"
VIRTUALENV="$VIRTUALENV_PATH/virtualenv.py"
export GEM_HOME="$ENV_PATH/gems"
export GEM_PATH=""
RUBY_PACKAGES="$BASE_PATH/ruby.packages"
NODE_BASE="$ENV_PATH/lib"
NODE_PACKAGES="$BASE_PATH/node.packages"

function log() {
    echo $@
}

if [ ! -d $ENV_PATH ]; then
    log "Creatin the virtual environment..."
    mkdir -p "$ENV_PATH"
    PYTHON=$(which python)
    GIT=$(which git)
    log "Retrieving virtualenv"
    $GIT clone --depth 1 -q "$VIRTUALENV_GIT" "$VIRTUALENV_PATH"
    log "Executing virtualenv"
    $PYTHON "$VIRTUALENV" "$ENV_PATH"
    if [ -r "$PYTHON_PACKAGES" ]; then
        log "Installing python dependencies"
        $ENV_PATH/bin/pip install -q -r "$PYTHON_PACKAGES"
    fi
fi
if [ ! -d $GEM_HOME ]; then
    mkdir -p "$GEM_HOME"
    if [ -r "$RUBY_PACKAGES" ]; then
        log "Bootstraping ruby dependencies"
        while read rubygem; do
            gem install $rubygem --quiet
        done < "$RUBY_PACKAGES"
    fi
fi
if [ -r "$NODE_PACKAGES" ]; then
    if [ ! -x $ENV_PATH/bin/node ]; then
        log "Bootstrapping node"
        $ENV_PATH/bin/pip install -q nodeenv
        $ENV_PATH/bin/nodeenv -p
    fi
    source $ENV_PATH/bin/activate
    if [ $(ls -1 "$NODE_BASE/node_modules" | wc -l) -le 1 ]; then
        log "Bootstrapping node dependencies"
        while read nodepkg; do
            npm install ${nodepkg}@latest --loglevel silent --prefix $NODE_BASE
        done < $NODE_PACKAGES
    fi
fi
