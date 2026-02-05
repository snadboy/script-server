#!/usr/bin/env python3
"""
Auto-generated wrapper script for Gmail Trim.

This script runs the project using the script-server common venv.
Required packages: google-api-python-client, requests, google-auth-oauthlib, pydantic, pyyaml, google-auth, pydantic-settings, typer, structlog
"""

import sys
import os

# Add project source to Python path
PROJECT_SRC_PATH = '/home/snadboy/projects/script-server/projects/gmail-trim-3/src'
sys.path.insert(0, PROJECT_SRC_PATH)

# Change to project directory for config/token files
os.chdir('/home/snadboy/projects/script-server/projects/gmail-trim-3')



# Import and run the CLI app
from gmail_cleanup.main import app

if __name__ == '__main__':
    app()
