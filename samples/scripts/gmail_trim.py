#!/usr/bin/env python3
"""Script-server wrapper for gmail-trim CLI."""
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path("/opt/gmail-trim")

# Run gmail-cleanup command with arguments
result = subprocess.run(
    [sys.executable, "-m", "gmail_cleanup.main"] + sys.argv[1:],
    cwd=PROJECT_DIR
)
sys.exit(result.returncode)
