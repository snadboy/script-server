"""Tests for connection credential injection."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List

from connections.injection import inject_connection_credentials, get_connection_env_vars
from connections.connection_types import ConnectionType, ConnectionField


class TestInjectConnectionCredentials(unittest.TestCase):
    """Test connection credential injection into environment variables."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock connection type for Plex
        self.plex_type = ConnectionType(
            type_id='plex',
            display_name='Plex Media Server',
            icon='plex',
            description='Plex server connection',
            fields=[
                ConnectionField(
                    name='url',
                    label='Server URL',
                    field_type='url',
                    required=True,
                    secret=False
                ),
                ConnectionField(
                    name='token',
                    label='API Token',
                    field_type='password',
                    required=True,
                    secret=True
                )
            ],
            injection_mode='env',
            env_prefix='PLEX'
        )

        # Mock connection instance
        self.plex_connection = {
            'id': 'home-plex',
            'name': 'Home Plex Server',
            'type': 'plex',
            'fields': {
                'url': 'http://plex:32400',
                'token': 'abc123xyz'
            }
        }

    @patch('connections.injection.get_connection_type')
    @patch('connections.injection.get_connection_service')
    def test_successful_injection(self, mock_get_service, mock_get_type):
        """Test successful credential injection."""
        # Setup mocks
        mock_service = Mock()
        mock_service.get_connection.return_value = self.plex_connection
        mock_get_service.return_value = mock_service
        mock_get_type.return_value = self.plex_type

        # Test injection
        env_vars = {'EXISTING_VAR': 'existing_value'}
        result = inject_connection_credentials(['home-plex'], env_vars)

        # Verify original env vars preserved
        self.assertEqual('existing_value', result['EXISTING_VAR'])

        # Verify credentials injected
        self.assertEqual('http://plex:32400', result['PLEX_URL'])
        self.assertEqual('abc123xyz', result['PLEX_TOKEN'])

        # Verify original dict not modified
        self.assertNotIn('PLEX_URL', env_vars)

    @patch('connections.injection.get_connection_service')
    def test_empty_connection_list(self, mock_get_service):
        """Test with empty connection list returns original env vars."""
        env_vars = {'VAR1': 'value1'}
        result = inject_connection_credentials([], env_vars)

        self.assertEqual(env_vars, result)
        mock_get_service.assert_not_called()

    @patch('connections.injection.get_connection_service')
    def test_none_connection_list(self, mock_get_service):
        """Test with None connection list returns original env vars."""
        env_vars = {'VAR1': 'value1'}
        result = inject_connection_credentials(None, env_vars)

        self.assertEqual(env_vars, result)
        mock_get_service.assert_not_called()

    @patch('connections.injection.get_connection_service')
    def test_connection_service_not_initialized(self, mock_get_service):
        """Test when connection service is not initialized."""
        mock_get_service.return_value = None

        env_vars = {'VAR1': 'value1'}
        result = inject_connection_credentials(['home-plex'], env_vars)

        # Should return original env vars unchanged
        self.assertEqual(env_vars, result)

    @patch('connections.injection.get_connection_type')
    @patch('connections.injection.get_connection_service')
    def test_connection_not_found(self, mock_get_service, mock_get_type):
        """Test when connection ID doesn't exist."""
        mock_service = Mock()
        mock_service.get_connection.return_value = None
        mock_get_service.return_value = mock_service

        env_vars = {'VAR1': 'value1'}
        result = inject_connection_credentials(['nonexistent'], env_vars)

        # Should return original env vars
        self.assertEqual(env_vars, result)
        # Should not attempt to get connection type
        mock_get_type.assert_not_called()

    @patch('connections.injection.get_connection_type')
    @patch('connections.injection.get_connection_service')
    def test_unknown_connection_type(self, mock_get_service, mock_get_type):
        """Test when connection type is not registered."""
        mock_service = Mock()
        mock_service.get_connection.return_value = self.plex_connection
        mock_get_service.return_value = mock_service
        mock_get_type.return_value = None  # Type not found

        env_vars = {'VAR1': 'value1'}
        result = inject_connection_credentials(['home-plex'], env_vars)

        # Should return original env vars
        self.assertEqual(env_vars, result)
        self.assertNotIn('PLEX_URL', result)

    @patch('connections.injection.get_connection_type')
    @patch('connections.injection.get_connection_service')
    def test_unsupported_injection_mode(self, mock_get_service, mock_get_type):
        """Test when connection type has unsupported injection mode."""
        # Create type with 'file' injection mode
        file_type = ConnectionType(
            type_id='custom',
            display_name='Custom',
            icon='custom',
            description='Custom connection',
            fields=[
                ConnectionField(
                    name='key',
                    label='Key',
                    field_type='text',
                    required=True,
                    secret=False
                )
            ],
            injection_mode='file',  # Not supported
            env_prefix='CUSTOM'
        )

        mock_service = Mock()
        mock_service.get_connection.return_value = {
            'id': 'custom-conn',
            'type': 'custom',
            'fields': {'key': 'value'}
        }
        mock_get_service.return_value = mock_service
        mock_get_type.return_value = file_type

        env_vars = {}
        result = inject_connection_credentials(['custom-conn'], env_vars)

        # Should not inject anything
        self.assertEqual({}, result)

    @patch('connections.injection.get_connection_type')
    @patch('connections.injection.get_connection_service')
    def test_missing_field_values(self, mock_get_service, mock_get_type):
        """Test when connection has missing field values."""
        # Connection with only URL, no token
        incomplete_connection = {
            'id': 'incomplete-plex',
            'type': 'plex',
            'fields': {
                'url': 'http://plex:32400'
                # token missing
            }
        }

        mock_service = Mock()
        mock_service.get_connection.return_value = incomplete_connection
        mock_get_service.return_value = mock_service
        mock_get_type.return_value = self.plex_type

        result = inject_connection_credentials(['incomplete-plex'], {})

        # URL should be injected
        self.assertEqual('http://plex:32400', result['PLEX_URL'])
        # Token should NOT be injected (field value is None)
        self.assertNotIn('PLEX_TOKEN', result)

    @patch('connections.injection.get_connection_type')
    @patch('connections.injection.get_connection_service')
    def test_multiple_connections(self, mock_get_service, mock_get_type):
        """Test injecting multiple connections."""
        # Setup second connection type (Sonarr)
        sonarr_type = ConnectionType(
            type_id='sonarr',
            display_name='Sonarr',
            icon='sonarr',
            description='Sonarr connection',
            fields=[
                ConnectionField(
                    name='url',
                    label='URL',
                    field_type='url',
                    required=True,
                    secret=False
                ),
                ConnectionField(
                    name='api_key',
                    label='API Key',
                    field_type='password',
                    required=True,
                    secret=True
                )
            ],
            injection_mode='env',
            env_prefix='SONARR'
        )

        sonarr_connection = {
            'id': 'my-sonarr',
            'type': 'sonarr',
            'fields': {
                'url': 'http://sonarr:8989',
                'api_key': 'sonarr-key-123'
            }
        }

        # Mock service to return different connections
        mock_service = Mock()

        def get_connection_side_effect(conn_id):
            if conn_id == 'home-plex':
                return self.plex_connection
            elif conn_id == 'my-sonarr':
                return sonarr_connection
            return None

        mock_service.get_connection.side_effect = get_connection_side_effect
        mock_get_service.return_value = mock_service

        # Mock type lookup
        def get_type_side_effect(type_id):
            if type_id == 'plex':
                return self.plex_type
            elif type_id == 'sonarr':
                return sonarr_type
            return None

        mock_get_type.side_effect = get_type_side_effect

        # Test injection of multiple connections
        result = inject_connection_credentials(['home-plex', 'my-sonarr'], {})

        # Verify both connections injected
        self.assertEqual('http://plex:32400', result['PLEX_URL'])
        self.assertEqual('abc123xyz', result['PLEX_TOKEN'])
        self.assertEqual('http://sonarr:8989', result['SONARR_URL'])
        self.assertEqual('sonarr-key-123', result['SONARR_API_KEY'])

    @patch('connections.injection.get_connection_type')
    @patch('connections.injection.get_connection_service')
    def test_exception_handling(self, mock_get_service, mock_get_type):
        """Test that exceptions during injection are caught and logged."""
        mock_service = Mock()
        # Simulate exception when getting connection
        mock_service.get_connection.side_effect = Exception('Database error')
        mock_get_service.return_value = mock_service

        env_vars = {'VAR1': 'value1'}
        result = inject_connection_credentials(['problematic'], env_vars)

        # Should return original env vars despite error
        self.assertEqual(env_vars, result)

    @patch('connections.injection.get_connection_type')
    @patch('connections.injection.get_connection_service')
    def test_partial_failure(self, mock_get_service, mock_get_type):
        """Test that one failing connection doesn't prevent others from injecting."""
        mock_service = Mock()

        # First connection fails, second succeeds
        def get_connection_side_effect(conn_id):
            if conn_id == 'failing':
                raise Exception('Connection error')
            elif conn_id == 'home-plex':
                return self.plex_connection
            return None

        mock_service.get_connection.side_effect = get_connection_side_effect
        mock_get_service.return_value = mock_service
        mock_get_type.return_value = self.plex_type

        result = inject_connection_credentials(['failing', 'home-plex'], {})

        # Second connection should still be injected
        self.assertEqual('http://plex:32400', result['PLEX_URL'])
        self.assertEqual('abc123xyz', result['PLEX_TOKEN'])

    @patch('connections.injection.get_connection_type')
    @patch('connections.injection.get_connection_service')
    def test_env_var_name_construction(self, mock_get_service, mock_get_type):
        """Test that environment variable names are constructed correctly."""
        # Create type with lowercase field names
        test_type = ConnectionType(
            type_id='test',
            display_name='Test',
            icon='test',
            description='Test connection',
            fields=[
                ConnectionField(
                    name='api_key',
                    label='API Key',
                    field_type='text',
                    required=True,
                    secret=False
                ),
                ConnectionField(
                    name='base_url',
                    label='Base URL',
                    field_type='url',
                    required=True,
                    secret=False
                )
            ],
            injection_mode='env',
            env_prefix='TEST'
        )

        connection = {
            'id': 'test-conn',
            'type': 'test',
            'fields': {
                'api_key': 'key123',
                'base_url': 'http://test.com'
            }
        }

        mock_service = Mock()
        mock_service.get_connection.return_value = connection
        mock_get_service.return_value = mock_service
        mock_get_type.return_value = test_type

        result = inject_connection_credentials(['test-conn'], {})

        # Verify uppercase field names
        self.assertEqual('key123', result['TEST_API_KEY'])
        self.assertEqual('http://test.com', result['TEST_BASE_URL'])


class TestGetConnectionEnvVars(unittest.TestCase):
    """Test get_connection_env_vars helper function."""

    @patch('connections.injection.inject_connection_credentials')
    def test_calls_inject_with_empty_env(self, mock_inject):
        """Test that get_connection_env_vars calls inject with empty dict."""
        mock_inject.return_value = {'PLEX_URL': 'http://plex:32400'}

        result = get_connection_env_vars(['home-plex'])

        # Verify it called inject with empty dict
        mock_inject.assert_called_once_with(['home-plex'], {})
        self.assertEqual({'PLEX_URL': 'http://plex:32400'}, result)


if __name__ == '__main__':
    unittest.main()
