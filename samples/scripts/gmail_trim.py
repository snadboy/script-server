#!/usr/bin/env python3
"""Script-server wrapper for gmail-trim CLI."""
import subprocess
import sys
import os
from pathlib import Path

PROJECT_DIR = Path("/opt/gmail-trim")
CLI_SCRIPT = PROJECT_DIR / ".venv" / "bin" / "gmail-cleanup"

# Set PYTHONPATH to include the installed package
env = os.environ.copy()
env["PYTHONPATH"] = str(PROJECT_DIR / ".venv" / "lib" / "python3.12" / "site-packages")

# Run gmail-cleanup CLI script directly
result = subprocess.run(
    ["/usr/local/bin/python3", str(CLI_SCRIPT)] + sys.argv[1:],
    cwd=PROJECT_DIR,
    env=env
)
sys.exit(result.returncode)
