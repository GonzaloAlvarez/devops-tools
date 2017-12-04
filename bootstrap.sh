#!/bin/bash
BASE_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ENV_PATH="$BASE_PATH/.env"
DEPENDENCIES_FILE="$BASE_PATH/dependencies"
VIRTUALENV_GIT="https://github.com/pypa/virtualenv.git"
VIRTUALENV_PATH="$ENV_PATH/virtualenv"
VIRTUALENV="$VIRTUALENV_PATH/virtualenv.py"
NODE_BASE="$ENV_PATH/lib"
CONFIG_FILE="$BASE_PATH/config.yaml"
export GEM_HOME="$ENV_PATH/gems"
export GEM_PATH=""
export PYTHONPATH="$PYTHONPATH:$BASE_PATH"

# Debug and logging
# @Provides: logging
function log() {
    echo $@
}

# Environment base methods
# @Depends: logging
# @Provides: environment

function env_install() {
    if [ ! -d $ENV_PATH ]; then
        log "Creatin the virtual environment..."
        mkdir -p "$ENV_PATH"
    fi
}

# Python install and config
# @Provides: python
# @Depends: logging environment
function python_base() {
    env_install
    if [ ! -d "$VIRTUALENV_PATH" ]; then
        log "Installing virtualenv"
        PYTHON=$(which python)
        GIT=$(which git)
        $GIT clone --depth 1 -q "$VIRTUALENV_GIT" "$VIRTUALENV_PATH"
        log "Executing virtualenv"
        $PYTHON "$VIRTUALENV" "$ENV_PATH"
    fi
}

function python_install() {
    python_base
    log "Installing python dependencies [$@]"
    for requirement in "$@"; do
        $ENV_PATH/bin/pip install -q $requirement
    done
}

# Configuration load
# @Provides: configuration
# @Depends: python logging
function decrypt_configuration() {
    if [ ! -r "$CONFIG_FILE" ]; then
        if [ -r "$CONFIG_FILE.enc" ]; then
            if [ ! -x "$ANSIBLE_VALUE" ]; then
                python_install ansible
            fi
            log "Decrypting config file"
            $ENV_PATH/bin/ansible-vault decrypt -v --ask-vault-pass --output="$CONFIG_FILE" "${CONFIG_FILE}.enc"
        else
            log "No configuration file found. Exiting"
            exit 1
        fi
    fi
}

function parse_config() {
    while read line; do
        if [[ $line =~ ^# ]]; then
            continue
        fi
        VARIABLE_NAME=$(echo $line | cut -d ':' -f 1 | tr '[:lower:]' '[:upper:]')
        VALUE=$(echo $line | cut -d ':' -f 2- | cut -d '#' -f 1 | sed -e 's/^\s*//' | tr "'" '"')
        printf "$VARIABLE_NAME=$VALUE\n"
    done < $1
}

function load_configuration() {
    if [ ! -r "$CONFIG_FILE" ]; then
        decrypt_configuration
    fi
    CONFIG_VARS="$(parse_config $CONFIG_FILE)"
    while read line; do
        eval "export $line"
    done <<< "$CONFIG_VARS"
}

# Ruby install and config
# @Provides: ruby
# @Depends: python
function ruby_install() {
    if [ ! -x "$ENV_BASE/bin/gem" ]; then
        python_base
        $ENV_PATH/bin/pip install -q rubyenv
        $ENV_PATH/bin/rubyenv install 2.4.1
    fi
    mkdir -p "$GEM_HOME"
    log "Bootstraping ruby dependencies"
    for rubygem in "$@"; do
        $ENV_PATH/bin/gem install $rubygem --quiet
    done
}

# Node install and config
# @Provides: node
# @Depends: python
function node_eval() {
    source $ENV_PATH/bin/activate
}

function node_install() {
    if [ ! -x $ENV_PATH/bin/node ]; then
        python_base
        log "Bootstrapping node"
        $ENV_PATH/bin/pip install -q nodeenv
        $ENV_PATH/bin/nodeenv -p
    fi
    source $ENV_PATH/bin/activate
    log "Bootstrapping node dependencies"
    for nodepkg in "$@"; do
        npm install ${nodepkg}@latest --loglevel silent --prefix $NODE_BASE
    done
}

# Install rclone
# @Provides: rclone
# @Depends: python
function rclone_install() {
    python_base
    local RCLONE_FILE="$ENV_PATH/rclone/rclone-latest.zip"
    local RCLONE_URL="https://downloads.rclone.org/rclone-current-linux-amd64.zip"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        RCLONE_URL="https://downloads.rclone.org/rclone-current-osx-amd64.zip"
    fi
    log "Installing httpie to download requirements"
    $ENV_PATH/bin/pip install -q --upgrade httpie
    $ENV_PATH/bin/pip install -q --upgrade requests[security]
    mkdir -p $ENV_PATH/rclone
    $ENV_PATH/bin/http --download --verify=no --output "$RCLONE_FILE" "$RCLONE_URL"
    $ENV_PATH/bin/python -m zipfile -e "$RCLONE_FILE" "$ENV_PATH/rclone"
    RCLONE_EXE="$(find "$ENV_PATH/rclone" -mindepth 1 -maxdepth 1 -type 'd')/rclone"
    log "RClone downloaded [$RCLONE_EXE]"
    mv "$RCLONE_EXE" $ENV_PATH/bin/rclone
    chmod +x "$ENV_PATH/bin/rclone"
}

# Shell configuration
# @Provides: shell
function shell_eval() {
    for dep in "$@"; do
        DEP_LOCATION="$(which $dep)"
        if [ -z "$DEP_LOCATION" ]; then
            echo "Dependency [$dep] unable to fulfill. Exiting."
            exit 1
        fi
        DEP_NAME=$(echo "$dep" | tr '[:lower:]' '[:upper:]')
        export $DEP_NAME="$DEP_LOCATION"
    done
}

function shell_install() {
    env_install
    log "Boostraping shell dependencies"
    shell_eval $@
}

function install_dependencies() {
    EXECUTABLE_NAME="$(basename $0)"
    DEPENDENCIES_LINE="$(grep "^${EXECUTABLE_NAME}:" "$DEPENDENCIES_FILE" | head -n 1)"
    FRAMEWORK="$(echo "$DEPENDENCIES_LINE" | cut -d ' ' -f 2)"
    FRAMEWORK_DEPENDENCIES="$(echo "$DEPENDENCIES_LINE" | cut -d ' ' -f 3-)"
    export ENV_PATH
    if [ ! -f "$ENV_PATH/$EXECUTABLE_NAME.installed" ]; then
        ${FRAMEWORK}_install $FRAMEWORK_DEPENDENCIES
        touch "$ENV_PATH/$EXECUTABLE_NAME.installed"
    else 
        if [ -n "$(type -t ${FRAMEWORK}_eval)" ] && [ "$(type -t ${FRAMEWORK}_eval)" = function ]; then
            ${FRAMEWORK}_eval $FRAMEWORK_DEPENDENCIES
        fi
    fi
}

install_dependencies
