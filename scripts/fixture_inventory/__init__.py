"""
Read-only inventory of pytest fixtures, hooks and dependencies in a test repo.

Run from the repo root with ``python -m scripts.fixture_inventory --help``.
Source files are parsed with ``ast`` and never imported or executed.
"""

__version__ = "0.1.0"
