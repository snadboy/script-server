import os
import unittest
from unittest.mock import patch, MagicMock, call
import subprocess

from execution.process_base import ProcessWrapper
from tests import test_utils


class MockProcessWrapper(ProcessWrapper):
    """Concrete implementation of ProcessWrapper for testing"""

    def __init__(self, command, working_directory, all_env_variables: dict):
        super().__init__(command, working_directory, all_env_variables)
        self.process = MagicMock()
        self.process.pid = 12345
        self.process.poll = MagicMock(return_value=None)  # Not finished

    def pipe_process_output(self):
        pass

    def start_execution(self, command, working_directory):
        pass

    def write_to_input(self, value):
        pass

    def wait_finish(self):
        pass


class TestProcessBaseKillSecurity(unittest.TestCase):
    """Security tests for process termination on Windows"""

    @patch('execution.process_base.os_utils.is_win', return_value=True)
    @patch('execution.process_base.subprocess.Popen')
    def test_kill_uses_list_args_not_shell(self, mock_popen, mock_is_win):
        """Security test: Verify kill() uses list args with shell=False to prevent command injection"""
        wrapper = MockProcessWrapper(['python', 'test.py'], '/tmp', {})

        wrapper.kill()

        # Verify Popen was called with list arguments (not string)
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args

        # Check that arguments are passed as a list
        self.assertIsInstance(call_args[0][0], list, 'Arguments must be a list to prevent command injection')

        # Check exact command structure
        expected_command = ['taskkill', '/F', '/T', '/PID', '12345']
        self.assertEqual(expected_command, call_args[0][0])

        # Check that shell=False (either explicit or default)
        if 'shell' in call_args[1]:
            self.assertFalse(call_args[1]['shell'], 'shell must be False to prevent command injection')

    @patch('execution.process_base.os_utils.is_win', return_value=True)
    @patch('execution.process_base.subprocess.Popen')
    def test_kill_with_malicious_pid(self, mock_popen, mock_is_win):
        """Security test: Verify malicious PID values cannot inject commands"""
        wrapper = MockProcessWrapper(['python', 'test.py'], '/tmp', {})

        # Simulate a malicious PID that would cause command injection if using string concatenation
        # For example: "12345 & del /f /s /q C:\\*"
        wrapper.process.pid = '12345 & del /f /s /q C:\\*'

        wrapper.kill()

        # With list arguments, the malicious PID becomes a harmless string argument
        call_args = mock_popen.call_args
        self.assertIsInstance(call_args[0][0], list)

        # The malicious string should be safely passed as a single argument
        self.assertEqual(['taskkill', '/F', '/T', '/PID', '12345 & del /f /s /q C:\\*'], call_args[0][0])

    @patch('execution.process_base.os_utils.is_win', return_value=False)
    @patch('execution.process_base.os.killpg')
    @patch('execution.process_base.os.getpgid', return_value=54321)
    def test_kill_unix_no_subprocess(self, mock_getpgid, mock_killpg, mock_is_win):
        """Verify Unix kill() doesn't use subprocess (no injection risk)"""
        wrapper = MockProcessWrapper(['python', 'test.py'], '/tmp', {})

        wrapper.kill()

        # On Unix, should use os.killpg, not subprocess
        mock_killpg.assert_called_once_with(54321, 9)  # SIGKILL = 9

    def setUp(self):
        test_utils.setup()
        super().setUp()

    def tearDown(self):
        test_utils.cleanup()
        super().tearDown()
