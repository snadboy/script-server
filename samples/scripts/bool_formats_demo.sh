#!/bin/bash

echo "=== Boolean Format Test ==="
echo ""
echo "Command line arguments received:"
echo "$@"
echo ""

# Parse all arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --separate)
      echo "✓ Separate format: --separate $2"
      shift 2
      ;;
    --combined=*)
      echo "✓ Combined format: $1"
      shift
      ;;
    --combined)
      echo "✓ Separate format (fallback): --combined $2"
      shift 2
      ;;
    --verbose)
      echo "✓ Dual flags: --verbose (true)"
      shift
      ;;
    --quiet)
      echo "✓ Dual flags: --quiet (false)"
      shift
      ;;
    *)
      echo "? Unknown argument: $1"
      shift
      ;;
  esac
done

echo ""
echo "Test complete!"
