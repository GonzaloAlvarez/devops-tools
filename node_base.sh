#!/bin/bash
BASE_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $BASE_PATH/base.sh
NODE_BASE="$ENV_PATH/lib"
NODE_PACKAGES="$BASE_PATH/node.packages"
if [ ! -x $ENV_PATH/bin/node ]; then
    $ENV_PATH/bin/pip install nodeenv
    $ENV_PATH/bin/nodeenv -p
fi
source $ENV_PATH/bin/activate
if [ $(ls -1 "$NODE_BASE/node_modules" | wc -l) -le 1 ]; then
    if [ -r "$NODE_PACKAGES" ]; then
        while read nodepkg; do
            npm install ${nodepkg}@latest --prefix $NODE_BASE
        done < $NODE_PACKAGES
    fi
fi
