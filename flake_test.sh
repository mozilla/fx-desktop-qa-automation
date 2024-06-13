#!/bin/bash

# usage: ./flake_test.sh path/to/tests 30
# This would run the tests 30 times and track results in ./results.txt.

echo "" > results.txt
for i in $(seq 1 "$2"); do
    echo -n "Test run number ${i}..."
    if pytest --run-headless -n 5 "$1" >> err_log.txt 2>&1; then
        echo "pass"
        echo "$i: pass" >> results.txt
    else
        echo "fail"
        echo "$i: fail" >> results.txt
    fi
done
