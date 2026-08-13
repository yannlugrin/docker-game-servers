# Fixture: unused import and undefined name — must fail ruff.
import os


def broken():
    return undefined_name
