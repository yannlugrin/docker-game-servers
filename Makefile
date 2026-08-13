# Harness entry points (CLAUDE.md rule 2). One setup command, then:
#   check  — the working tree is well-formed
#   test   — harness behavior against fixtures, must-fail and must-warn cases
#   verify — both
SHELL := /bin/bash
.DEFAULT_GOAL := help

.PHONY: help setup check test verify

help:
	@echo "make setup   install pinned harness tools and the git hooks path"
	@echo "make check   check the working tree (ONLY=family[,family] narrows it)"
	@echo "make test    run the harness behavior tests"
	@echo "make verify  check + test"
	@echo ""
	@echo "families:    $$(tools/check.sh --list | tr '\n' ' ')"

setup:
	@tools/setup.sh $(SETUP_ARGS)

check:
	@tools/check.sh $(if $(ONLY),--only $(ONLY))

test:
	@tools/test.sh

verify: check test
