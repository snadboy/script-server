#!/usr/bin/env python3
"""
Gmail Auto-Cleanup wrapper script for script-server.

This script runs the gmail-cleanup tool using the common venv.
Requires: google-api-python-client, google-auth-oauthlib, google-auth,
          pydantic, pydantic-settings, structlog, typer, pyyaml
"""

import sys
import os

# Add gm source to path
GM_PROJECT_PATH = '/home/snadboy/projects/gm/src'
GM_CONFIG_PATH = '/home/snadboy/projects/gm/config/config.yaml'
sys.path.insert(0, GM_PROJECT_PATH)

# Change to gm project directory for config/token files
os.chdir('/home/snadboy/projects/gm')

# Inject --config if running 'run' command and not already specified
if len(sys.argv) >= 2 and sys.argv[1] == 'run' and '--config' not in sys.argv:
    sys.argv.insert(2, '--config')
    sys.argv.insert(3, GM_CONFIG_PATH)

# Import and run the typer app
from gmail_cleanup.main import app

if __name__ == '__main__':
    app()
