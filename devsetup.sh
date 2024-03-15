#!/bin/sh

./post-checkout
cp -f post-merge ./.git/hooks/post-commit
