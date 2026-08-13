#!/usr/bin/env bash
# Fixture: syntactically valid, unsafe — must fail shellcheck (SC2086).
target=$1
rm -rf $target
