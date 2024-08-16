#!/bin/bash

UNAME_A=$(uname -a)

if [[ "$UNAME_A" == *"Darwin"* ]]
then
    curl -o Firefox.dmg -L "$(pipenv run python collect_executables.py)"
    hdiutil attach Firefox.dmg
else
    curl -o firefox.tar.bz2 -L "$(pipenv run python collect_executables.py)"
    tar -xvjf firefox.tar.bz2
fi
curl -o geckodriver.tar.gz -L "$(pipenv run python collect_executables.py -g)"
tar -xvzf geckodriver.tar.gz
