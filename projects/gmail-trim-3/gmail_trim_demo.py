#!/usr/bin/env python3
"""
Demo Gmail Trim script for testing verb and parameter configuration.

This is a mock script that doesn't actually connect to Gmail - it just
demonstrates the command-line argument construction.
"""

import sys
import argparse


def main():
    print("Gmail Trim Demo Script")
    print("=" * 60)
    print(f"Command: {' '.join(sys.argv)}")
    print("=" * 60)

    # Show what command was called
    if len(sys.argv) > 1:
        command = sys.argv[1]
        print(f"\n✓ Verb/Command: {command}")

    # Parse remaining args
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='Command to run')
    parser.add_argument('-d', '--days', type=int, help='Days to keep')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose')
    parser.add_argument('-c', '--config-file', help='Config file path')

    try:
        args = parser.parse_args()
        print(f"\n✓ Parsed arguments:")
        for key, value in vars(args).items():
            if value is not None:
                print(f"  {key}: {value}")
    except SystemExit:
        print("\n✗ Failed to parse arguments")

    print("\n" + "=" * 60)
    print("Demo completed successfully!")


if __name__ == '__main__':
    main()
