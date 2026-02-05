#!/usr/bin/env python3
"""
Auto-generated wrapper script for Gmail Trim.

This script runs the project using the script-server common venv.
Required packages: 
"""

import sys
import os

# Add project source to Python path
PROJECT_SRC_PATH = '/home/snadboy/projects/script-server/projects/gmail-trim-3'
sys.path.insert(0, PROJECT_SRC_PATH)

# Change to project directory for config/token files
os.chdir('/home/snadboy/projects/script-server/projects/gmail-trim-3')



# Import and run the CLI app
from gmail_trim_demo import main

if __name__ == '__main__':
    main()
