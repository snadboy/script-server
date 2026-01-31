#!/usr/bin/env python3
"""
Gmail Auto-Cleanup wrapper script for script-server.

This script runs the gmail-cleanup CLI tool installed in the common venv.
The gmail-auto-cleanup package must be installed via:
  pip install -e /home/snadboy/projects/gmail-trim
"""

import sys
from gmail_cleanup.main import app

if __name__ == '__main__':
    app()
