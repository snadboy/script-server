"""Tests for connection credential injection."""

import json
import os
import stat
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List

from connections.injection import (
    inject_connection_credentials,
    get_connection_env_vars,
    _CredentialFileCleanup,
    _filename_to_env_suffix,
    _render_template,
)
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
        mock_service = Mock()
        mock_service.get_connection.return_value = self.plex_connection
        mock_get_service.return_value = mock_service
        mock_get_type.return_value = self.plex_type

        env_vars = {'EXISTING_VAR': 'existing_value'}
        result, cleanup = inject_connection_credentials(['home-plex'], env_vars)

        # Verify original env vars preserved
        self.assertEqual('existing_value', result['EXISTING_VAR'])

        # Verify credentials injected
        self.assertEqual('http://plex:32400', result['PLEX_URL'])
        self.assertEqual('abc123xyz', result['PLEX_TOKEN'])

        # Verify original dict not modified
        self.assertNotIn('PLEX_URL', env_vars)

        # No file cleanup for env-only injection
        self.assertIsNone(cleanup)

        # Verify mask_secrets=False was passed
        mock_service.get_connection.assert_called_once_with('home-plex', mask_secrets=False)

    @patch('connections.injection.get_connection_service')
    def test_empty_connection_list(self, mock_get_service):
        """Test with empty connection list returns original env vars."""
        env_vars = {'VAR1': 'value1'}
        result, cleanup = inject_connection_credentials([], env_vars)

        self.assertEqual(env_vars, result)
        self.assertIsNone(cleanup)
        mock_get_service.assert_not_called()

    @patch('connections.injection.get_connection_service')
    def test_none_connection_list(self, mock_get_service):
        """Test with None connection list returns original env vars."""
        env_vars = {'VAR1': 'value1'}
        result, cleanup = inject_connection_credentials(None, env_vars)

        self.assertEqual(env_vars, result)
        self.assertIsNone(cleanup)
        mock_get_service.assert_not_called()

    @patch('connections.injection.get_connection_service')
    def test_connection_service_not_initialized(self, mock_get_service):
        """Test when connection service is not initialized."""
        mock_get_service.return_value = None

        env_vars = {'VAR1': 'value1'}
        result, cleanup = inject_connection_credentials(['home-plex'], env_vars)

        self.assertEqual(env_vars, result)
        self.assertIsNone(cleanup)

    @patch('connections.injection.get_connection_type')
    @patch('connections.injection.get_connection_service')
    def test_connection_not_found(self, mock_get_service, mock_get_type):
        """Test when connection ID doesn't exist."""
        mock_service = Mock()
        mock_service.get_connection.return_value = None
        mock_get_service.return_value = mock_service

        env_vars = {'VAR1': 'value1'}
        result, cleanup = inject_connection_credentials(['nonexistent'], env_vars)

        self.assertEqual(env_vars, result)
        mock_get_type.assert_not_called()
        self.assertIsNone(cleanup)

    @patch('connections.injection.get_connection_type')
    @patch('connections.injection.get_connection_service')
    def test_unknown_connection_type(self, mock_get_service, mock_get_type):
        """Test when connection type is not registered."""
        mock_service = Mock()
        mock_service.get_connection.return_value = self.plex_connection
        mock_get_service.return_value = mock_service
        mock_get_type.return_value = None

        env_vars = {'VAR1': 'value1'}
        result, cleanup = inject_connection_credentials(['home-plex'], env_vars)

        self.assertEqual(env_vars, result)
        self.assertNotIn('PLEX_URL', result)
        self.assertIsNone(cleanup)

    @patch('connections.injection.get_connection_type')
    @patch('connections.injection.get_connection_service')
    def test_file_injection_mode(self, mock_get_service, mock_get_type):
        """Test file-based credential injection writes temp files."""
        google_type = ConnectionType(
            type_id='google',
            display_name='Google Account',
            icon='cloud',
            description='Google services',
            fields=[
                ConnectionField(name='client_id', label='Client ID',
                                field_type='text', required=True, secret=True),
                ConnectionField(name='client_secret', label='Client Secret',
                                field_type='password', required=True, secret=True),
                ConnectionField(name='token_data', label='Token Data',
                                field_type='textarea', required=False, secret=True),
            ],
            injection_mode='file',
            env_prefix='GOOGLE',
            file_templates={
                'credentials.json': '{"client_id": "{{client_id}}", "client_secret": "{{client_secret}}"}',
                'token.json': '{{token_data}}'
            }
        )

        google_connection = {
            'id': 'home-google',
            'type': 'google',
            'fields': {
                'client_id': 'my-client-id',
                'client_secret': 'my-secret',
                'token_data': '{"token": "abc"}'
            }
        }

        mock_service = Mock()
        mock_service.get_connection.return_value = google_connection
        mock_get_service.return_value = mock_service
        mock_get_type.return_value = google_type

        result, cleanup = inject_connection_credentials(['home-google'], {})

        # Should have path env vars
        self.assertIn('GOOGLE_CREDENTIALS_PATH', result)
        self.assertIn('GOOGLE_TOKEN_PATH', result)

        # Should NOT have field env vars (mode is 'file', not 'env' or 'both')
        self.assertNotIn('GOOGLE_CLIENT_ID', result)
        self.assertNotIn('GOOGLE_CLIENT_SECRET', result)

        # Verify files exist and have correct content
        creds_path = result['GOOGLE_CREDENTIALS_PATH']
        token_path = result['GOOGLE_TOKEN_PATH']

        self.assertTrue(os.path.exists(creds_path))
        self.assertTrue(os.path.exists(token_path))

        with open(creds_path) as f:
            creds_content = json.loads(f.read())
        self.assertEqual('my-client-id', creds_content['client_id'])
        self.assertEqual('my-secret', creds_content['client_secret'])

        with open(token_path) as f:
            token_content = f.read()
        self.assertEqual('{"token": "abc"}', token_content)

        # Verify file permissions (0600)
        creds_mode = os.stat(creds_path).st_mode & 0o777
        self.assertEqual(stat.S_IRUSR | stat.S_IWUSR, creds_mode)

        # Cleanup should exist
        self.assertIsNotNone(cleanup)

        # Clean up temp files
        cleanup.finished()
        self.assertFalse(os.path.exists(creds_path))

    @patch('connections.injection.get_connection_type')
    @patch('connections.injection.get_connection_service')
    def test_both_injection_mode(self, mock_get_service, mock_get_type):
        """Test 'both' injection mode sets env vars AND writes files."""
        both_type = ConnectionType(
            type_id='hybrid',
            display_name='Hybrid',
            icon='cloud',
            description='Hybrid connection',
            fields=[
                ConnectionField(name='api_key', label='API Key',
                                field_type='password', required=True, secret=True),
                ConnectionField(name='config_data', label='Config',
                                field_type='textarea', required=False, secret=False),
            ],
            injection_mode='both',
            env_prefix='HYBRID',
            file_templates={
                'config.yaml': 'api_key: {{api_key}}\ndata: {{config_data}}'
            }
        )

        connection = {
            'id': 'my-hybrid',
            'type': 'hybrid',
            'fields': {
                'api_key': 'secret-key-123',
                'config_data': 'some-data'
            }
        }

        mock_service = Mock()
        mock_service.get_connection.return_value = connection
        mock_get_service.return_value = mock_service
        mock_get_type.return_value = both_type

        result, cleanup = inject_connection_credentials(['my-hybrid'], {})

        # Should have BOTH env vars AND file paths
        self.assertEqual('secret-key-123', result['HYBRID_API_KEY'])
        self.assertEqual('some-data', result['HYBRID_CONFIG_DATA'])
        self.assertIn('HYBRID_CONFIG_PATH', result)

        # Verify file content
        with open(result['HYBRID_CONFIG_PATH']) as f:
            content = f.read()
        self.assertIn('api_key: secret-key-123', content)
        self.assertIn('data: some-data', content)

        # Cleanup
        self.assertIsNotNone(cleanup)
        cleanup.finished()

    @patch('connections.injection.get_connection_type')
    @patch('connections.injection.get_connection_service')
    def test_missing_field_values(self, mock_get_service, mock_get_type):
        """Test when connection has missing field values."""
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

        result, cleanup = inject_connection_credentials(['incomplete-plex'], {})

        self.assertEqual('http://plex:32400', result['PLEX_URL'])
        self.assertNotIn('PLEX_TOKEN', result)
        self.assertIsNone(cleanup)

    @patch('connections.injection.get_connection_type')
    @patch('connections.injection.get_connection_service')
    def test_multiple_connections(self, mock_get_service, mock_get_type):
        """Test injecting multiple connections."""
        sonarr_type = ConnectionType(
            type_id='sonarr',
            display_name='Sonarr',
            icon='sonarr',
            description='Sonarr connection',
            fields=[
                ConnectionField(name='url', label='URL', field_type='url',
                                required=True, secret=False),
                ConnectionField(name='api_key', label='API Key', field_type='password',
                                required=True, secret=True)
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

        mock_service = Mock()

        def get_connection_side_effect(conn_id, mask_secrets=True):
            if conn_id == 'home-plex':
                return self.plex_connection
            elif conn_id == 'my-sonarr':
                return sonarr_connection
            return None

        mock_service.get_connection.side_effect = get_connection_side_effect
        mock_get_service.return_value = mock_service

        def get_type_side_effect(type_id):
            if type_id == 'plex':
                return self.plex_type
            elif type_id == 'sonarr':
                return sonarr_type
            return None

        mock_get_type.side_effect = get_type_side_effect

        result, cleanup = inject_connection_credentials(['home-plex', 'my-sonarr'], {})

        self.assertEqual('http://plex:32400', result['PLEX_URL'])
        self.assertEqual('abc123xyz', result['PLEX_TOKEN'])
        self.assertEqual('http://sonarr:8989', result['SONARR_URL'])
        self.assertEqual('sonarr-key-123', result['SONARR_API_KEY'])
        self.assertIsNone(cleanup)

    @patch('connections.injection.get_connection_type')
    @patch('connections.injection.get_connection_service')
    def test_exception_handling(self, mock_get_service, mock_get_type):
        """Test that exceptions during injection are caught and logged."""
        mock_service = Mock()
        mock_service.get_connection.side_effect = Exception('Database error')
        mock_get_service.return_value = mock_service

        env_vars = {'VAR1': 'value1'}
        result, cleanup = inject_connection_credentials(['problematic'], env_vars)

        self.assertEqual(env_vars, result)
        self.assertIsNone(cleanup)

    @patch('connections.injection.get_connection_type')
    @patch('connections.injection.get_connection_service')
    def test_partial_failure(self, mock_get_service, mock_get_type):
        """Test that one failing connection doesn't prevent others from injecting."""
        mock_service = Mock()

        def get_connection_side_effect(conn_id, mask_secrets=True):
            if conn_id == 'failing':
                raise Exception('Connection error')
            elif conn_id == 'home-plex':
                return self.plex_connection
            return None

        mock_service.get_connection.side_effect = get_connection_side_effect
        mock_get_service.return_value = mock_service
        mock_get_type.return_value = self.plex_type

        result, cleanup = inject_connection_credentials(['failing', 'home-plex'], {})

        self.assertEqual('http://plex:32400', result['PLEX_URL'])
        self.assertEqual('abc123xyz', result['PLEX_TOKEN'])

    @patch('connections.injection.get_connection_type')
    @patch('connections.injection.get_connection_service')
    def test_env_var_name_construction(self, mock_get_service, mock_get_type):
        """Test that environment variable names are constructed correctly."""
        test_type = ConnectionType(
            type_id='test',
            display_name='Test',
            icon='test',
            description='Test connection',
            fields=[
                ConnectionField(name='api_key', label='API Key', field_type='text',
                                required=True, secret=False),
                ConnectionField(name='base_url', label='Base URL', field_type='url',
                                required=True, secret=False)
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

        result, cleanup = inject_connection_credentials(['test-conn'], {})

        self.assertEqual('key123', result['TEST_API_KEY'])
        self.assertEqual('http://test.com', result['TEST_BASE_URL'])


class TestFileCleanup(unittest.TestCase):
    """Test _CredentialFileCleanup."""

    def test_cleanup_removes_temp_dirs(self):
        """Test that cleanup removes all temp directories."""
        import tempfile

        dir1 = tempfile.mkdtemp(prefix='test_cleanup_')
        dir2 = tempfile.mkdtemp(prefix='test_cleanup_')

        # Write a file in each to verify full removal
        with open(os.path.join(dir1, 'test.txt'), 'w') as f:
            f.write('test')
        with open(os.path.join(dir2, 'test.txt'), 'w') as f:
            f.write('test')

        self.assertTrue(os.path.exists(dir1))
        self.assertTrue(os.path.exists(dir2))

        cleanup = _CredentialFileCleanup([dir1, dir2])
        cleanup.finished()

        self.assertFalse(os.path.exists(dir1))
        self.assertFalse(os.path.exists(dir2))

    def test_cleanup_handles_missing_dirs(self):
        """Test that cleanup doesn't fail on already-removed dirs."""
        cleanup = _CredentialFileCleanup(['/tmp/nonexistent_dir_12345'])
        # Should not raise
        cleanup.finished()


class TestHelperFunctions(unittest.TestCase):
    """Test helper functions."""

    def test_filename_to_env_suffix(self):
        self.assertEqual('CREDENTIALS', _filename_to_env_suffix('credentials.json'))
        self.assertEqual('TOKEN', _filename_to_env_suffix('token.json'))
        self.assertEqual('MY_CONFIG', _filename_to_env_suffix('my-config.yaml'))
        self.assertEqual('DATA', _filename_to_env_suffix('data.txt'))

    def test_render_template(self):
        template = '{"id": "{{client_id}}", "secret": "{{client_secret}}"}'
        values = {'client_id': 'my-id', 'client_secret': 'my-secret'}
        result = _render_template(template, values)
        self.assertEqual('{"id": "my-id", "secret": "my-secret"}', result)

    def test_render_template_missing_field(self):
        template = '{{present}} and {{missing}}'
        values = {'present': 'hello'}
        result = _render_template(template, values)
        self.assertEqual('hello and {{missing}}', result)

    def test_render_template_none_value(self):
        template = 'value: {{field}}'
        values = {'field': None}
        result = _render_template(template, values)
        self.assertEqual('value: ', result)


class TestGetConnectionEnvVars(unittest.TestCase):
    """Test get_connection_env_vars helper function."""

    @patch('connections.injection.inject_connection_credentials')
    def test_calls_inject_with_empty_env(self, mock_inject):
        """Test that get_connection_env_vars calls inject with empty dict."""
        mock_inject.return_value = ({'PLEX_URL': 'http://plex:32400'}, None)

        result = get_connection_env_vars(['home-plex'])

        mock_inject.assert_called_once_with(['home-plex'], {})
        self.assertEqual({'PLEX_URL': 'http://plex:32400'}, result)


if __name__ == '__main__':
    unittest.main()
