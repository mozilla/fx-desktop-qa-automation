#!/bin/bash

STARFOX_SPLIT=nightly-as-beta python3 -m scripts.choose_test_split
git checkout main tests
git checkout main modules
git checkout main .github/workflows/main.yml
python3 scripts/smoke_to_nightly.py
git checkout main manifests
python3 -m scripts.reset_manifest nightly-as-beta
