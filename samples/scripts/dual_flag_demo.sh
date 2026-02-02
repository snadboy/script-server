#!/bin/bash

echo "=== Dual Flag Boolean Test ==="
echo ""
echo "Command line arguments received:"
echo "$@"
echo ""

# Parse all arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --verbose)
      echo "✓ Verbose mode enabled"
      shift
      ;;
    --quiet)
      echo "✓ Quiet mode enabled"
      shift
      ;;
    --enable-cache)
      echo "✓ Cache enabled"
      shift
      ;;
    --disable-cache)
      echo "✓ Cache disabled"
      shift
      ;;
    --color)
      echo "✓ Colors enabled"
      shift
      ;;
    --no-color)
      echo "✓ Colors disabled"
      shift
      ;;
    --enabled)
      echo "✓ Regular bool enabled with value: $2"
      shift 2
      ;;
    *)
      echo "? Unknown argument: $1"
      shift
      ;;
  esac
done

echo ""
echo "Test complete!"
