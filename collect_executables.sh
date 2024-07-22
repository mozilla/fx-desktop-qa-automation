#!/bin/bash
echo "~~collect executables~~"

# Usage: ./collect_executables.sh [channel]
# Collects geckodriver and Fx, default channel is Beta.

## Determine OS and arch
UNAME_A=$(uname -a)
echo "uname -a: ${UNAME_A}"
if [ -n "$WSL_DISTRO_NAME" ]
then
    SYSTEM_NAME="win"
else
    if [[ $UNAME_A == *"Darwin"* ]]
    then
        SYSTEM_NAME="macos"
    else
        SYSTEM_NAME="linux"
    fi
fi

if [[ $UNAME_A == *"arm64"* ]]
then
    ARCH="-aarch64"
else
    if [[ $SYSTEM_NAME == "linux" ]] && [[ $UNAME_A == *"i386"* ]]
    then
        BITS="32"
    else
        BITS="64"
    fi
fi

if [[ "$SYSTEM_NAME" == "win" ]] && [[ -z $ARCH ]] && [[ $BITS = "64" ]]
then
    BITS=32
fi

if [[ $SYSTEM_NAME == "win" ]]
then
    EXT="zip"
else
    EXT="tar.gz"
fi

# Find the version of Geckodriver that matches arch
FILENAME="-${SYSTEM_NAME}${BITS}${ARCH}.${EXT}"
# 20 is arbitrary and may break if future releases of Geckodriver have more than 20 channels
for i in {0..20}
do
    GECKO_LINK=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | jq ".[\"assets\"][${i}][\"browser_download_url\"]" | tr -d '"')
    echo "$GECKO_LINK"
    if [[ $GECKO_LINK == *"${FILENAME}"* ]] && [[ $GECKO_LINK != *".asc" ]]
    then
        curl -OL "$GECKO_LINK"
    fi
done

# Determine the Fx channel and arch
if [[ $SYSTEM_NAME == "macos" ]]
then
    FX_SYS_NAME="osx"
else
    if [[ $SYSTEM_NAME == "linux" ]] && [[ $BITS == "64" ]]
    then
        FX_SYS_NAME="linux64"
    else
        FX_SYS_NAME=$"$SYSTEM_NAME"
    fi
fi

CHANNEL="-beta"
if [[ $1 == *"ightly"* ]]
then
    CHANNEL="-nightly"
else
    if [[ $1 == *"rod"* ]] || [[ $1 == *"elease"* ]]
    then
        CHANNEL=""
    fi
fi
FX_LINK_HTML=$(curl -s https://download.mozilla.org/\?product\=firefox${CHANNEL}-latest-ssl\&os\=${FX_SYS_NAME}\&lang\=en-US)
FX_LOC=$(echo "$FX_LINK_HTML" | awk -F '"' '{print $2}')

curl -O "$FX_LOC"

mv geckodriver*.tar.gz geckodriver.tar.gz
tar -xvzf geckodriver.tar.gz
chmod +x geckodriver

if [[ $SYSTEM_NAME == "linux" ]]
then
    ls firefox*.tar.bz2
    mv firefox*.tar.bz2 firefox.tar.bz2
    tar -xvjf firefox.tar.bz2
fi
