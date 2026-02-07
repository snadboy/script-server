#!/usr/bin/env python3
"""Helper script to create connection instances."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__) + '/src')

from connections.connection_service import ConnectionService
from connections import encryption

# Initialize encryption
encryption.init_encryption('conf/.connection_key')

# Initialize connection service
conn_service = ConnectionService('conf/connections')

# Connection definitions
connections = [
    {
        'id': 'production-sonarr',
        'name': 'Production Sonarr',
        'type': 'sonarr',
        'fields': {
            'url': 'https://sonarr.isnadboy.com',
            'api_key': '36261001e1ac41d185b42028228b8f09'
        }
    },
    {
        'id': 'production-radarr',
        'name': 'Production Radarr',
        'type': 'radarr',
        'fields': {
            'url': 'https://radarr.isnadboy.com',
            'api_key': '681c54f9962e42a8b6aa5082c074b939'
        }
    },
    {
        'id': 'production-plex',
        'name': 'Production Plex',
        'type': 'plex',
        'fields': {
            'url': 'https://plex.isnadboy.com',
            'token': '05f660f70f3e23a0445997d159ad109ffb325bd2'
        }
    },
    {
        'id': 'production-sabnzbd',
        'name': 'Production SABnzbd',
        'type': 'sabnzbd',
        'fields': {
            'url': 'https://sabnzbd.isnadboy.com',
            'api_key': '08c4abc526b548ab93b00862c7e46384'
        }
    }
]

# Create each connection
for conn_def in connections:
    try:
        print(f"Creating connection: {conn_def['id']} ({conn_def['name']})...")
        conn_service.create_connection(conn_def)
        print(f"✓ Created {conn_def['id']}")
    except Exception as e:
        print(f"✗ Error creating {conn_def['id']}: {e}")

print("\nDone! Created connections:")
for conn in conn_service.list_connections():
    if conn['id'].startswith('production-'):
        print(f"  - {conn['id']}: {conn['name']} ({conn['type']})")
