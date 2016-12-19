#!/bin/bash
BASE_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $BASE_PATH/base.sh
export GEM_HOME="$ENV_PATH/gems"
export GEM_PATH=""
RUBY_PACKAGES="$BASE_PATH/ruby.packages"
if [ ! -d $GEM_HOME ]; then
    mkdir -p "$GEM_HOME"
    if [ -r "$RUBY_PACKAGES" ]; then
        while read rubygem; do
            gem install $rubygem
        done < "$RUBY_PACKAGES"
    fi
fi
