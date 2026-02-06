"""
Connection management service.

Provides CRUD operations, file-based storage, and resolution logic for
connection instances.
"""

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .connection_types import get_connection_type, ConnectionType
from .encryption import get_encryption_service

LOGGER = logging.getLogger('script_server.connections.service')


class ConnectionService:
    """Service for managing connection instances."""

    def __init__(self, connections_dir: str):
        """
        Initialize connection service.

        Args:
            connections_dir: Directory for connection storage (typically conf/connections/)
        """
        self.connections_dir = Path(connections_dir)
        self.connections_dir.mkdir(parents=True, exist_ok=True)
        LOGGER.info(f"Connection service initialized with storage: {self.connections_dir}")

    def _get_connection_file_path(self, connection_id: str) -> Path:
        """Get the file path for a connection ID."""
        # Sanitize ID to prevent directory traversal
        safe_id = re.sub(r'[^a-zA-Z0-9_-]', '_', connection_id)
        return self.connections_dir / f"{safe_id}.json"

    def _load_connection_file(self, connection_id: str) -> Optional[Dict]:
        """Load a connection from its JSON file."""
        file_path = self._get_connection_file_path(connection_id)
        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            LOGGER.error(f"Failed to load connection {connection_id}: {e}")
            return None

    def _save_connection_file(self, connection_id: str, data: Dict):
        """Save a connection to its JSON file."""
        file_path = self._get_connection_file_path(connection_id)

        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            LOGGER.info(f"Saved connection {connection_id} to {file_path}")
        except Exception as e:
            LOGGER.error(f"Failed to save connection {connection_id}: {e}")
            raise

    def _delete_connection_file(self, connection_id: str):
        """Delete a connection's JSON file."""
        file_path = self._get_connection_file_path(connection_id)
        if file_path.exists():
            file_path.unlink()
            LOGGER.info(f"Deleted connection file {file_path}")

    def list_connections(self, include_deleted: bool = False) -> List[Dict]:
        """
        List all connections.

        Args:
            include_deleted: Whether to include soft-deleted connections

        Returns:
            List of connection metadata (secrets masked)
        """
        connections = []

        for file_path in self.connections_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                # Skip deleted connections unless requested
                if data.get('deleted', False) and not include_deleted:
                    continue

                # Mask secrets before returning
                connections.append(self._mask_secrets(data))
            except Exception as e:
                LOGGER.error(f"Failed to load connection from {file_path}: {e}")

        # Sort by name
        connections.sort(key=lambda c: c.get('name', '').lower())
        return connections

    def get_connection(self, connection_id: str, mask_secrets: bool = True) -> Optional[Dict]:
        """
        Get a connection by ID.

        Args:
            connection_id: Connection identifier
            mask_secrets: Whether to mask secret fields (default True)

        Returns:
            Connection data or None if not found
        """
        data = self._load_connection_file(connection_id)
        if not data:
            return None

        if mask_secrets:
            return self._mask_secrets(data)
        return data

    def create_connection(self, connection_data: Dict) -> Dict:
        """
        Create a new connection.

        Args:
            connection_data: Connection fields including id, type, name, fields

        Returns:
            Created connection (secrets masked)

        Raises:
            ValueError: If validation fails or connection already exists
        """
        connection_id = connection_data.get('id')
        if not connection_id:
            raise ValueError("Connection ID is required")

        conn_type_id = connection_data.get('type')
        if not conn_type_id:
            raise ValueError("Connection type is required")

        conn_type = get_connection_type(conn_type_id)
        if not conn_type:
            raise ValueError(f"Unknown connection type: {conn_type_id}")

        # Check if already exists
        if self._load_connection_file(connection_id):
            raise ValueError(f"Connection {connection_id} already exists")

        # Validate and encrypt fields
        validated_fields = self._validate_and_encrypt_fields(
            connection_data.get('fields', {}),
            conn_type
        )

        # Build connection document
        now = datetime.utcnow().isoformat() + 'Z'
        connection_doc = {
            'id': connection_id,
            'type': conn_type_id,
            'name': connection_data.get('name', connection_id),
            'created_at': now,
            'updated_at': now,
            'fields': validated_fields,
            'deleted': False
        }

        # Save to file
        self._save_connection_file(connection_id, connection_doc)

        LOGGER.info(f"Created connection: {connection_id} (type: {conn_type_id})")
        return self._mask_secrets(connection_doc)

    def update_connection(self, connection_id: str, updates: Dict) -> Dict:
        """
        Update an existing connection.

        Args:
            connection_id: Connection identifier
            updates: Fields to update (name, fields)

        Returns:
            Updated connection (secrets masked)

        Raises:
            ValueError: If connection not found or validation fails
        """
        existing = self._load_connection_file(connection_id)
        if not existing:
            raise ValueError(f"Connection {connection_id} not found")

        conn_type = get_connection_type(existing['type'])
        if not conn_type:
            raise ValueError(f"Unknown connection type: {existing['type']}")

        # Update name if provided
        if 'name' in updates:
            existing['name'] = updates['name']

        # Update fields if provided
        if 'fields' in updates:
            # Merge with existing fields (allows partial updates)
            current_fields = existing.get('fields', {})
            updated_fields = updates['fields']

            # For secret fields, if value is "********" (masked), keep existing value
            encryption = get_encryption_service()
            for field_name, field_value in updated_fields.items():
                if field_value == "********":
                    # Keep existing encrypted value
                    continue
                current_fields[field_name] = field_value

            # Validate and encrypt
            existing['fields'] = self._validate_and_encrypt_fields(current_fields, conn_type)

        # Update timestamp
        existing['updated_at'] = datetime.utcnow().isoformat() + 'Z'

        # Save
        self._save_connection_file(connection_id, existing)

        LOGGER.info(f"Updated connection: {connection_id}")
        return self._mask_secrets(existing)

    def delete_connection(self, connection_id: str, soft_delete: bool = True) -> bool:
        """
        Delete a connection.

        Args:
            connection_id: Connection identifier
            soft_delete: If True, mark as deleted but keep file; if False, remove file

        Returns:
            True if deleted, False if not found
        """
        existing = self._load_connection_file(connection_id)
        if not existing:
            return False

        if soft_delete:
            # Mark as deleted
            existing['deleted'] = True
            existing['deleted_at'] = datetime.utcnow().isoformat() + 'Z'
            self._save_connection_file(connection_id, existing)
            LOGGER.info(f"Soft-deleted connection: {connection_id}")
        else:
            # Permanently delete file
            self._delete_connection_file(connection_id)
            LOGGER.info(f"Permanently deleted connection: {connection_id}")

        return True

    def resolve_connection(self, declaration: Dict) -> Optional[Dict]:
        """
        Resolve a connection declaration to a connection instance.

        Args:
            declaration: Connection declaration with 'type' and optional 'id'
                         e.g., {"type": "google", "id": "home-google"}
                         or {"type": "plex"} (auto-resolve if only one exists)

        Returns:
            Resolved connection (secrets decrypted) or None if not found

        Raises:
            ValueError: If resolution is ambiguous (multiple connections of type with no ID specified)
        """
        conn_type = declaration.get('type')
        conn_id = declaration.get('id')

        if conn_id:
            # Direct ID reference - load and decrypt
            connection = self._load_connection_file(conn_id)
            if not connection or connection.get('deleted', False):
                return None

            # Verify type matches
            if connection['type'] != conn_type:
                LOGGER.warning(
                    f"Connection {conn_id} is type {connection['type']}, "
                    f"expected {conn_type}"
                )
                return None

            return self._decrypt_fields(connection)

        # No ID specified - auto-resolve by type
        # Find all connections of this type
        matching = [
            c for c in self.list_connections(include_deleted=False)
            if c['type'] == conn_type
        ]

        if len(matching) == 0:
            LOGGER.warning(f"No connections found for type: {conn_type}")
            return None

        if len(matching) > 1:
            connection_names = ', '.join(c['name'] for c in matching)
            raise ValueError(
                f"Multiple {conn_type} connections found ({connection_names}). "
                f"Specify 'id' in connection declaration."
            )

        # Load the full connection with decrypted secrets
        return self._decrypt_fields(self._load_connection_file(matching[0]['id']))

    def _validate_and_encrypt_fields(self, fields: Dict, conn_type: ConnectionType) -> Dict:
        """
        Validate required fields and encrypt secret fields.

        Args:
            fields: Field values from user input
            conn_type: Connection type definition

        Returns:
            Validated and encrypted fields

        Raises:
            ValueError: If required fields are missing
        """
        encryption = get_encryption_service()
        result = {}

        # Check required fields
        for field_def in conn_type.fields:
            field_name = field_def.name
            field_value = fields.get(field_name, '')

            if field_def.required and not field_value:
                raise ValueError(f"Required field missing: {field_def.label}")

            if field_value:
                # Encrypt if secret
                if field_def.secret:
                    result[field_name] = encryption.encrypt(field_value)
                else:
                    result[field_name] = field_value

        # Include any extra fields not in the type definition (for generic connections)
        for field_name, field_value in fields.items():
            if field_name not in result and field_value:
                result[field_name] = field_value

        return result

    def _decrypt_fields(self, connection: Dict) -> Dict:
        """
        Decrypt all encrypted fields in a connection.

        Args:
            connection: Connection document

        Returns:
            Connection with decrypted fields
        """
        if not connection:
            return connection

        encryption = get_encryption_service()
        decrypted = connection.copy()
        decrypted_fields = {}

        for field_name, field_value in connection.get('fields', {}).items():
            if encryption.is_encrypted(field_value):
                try:
                    decrypted_fields[field_name] = encryption.decrypt(field_value)
                except Exception as e:
                    LOGGER.error(f"Failed to decrypt field {field_name}: {e}")
                    decrypted_fields[field_name] = None
            else:
                decrypted_fields[field_name] = field_value

        decrypted['fields'] = decrypted_fields
        return decrypted

    def _mask_secrets(self, connection: Dict) -> Dict:
        """
        Mask secret fields in a connection for API responses.

        Args:
            connection: Connection document

        Returns:
            Connection with secrets masked as "********"
        """
        if not connection:
            return connection

        conn_type = get_connection_type(connection['type'])
        if not conn_type:
            return connection

        encryption = get_encryption_service()
        masked = connection.copy()
        masked_fields = {}

        # Get secret field names
        secret_field_names = {f.name for f in conn_type.fields if f.secret}

        for field_name, field_value in connection.get('fields', {}).items():
            if field_name in secret_field_names and field_value:
                masked_fields[field_name] = encryption.mask_secret(field_value)
            else:
                masked_fields[field_name] = field_value

        masked['fields'] = masked_fields
        return masked


# Global connection service instance (initialized by server on startup)
_connection_service: Optional[ConnectionService] = None


def init_connection_service(connections_dir: str):
    """
    Initialize the global connection service.

    Should be called once during server startup.

    Args:
        connections_dir: Directory for connection storage
    """
    global _connection_service
    _connection_service = ConnectionService(connections_dir)
    LOGGER.info("Connection service initialized")


def get_connection_service() -> ConnectionService:
    """
    Get the global connection service instance.

    Returns:
        The initialized ConnectionService

    Raises:
        RuntimeError: If service hasn't been initialized
    """
    if _connection_service is None:
        raise RuntimeError(
            "Connection service not initialized. Call init_connection_service() first."
        )
    return _connection_service
