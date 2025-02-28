#!/bin/bash

UNAME_A=$(uname -a)

if [[ "$UNAME_A" == *"Darwin"* ]]
then
    curl -o Firefox.dmg -L "$(pipenv run python collect_executables.py)"
    hdiutil attach Firefox.dmg
else
    pipenv run python collect_executables.py
    curl -o firefox.tar.xz -L "$(pipenv run python collect_executables.py)"
    tar xf firefox.tar.xz
fi
curl -o geckodriver.tar.gz -L "$(pipenv run python collect_executables.py -g)"
tar -xvzf geckodriver.tar.gz
