#!/bin/sh

cp -f ./scripts/pre-commit ./.git/hooks/pre-commit
cp -f ./config/dev_pyproject.toml ./pyproject.toml
