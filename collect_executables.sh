#!/bin/bash

UNAME_A=$(uname -a)

if [[ "$UNAME_A" == *"Darwin"* ]]
then
    curl -o Firefox.dmg -L "$(./collect_executables.py)"
else
    curl -o firefox.tar.bz2 -L "$(./collect_executables.py)"
    tar -xvjf firefox.tar.bz2
fi
curl -o geckodriver.tar.gz -L "$(./collect_executables.py -g)"
tar -xvzf geckodriver.tar.gz
