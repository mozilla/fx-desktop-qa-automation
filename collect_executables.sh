#!/bin/bash
echo "~~collect executables~~"

# Usage: ./collect_executables.sh [channel]
# Collects geckodriver and Fx, default channel is Beta.

## Determine OS and arch
UNAME_A=$(uname -a)
## Save the system arch info
if [ -n "$COLLECT_LANG" ]
then
    COLLECT_LANG=en-US
fi
echo "uname -a: ${UNAME_A}"
if [ -n "$WSL_DISTRO_NAME" ] || [[ $UNAME_A == *"MINGW"* ]]
then
    SYSTEM_NAME="win"
    if [[ $UNAME_A == *"x86_64"* ]]
    then
        BITS="64"
    else
        BITS="32"
    fi
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

if [[ $SYSTEM_NAME == "win" ]]
then
    EXT="zip"
else
    EXT="tar.gz"
fi

# Find the version of Geckodriver that matches arch
FILENAME="-${SYSTEM_NAME}${BITS}${ARCH}.${EXT}"
echo "FILENAME ${FILENAME}"
# 20 is arbitrary and may break if future releases of Geckodriver have more than 20 channels
for i in {0..20}
do
    GECKO_LINK=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | jq ".[\"assets\"][${i}][\"browser_download_url\"]" | tr -d '"')
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
FX_LINK_HTML=$(curl -s https://download.mozilla.org/\?product\=firefox${CHANNEL}-latest-ssl\&os\=${FX_SYS_NAME}\&lang\=${COLLECT_LANG})
FX_LOC=$(echo "$FX_LINK_HTML" | awk -F '"' '{print $2}')

curl -O "$FX_LOC"

GD_FILE=$(ls geckodriver*)
mv "$GD_FILE" "geckodriver.${EXT}"
if [[ $EXT == "zip" ]]
then
    unzip geckodriver.zip
else
    tar -xvzf geckodriver.tar.gz
fi

# Wait up to 10 seconds for geckodriver to exist
for ((i=0; i<200; i++))
do
    if [ -f geckodriver ]
    then
        break
    fi
    sleep 0.2
done
chmod +x geckodriver
./geckodriver --version

if [[ $SYSTEM_NAME == "linux" ]]
then
    ls firefox*.tar.bz2
    mv firefox*.tar.bz2 firefox.tar.bz2
    tar -xvjf firefox.tar.bz2
    echo "./firefox/firefox" > fx_location
else
    if [[ $SYSTEM_NAME == "win" ]]
    then
        mv Firefox*.exe setup.exe
    else
        if [[ $SYSTEM_NAME == "macos" ]]
        then
            VOLUME=$(hdiutil attach Firefox*.dmg | grep -Eo '/Volumes/Firefox.*$')
            echo "$VOLUME/Firefox.app/Contents/MacOS/firefox" > fx_location
        fi
    fi
fi
