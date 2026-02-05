#!/usr/bin/env python3
"""
Auto-generated wrapper script for Fetch Quotes.

This script runs the project using the script-server common venv.
Required packages: requests
"""

import sys
import os

# Add project source to Python path
PROJECT_SRC_PATH = '/home/snadboy/projects/script-server/src/projects/fetch-quotes'
sys.path.insert(0, PROJECT_SRC_PATH)

# Change to project directory for config/token files
os.chdir('/home/snadboy/projects/script-server/src/projects/fetch-quotes')



# Import and run the CLI app
from main import main

if __name__ == '__main__':
    main()
