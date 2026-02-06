"""
Encryption utilities for connection credential storage.

Uses Fernet symmetric encryption (from cryptography library) for secure,
authenticated encryption of sensitive connection fields.
"""

import os
import logging
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

LOGGER = logging.getLogger('script_server.connections.encryption')

# Version prefix for encrypted values - allows future key rotation/migration
ENCRYPTION_VERSION = 'v1'
ENCRYPTION_PREFIX = f'ENC:{ENCRYPTION_VERSION}:'


class EncryptionService:
    """Manages encryption key and provides encrypt/decrypt operations."""

    def __init__(self, key_file_path: str):
        """
        Initialize encryption service.

        Args:
            key_file_path: Path to the encryption key file (typically conf/.connection_key)
        """
        self.key_file_path = Path(key_file_path)
        self._fernet: Optional[Fernet] = None
        self._ensure_key_exists()

    def _ensure_key_exists(self):
        """Generate and store encryption key if it doesn't exist."""
        if not self.key_file_path.exists():
            LOGGER.warning("=" * 80)
            LOGGER.warning("No encryption key found - generating new key")
            LOGGER.warning(f"Key location: {self.key_file_path.absolute()}")
            LOGGER.warning("IMPORTANT: Back up this file securely!")
            LOGGER.warning("Without the key, encrypted connection data cannot be recovered.")
            LOGGER.warning("=" * 80)

            # Generate new key
            key = Fernet.generate_key()

            # Ensure parent directory exists
            self.key_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write key with restrictive permissions (read-only by owner)
            # Write first, then chmod (safer than setting umask)
            self.key_file_path.write_bytes(key)
            os.chmod(self.key_file_path, 0o400)

            LOGGER.info(f"Encryption key generated and saved to {self.key_file_path}")

        # Load the key
        key = self.key_file_path.read_bytes()
        self._fernet = Fernet(key)
        LOGGER.debug(f"Encryption service initialized with key from {self.key_file_path}")

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string value.

        Args:
            plaintext: The value to encrypt

        Returns:
            Encrypted value with version prefix (e.g., "ENC:v1:gAAAAAB...")
        """
        if not plaintext:
            return plaintext

        encrypted_bytes = self._fernet.encrypt(plaintext.encode('utf-8'))
        encrypted_str = encrypted_bytes.decode('ascii')

        return f"{ENCRYPTION_PREFIX}{encrypted_str}"

    def decrypt(self, encrypted_value: str) -> str:
        """
        Decrypt an encrypted string value.

        Args:
            encrypted_value: Value with ENC:v1: prefix

        Returns:
            Decrypted plaintext string

        Raises:
            ValueError: If the encrypted value has invalid format
            InvalidToken: If decryption fails (wrong key, corrupted data)
        """
        if not encrypted_value:
            return encrypted_value

        # Not encrypted - return as-is
        if not encrypted_value.startswith('ENC:'):
            return encrypted_value

        # Parse version and encrypted data
        if not encrypted_value.startswith(ENCRYPTION_PREFIX):
            raise ValueError(
                f"Unsupported encryption version. Expected {ENCRYPTION_PREFIX}, "
                f"got {encrypted_value[:10]}..."
            )

        # Extract the Fernet token (everything after the prefix)
        fernet_token = encrypted_value[len(ENCRYPTION_PREFIX):]

        try:
            decrypted_bytes = self._fernet.decrypt(fernet_token.encode('ascii'))
            return decrypted_bytes.decode('utf-8')
        except InvalidToken as e:
            LOGGER.error(f"Failed to decrypt value: {e}")
            raise ValueError("Decryption failed - invalid token or wrong key") from e

    def is_encrypted(self, value: str) -> bool:
        """
        Check if a value is encrypted.

        Args:
            value: String to check

        Returns:
            True if the value has an encryption prefix
        """
        return isinstance(value, str) and value.startswith('ENC:')

    def mask_secret(self, value: str) -> str:
        """
        Return a masked version of a secret value for display.

        Args:
            value: The value to mask (encrypted or plaintext)

        Returns:
            "********" for display purposes
        """
        return "********" if value else ""


# Global encryption service instance (initialized by server on startup)
_encryption_service: Optional[EncryptionService] = None


def init_encryption(key_file_path: str):
    """
    Initialize the global encryption service.

    Should be called once during server startup.

    Args:
        key_file_path: Path to encryption key file
    """
    global _encryption_service
    _encryption_service = EncryptionService(key_file_path)
    LOGGER.info("Encryption service initialized")


def get_encryption_service() -> EncryptionService:
    """
    Get the global encryption service instance.

    Returns:
        The initialized EncryptionService

    Raises:
        RuntimeError: If encryption service hasn't been initialized
    """
    if _encryption_service is None:
        raise RuntimeError(
            "Encryption service not initialized. Call init_encryption() first."
        )
    return _encryption_service
