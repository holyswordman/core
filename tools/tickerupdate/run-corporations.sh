#!/usr/bin/env bash

if [[ -z "$CORE_HOME" ]];
then
    echo "You need to set CORE_HOME first."
    exit 1
fi

cat update-corporations.py | ../../bin/core-shell



