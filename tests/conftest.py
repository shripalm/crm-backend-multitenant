"""Pytest configuration helpers.

Ensure the project root is on sys.path so tests can import the application package
when pytest is invoked from the project workspace.
"""
from __future__ import annotations

import sys
from pathlib import Path
import os


def _add_project_root_to_path() -> None:
    root = Path(__file__).resolve().parent.parent
    p = str(root)
    if p not in sys.path:
        # Insert at front so local packages take precedence over installed ones
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

_add_project_root_to_path()
