#!/bin/bash

echo "" > results
for i in $(seq 1 "$2"); do
    if pytest --run-headless -n 5 "$1"; then
        echo "$i: pass" >> results
    else
        echo "$i: fail" >> results
    fi
done
