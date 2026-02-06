#!/bin/bash
# Test script to verify connection credential injection

echo "=== Connection Credentials Test ==="
echo ""

# Check for Plex credentials
if [ -n "$PLEX_URL" ]; then
    echo "✓ PLEX_URL: $PLEX_URL"
fi

if [ -n "$PLEX_TOKEN" ]; then
    echo "✓ PLEX_TOKEN: ${PLEX_TOKEN:0:10}... (masked)"
fi

# Check for Sonarr credentials
if [ -n "$SONARR_URL" ]; then
    echo "✓ SONARR_URL: $SONARR_URL"
fi

if [ -n "$SONARR_API_KEY" ]; then
    echo "✓ SONARR_API_KEY: ${SONARR_API_KEY:0:10}... (masked)"
fi

# Check for Radarr credentials
if [ -n "$RADARR_URL" ]; then
    echo "✓ RADARR_URL: $RADARR_URL"
fi

if [ -n "$RADARR_API_KEY" ]; then
    echo "✓ RADARR_API_KEY: ${RADARR_API_KEY:0:10}... (masked)"
fi

# Check for Home Assistant credentials
if [ -n "$HOME_ASSISTANT_URL" ]; then
    echo "✓ HOME_ASSISTANT_URL: $HOME_ASSISTANT_URL"
fi

if [ -n "$HOME_ASSISTANT_TOKEN" ]; then
    echo "✓ HOME_ASSISTANT_TOKEN: ${HOME_ASSISTANT_TOKEN:0:10}... (masked)"
fi

# Check for Generic credentials
if [ -n "$GENERIC_URL" ]; then
    echo "✓ GENERIC_URL: $GENERIC_URL"
fi

if [ -n "$GENERIC_USERNAME" ]; then
    echo "✓ GENERIC_USERNAME: $GENERIC_USERNAME"
fi

echo ""
echo "=== Test Complete ==="
