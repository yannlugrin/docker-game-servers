#!/usr/bin/env bash
# Fixture: unbalanced `if` — must fail `bash -n`.
if [ -n "$1" ]; then
  echo "missing fi"
