#!/bin/bash

# usage: ./flake_test.sh path/to/tests 30
# This would run the tests 30 times and track results in ./results.

echo "" > results
for i in $(seq 1 "$2"); do
    if pytest --run-headless -n 5 "$1"; then
        echo "$i: pass" >> results
    else
        echo "$i: fail" >> results
    fi
done
