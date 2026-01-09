#!/usr/bin/env python3
"""
Long running test script for testing execute/stop button behavior.
Runs for approximately 30 seconds with progress output.
"""

import sys
import time

def main():
    duration = 30
    print(f"Starting long-running task ({duration} seconds)...")
    print("-" * 40)

    for i in range(duration):
        progress = (i + 1) / duration * 100
        bar_length = 30
        filled = int(bar_length * (i + 1) / duration)
        bar = "=" * filled + "-" * (bar_length - filled)

        print(f"[{bar}] {progress:5.1f}% - {i + 1}/{duration}s elapsed")
        sys.stdout.flush()
        time.sleep(1)

    print("-" * 40)
    print("Task completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
