#!/usr/bin/env python3
"""
Gmail Trim Demo Script - For testing project-level parameters and verbs.

This is a simplified demo script that mimics the structure of the actual
gmail-cleanup CLI but just prints what it would do.
"""

import sys
import argparse


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Gmail Trim Demo")

    # Subcommands (verbs)
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Run command
    run_parser = subparsers.add_parser('run', help='Run cleanup')
    run_parser.add_argument('-d', '--days', type=int, default=30, help='Days to keep')
    run_parser.add_argument('--dry-run', action='store_true', help='Preview mode')
    run_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')
    run_parser.add_argument('-c', '--config', help='Config file path')

    # Auth command
    auth_parser = subparsers.add_parser('auth', help='Authenticate')
    auth_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')

    # Labels command
    labels_parser = subparsers.add_parser('labels', help='List labels')
    labels_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')

    # Groups command
    groups_parser = subparsers.add_parser('groups', help='List contact groups')
    groups_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')

    # Config command
    config_parser = subparsers.add_parser('config', help='Show config')
    config_parser.add_argument('-c', '--config', help='Config file path')
    config_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')

    args = parser.parse_args()

    # Execute command
    if args.command == 'run':
        print(f"[DEMO] Running cleanup with:")
        print(f"  Days: {args.days}")
        print(f"  Dry run: {args.dry_run}")
        print(f"  Verbose: {args.verbose}")
        if args.config:
            print(f"  Config: {args.config}")

    elif args.command == 'auth':
        print(f"[DEMO] Authenticating...")
        print(f"  Verbose: {args.verbose}")

    elif args.command == 'labels':
        print(f"[DEMO] Listing labels...")
        print(f"  Verbose: {args.verbose}")
        print("  - Inbox")
        print("  - KEEP")
        print("  - Work")

    elif args.command == 'groups':
        print(f"[DEMO] Listing contact groups...")
        print(f"  Verbose: {args.verbose}")
        print("  - Family")
        print("  - Friends")
        print("  - Coworkers")

    elif args.command == 'config':
        print(f"[DEMO] Showing configuration...")
        print(f"  Verbose: {args.verbose}")
        if args.config:
            print(f"  Config file: {args.config}")

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
