#!/usr/bin/env python3
"""Script-server wrapper to trigger upcoming-episodes sync."""
import requests
import sys
import json

import socket

# Try to get host gateway IP, fallback to localhost
try:
    gateway = socket.gethostbyname('gateway.docker.internal')
    SERVICE_URL = f"http://{gateway}:8001"
except:
    SERVICE_URL = "http://172.17.0.1:8001"  # Default Docker bridge gateway

try:
    # Call the /sync endpoint
    response = requests.post(f"{SERVICE_URL}/sync", timeout=30)
    response.raise_for_status()

    # Parse and display results
    data = response.json()
    print(f"✓ Sync completed successfully")
    print(f"  Episodes updated: {data.get('episodes_updated', 0)}")
    print(f"  Series updated: {data.get('series_updated', 0)}")
    print(f"  Seasons updated: {data.get('seasons_updated', 0)}")
    sys.exit(0)

except requests.exceptions.ConnectionError:
    print("✗ Error: upcoming-episodes service not running", file=sys.stderr)
    print("  Start with: systemctl start upcoming-episodes", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}", file=sys.stderr)
    sys.exit(1)
