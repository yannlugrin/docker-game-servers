# The rule-2 harness. Everything is pre-commit and pytest; nothing here is
# bespoke tooling.
SHELL := /bin/bash
VENV := .venv/bin
.DEFAULT_GOAL := help

.PHONY: help setup check test verify

help:
	@echo "make setup   create .venv from requirements.txt, install the git hook"
	@echo "make check   run every linter over the tree, untracked files included"
	@echo "make test    behavior tests — none yet; they arrive with the images"
	@echo "make verify  check + test"

setup:
	@python3 -m venv .venv
	@$(VENV)/pip install --quiet --disable-pip-version-check -r requirements.txt
	@$(VENV)/pre-commit install
	@echo "ready — run: make verify"

# --files rather than --all-files: pre-commit's --all-files reads the index,
# which would skip a file that exists but has never been added.
check:
	@$(VENV)/pre-commit run --files $$(git ls-files --cached --others --exclude-standard)

# Nothing to test yet: this repository ships no behavior of its own. The
# first tests are the image smoke tests (root spec 8).
test:
	@echo "no behavior tests yet — they arrive with the first image"

verify: check test
