#!/bin/bash

while read -r line; do
    if [[ "${line}" == *"/Volumes/"* ]]; then
        echo "${line}" | cut -f 3 | cut -d"/" -f 3
    fi
done <<< "$1"
