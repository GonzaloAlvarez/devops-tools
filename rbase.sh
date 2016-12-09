#!/bin/bash
BASE_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $BASE_PATH/base.sh
export GEM_HOME="$ENV_PATH/gems"
export GEM_PATH=""
if [ ! -d $GEM_HOME ]; then
    mkdir -p "$GEM_HOME"
    while read rubygem; do
        gem install $rubygem
    done < ruby.packages
fi
