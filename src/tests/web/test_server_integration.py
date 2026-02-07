"""Integration tests for critical HTTP endpoints in web/server.py"""

import json
import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

import tornado.testing
import tornado.web
from tornado.testing import AsyncHTTPTestCase

# Import will be relative to test execution
from web import server
from auth.authorization import Authorizer, EmptyGroupProvider
from config.config_service import ConfigService
from execution.execution_service import ExecutionService
from scheduling.schedule_service import ScheduleService


class BaseServerTestCase(AsyncHTTPTestCase):
    """Base test case with test application setup."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temp directories for test
        self.temp_dir = tempfile.mkdtemp()
        self.conf_dir = os.path.join(self.temp_dir, 'conf')
        self.runners_dir = os.path.join(self.conf_dir, 'runners')
        self.projects_dir = os.path.join(self.temp_dir, 'projects')
        self.work_dir = os.path.join(self.temp_dir, 'work')

        os.makedirs(self.runners_dir, exist_ok=True)
        os.makedirs(self.projects_dir, exist_ok=True)
        os.makedirs(self.work_dir, exist_ok=True)

        # Mock services
        self.config_service = Mock(spec=ConfigService)
        self.execution_service = Mock(spec=ExecutionService)
        self.schedule_service = Mock(spec=ScheduleService)
        self.authorizer = Mock(spec=Authorizer)

        # Default: user is admin
        self.authorizer.is_admin.return_value = True
        self.authorizer.is_allowed_in_app.return_value = True

        super().setUp()

    def get_app(self):
        """Create tornado application for testing."""
        # Create minimal application with handlers
        application = tornado.web.Application([
            # Test only critical endpoints
            (r"/admin/scripts/([^/]*)", server.AdminScriptEndpoint),
            (r"/scripts/execute", server.ScriptExecute),
        ])

        # Inject mock services
        application.config_service = self.config_service
        application.execution_service = self.execution_service
        application.schedule_service = self.schedule_service
        application.authorizer = self.authorizer

        return application

    def tearDown(self):
        """Clean up test fixtures."""
        super().tearDown()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestAdminScriptEndpoint(BaseServerTestCase):
    """Test AdminScriptEndpoint (GET/PUT/DELETE /admin/scripts/{name})."""

    def test_get_script_config_success(self):
        """Test GET /admin/scripts/{name} returns script config."""
        # Setup mock config
        mock_config = {
            'name': 'test-script',
            'script_path': '/path/to/script.py',
            'parameters': []
        }
        self.config_service.load_config.return_value = Mock(
            name='test-script',
            config=mock_config
        )

        response = self.fetch('/admin/scripts/test-script')

        self.assertEqual(200, response.code)
        data = json.loads(response.body)
        self.assertEqual('test-script', data['name'])

    def test_get_script_not_found(self):
        """Test GET /admin/scripts/{name} returns 404 when script doesn't exist."""
        self.config_service.load_config.return_value = None

        response = self.fetch('/admin/scripts/nonexistent')

        self.assertEqual(404, response.code)

    def test_delete_script_config_success(self):
        """Test DELETE /admin/scripts/{name} deletes script config."""
        response = self.fetch(
            '/admin/scripts/test-script',
            method='DELETE'
        )

        self.assertEqual(200, response.code)

    def test_put_script_requires_admin(self):
        """Test PUT /admin/scripts/{name} requires admin rights."""
        # User is not admin
        self.authorizer.is_admin.return_value = False

        response = self.fetch(
            '/admin/scripts/test-script',
            method='PUT',
            body=json.dumps({'name': 'test-script'})
        )

        self.assertEqual(403, response.code)


class TestScriptExecute(BaseServerTestCase):
    """Test ScriptExecute endpoint (POST /scripts/execute)."""

    def test_execute_script_success(self):
        """Test successful script execution."""
        # Setup mocks
        mock_config = Mock()
        mock_config.name = 'test-script'
        mock_config.is_allowed_for_user.return_value = True

        self.config_service.load_config.return_value = mock_config
        self.execution_service.start_script.return_value = 'exec-123'

        response = self.fetch(
            '/scripts/execute',
            method='POST',
            body=json.dumps({
                'script': 'test-script',
                'parameters': {}
            })
        )

        self.assertEqual(200, response.code)
        data = json.loads(response.body)
        self.assertEqual('exec-123', data.get('executionId'))

    def test_execute_script_not_found(self):
        """Test executing nonexistent script returns 404."""
        self.config_service.load_config.return_value = None

        response = self.fetch(
            '/scripts/execute',
            method='POST',
            body=json.dumps({
                'script': 'nonexistent',
                'parameters': {}
            })
        )

        self.assertEqual(404, response.code)

    def test_execute_script_forbidden(self):
        """Test executing script user doesn't have access to."""
        mock_config = Mock()
        mock_config.name = 'restricted-script'
        mock_config.is_allowed_for_user.return_value = False

        self.config_service.load_config.return_value = mock_config

        response = self.fetch(
            '/scripts/execute',
            method='POST',
            body=json.dumps({
                'script': 'restricted-script',
                'parameters': {}
            })
        )

        self.assertEqual(403, response.code)

    def test_execute_script_invalid_json(self):
        """Test executing script with invalid JSON returns 400."""
        response = self.fetch(
            '/scripts/execute',
            method='POST',
            body='invalid json {'
        )

        self.assertEqual(400, response.code)

    def test_execute_script_missing_script_name(self):
        """Test executing without script name returns 400."""
        response = self.fetch(
            '/scripts/execute',
            method='POST',
            body=json.dumps({
                'parameters': {}
            })
        )

        self.assertEqual(400, response.code)


class TestGenerateWrapperHandler(unittest.TestCase):
    """Test GenerateWrapperHandler (POST /admin/projects/{id}/wrapper)."""

    def test_duplicate_script_name_validation(self):
        """Test that duplicate script names are rejected."""
        # This would require full handler setup
        # Placeholder for comprehensive test
        pass

    def test_valid_wrapper_generation(self):
        """Test successful wrapper script generation."""
        # Placeholder for comprehensive test
        pass

    def test_missing_entry_point(self):
        """Test error when entry point is missing."""
        # Placeholder for comprehensive test
        pass


class TestScheduleEndpoints(unittest.TestCase):
    """Test schedule-related endpoints."""

    def test_add_schedule_success(self):
        """Test POST /schedules creates new schedule."""
        # Placeholder for comprehensive test
        pass

    def test_add_schedule_invalid_cron(self):
        """Test schedule creation with invalid cron expression."""
        # Placeholder for comprehensive test
        pass

    def test_get_all_schedules(self):
        """Test GET /schedules returns all schedules."""
        # Placeholder for comprehensive test
        pass

    def test_delete_schedule(self):
        """Test DELETE /schedules/{id} removes schedule."""
        # Placeholder for comprehensive test
        pass


class TestConnectionEndpoints(unittest.TestCase):
    """Test connection management endpoints."""

    def test_get_all_connections(self):
        """Test GET /admin/connections returns all connections."""
        # Placeholder for comprehensive test
        pass

    def test_create_connection(self):
        """Test POST /admin/connections creates connection."""
        # Placeholder for comprehensive test
        pass

    def test_create_connection_duplicate_name(self):
        """Test creating connection with duplicate name fails."""
        # Placeholder for comprehensive test
        pass

    def test_get_connection_by_id(self):
        """Test GET /admin/connections/{id} returns specific connection."""
        # Placeholder for comprehensive test
        pass

    def test_delete_connection(self):
        """Test DELETE /admin/connections/{id} removes connection."""
        # Placeholder for comprehensive test
        pass

    def test_update_connection(self):
        """Test PUT /admin/connections/{id} updates connection."""
        # Placeholder for comprehensive test
        pass


class TestAuthenticationEndpoints(unittest.TestCase):
    """Test authentication and authorization endpoints."""

    def test_login_success(self):
        """Test successful login."""
        # Placeholder for comprehensive test
        pass

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        # Placeholder for comprehensive test
        pass

    def test_logout(self):
        """Test logout endpoint."""
        # Placeholder for comprehensive test
        pass

    def test_requires_admin_decorator(self):
        """Test @requires_admin_rights decorator blocks non-admins."""
        # Placeholder for comprehensive test
        pass


class TestHistoryEndpoints(unittest.TestCase):
    """Test execution history endpoints."""

    def test_get_execution_log(self):
        """Test GET /history/execution_log returns execution history."""
        # Placeholder for comprehensive test
        pass

    def test_delete_execution_log_entry(self):
        """Test DELETE /history/execution_log/{id} removes entry."""
        # Placeholder for comprehensive test
        pass

    def test_delete_all_execution_logs(self):
        """Test DELETE /history/execution_log/all removes all logs."""
        # Placeholder for comprehensive test
        pass


if __name__ == '__main__':
    unittest.main()
