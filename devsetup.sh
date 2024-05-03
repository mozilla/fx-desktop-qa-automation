#!/bin/sh

cp -f pre-commit ./.git/hooks/pre-commit
cp -f ./dev_pyproject.toml ./pyproject.toml
