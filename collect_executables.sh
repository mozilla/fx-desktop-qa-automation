#!/bin/bash

UNAME_A=$(uname -a)

if [[ "$UNAME_A" == *"Darwin"* ]]
then
    if [ -n "$MANUAL_DOWNLOAD_LINK" ]
    then
        curl -o Firefox.dmg -L "${MANUAL_DOWNLOAD_LINK}"
    else
        curl -o Firefox.dmg -L "$(pipenv run python collect_executables.py)"
    fi
    hdiutil attach Firefox.dmg
else
    if [ -n "$MANUAL_DOWNLOAD_LINK" ]
    then
        curl -o firefox.tar.xz -L "${MANUAL_DOWNLOAD_LINK}"
    else
        pipenv run python collect_executables.py
        curl -o firefox.tar.xz -L "$(pipenv run python collect_executables.py)"
    fi
    tar xf firefox.tar.xz
fi
curl -o geckodriver.tar.gz -L "$(pipenv run python collect_executables.py -g)"
gunzip -c geckodriver.tar.gz | tar xopf -
