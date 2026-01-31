import unittest
import tempfile
import shutil
import zipfile
import sys
from pathlib import Path
from io import BytesIO

from project_manager.project_service import ProjectService


class TestZipSlipProtection(unittest.TestCase):
    """Test ZIP extraction protection against zip-slip attacks"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.service = ProjectService(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_zip_with_paths(self, paths):
        """Helper to create a ZIP file with specified paths"""
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for path in paths:
                zf.writestr(path, f'content of {path}')
        return zip_buffer.getvalue()

    def test_safe_zip_extraction(self):
        """Safe ZIP with normal paths should extract successfully"""
        zip_data = self._create_zip_with_paths([
            'myproject/README.md',
            'myproject/src/main.py',
            'myproject/src/__init__.py'
        ])

        # Should not raise
        result = self.service.import_from_zip(zip_data, 'safe.zip')
        self.assertIsNotNone(result)
        self.assertIn('id', result)

    def test_zip_slip_parent_directory(self):
        """ZIP with ../ path traversal should be rejected"""
        zip_data = self._create_zip_with_paths([
            'myproject/README.md',
            '../../etc/passwd'  # Malicious path
        ])

        with self.assertRaises(ValueError) as cm:
            self.service.import_from_zip(zip_data, 'malicious.zip')
        self.assertIn('path traversal', str(cm.exception).lower())

    def test_zip_slip_multiple_parent_traversal(self):
        """ZIP with multiple ../ should be rejected"""
        zip_data = self._create_zip_with_paths([
            'myproject/file.py',
            '../../../../../../../etc/cron.d/backdoor'  # Deep traversal
        ])

        with self.assertRaises(ValueError) as cm:
            self.service.import_from_zip(zip_data, 'malicious2.zip')
        self.assertIn('path traversal', str(cm.exception).lower())

    def test_zip_slip_parent_in_middle(self):
        """ZIP with ../ in the middle of path should be rejected"""
        zip_data = self._create_zip_with_paths([
            'myproject/README.md',
            'myproject/../../../etc/shadow'  # Traversal in middle
        ])

        with self.assertRaises(ValueError) as cm:
            self.service.import_from_zip(zip_data, 'malicious3.zip')
        self.assertIn('path traversal', str(cm.exception).lower())

    def test_zip_with_absolute_path(self):
        """ZIP with absolute path should be rejected"""
        zip_data = self._create_zip_with_paths([
            'myproject/file.py',
            '/etc/passwd'  # Absolute path
        ])

        with self.assertRaises(ValueError) as cm:
            self.service.import_from_zip(zip_data, 'malicious4.zip')
        self.assertIn('path traversal', str(cm.exception).lower())

    @unittest.skipUnless(sys.platform == 'win32', 'Windows-specific path test')
    def test_zip_with_windows_absolute_path(self):
        """ZIP with Windows absolute path should be rejected"""
        zip_data = self._create_zip_with_paths([
            'myproject/file.py',
            'C:/Windows/System32/evil.dll'  # Windows absolute path
        ])

        with self.assertRaises(ValueError) as cm:
            self.service.import_from_zip(zip_data, 'malicious5.zip')
        self.assertIn('path traversal', str(cm.exception).lower())

    @unittest.skipUnless(sys.platform == 'win32', 'Windows-specific path test')
    def test_zip_with_backslash_traversal(self):
        """ZIP with backslash path traversal should be rejected"""
        zip_data = self._create_zip_with_paths([
            'myproject/file.py',
            '..\\..\\..\\Windows\\System32\\backdoor.exe'  # Windows-style traversal
        ])

        with self.assertRaises(ValueError) as cm:
            self.service.import_from_zip(zip_data, 'malicious6.zip')
        self.assertIn('path traversal', str(cm.exception).lower())

    def test_safe_zip_with_subdirectories(self):
        """Safe ZIP with deep subdirectories should extract"""
        zip_data = self._create_zip_with_paths([
            'myproject/src/utils/helpers.py',
            'myproject/src/models/user.py',
            'myproject/tests/test_main.py',
            'myproject/docs/api.md'
        ])

        # Should not raise
        result = self.service.import_from_zip(zip_data, 'safe_deep.zip')
        self.assertIsNotNone(result)

    def test_zip_with_dot_prefix(self):
        """ZIP with hidden files (. prefix) should extract safely"""
        zip_data = self._create_zip_with_paths([
            'myproject/.gitignore',
            'myproject/.env.example',
            'myproject/src/.hidden/config.py'
        ])

        # Should not raise (. prefix alone is safe)
        result = self.service.import_from_zip(zip_data, 'hidden_files.zip')
        self.assertIsNotNone(result)


class TestGitUrlValidation(unittest.TestCase):
    """Test Git URL validation to prevent SSRF attacks"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.service = ProjectService(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # Valid URLs
    def test_valid_https_github_url(self):
        """Valid HTTPS GitHub URL should not raise"""
        self.service._validate_git_url('https://github.com/user/repo.git')

    def test_valid_https_gitlab_url(self):
        """Valid HTTPS GitLab URL should not raise"""
        self.service._validate_git_url('https://gitlab.com/user/repo.git')

    def test_valid_https_bitbucket_url(self):
        """Valid HTTPS Bitbucket URL should not raise"""
        self.service._validate_git_url('https://bitbucket.org/user/repo.git')

    def test_valid_https_custom_domain(self):
        """Valid HTTPS URL with custom domain should not raise"""
        self.service._validate_git_url('https://git.company.com/team/project.git')

    def test_valid_https_url_no_git_extension(self):
        """Valid HTTPS URL without .git extension should not raise"""
        self.service._validate_git_url('https://github.com/user/repo')

    # Invalid protocols
    def test_invalid_http_protocol(self):
        """HTTP URL should be rejected (only HTTPS allowed)"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_git_url('http://github.com/user/repo.git')
        self.assertIn('HTTPS', str(cm.exception))

    def test_invalid_git_protocol(self):
        """git:// protocol should be rejected"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_git_url('git://github.com/user/repo.git')
        self.assertIn('HTTPS', str(cm.exception))

    def test_invalid_ssh_protocol(self):
        """SSH protocol should be rejected"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_git_url('ssh://git@github.com/user/repo.git')
        self.assertIn('HTTPS', str(cm.exception))

    def test_invalid_git_ssh_format(self):
        """git@host:path SSH format should be rejected"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_git_url('git@github.com:user/repo.git')
        # This might pass URL parsing, so check protocol or reject in validation
        self.assertTrue('HTTPS' in str(cm.exception) or 'Invalid URL' in str(cm.exception))

    def test_invalid_file_protocol(self):
        """file:// protocol should be rejected (local file access)"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_git_url('file:///var/repos/malicious.git')
        self.assertIn('HTTPS', str(cm.exception))

    def test_invalid_ftp_protocol(self):
        """ftp:// protocol should be rejected"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_git_url('ftp://server.com/repo.git')
        self.assertIn('HTTPS', str(cm.exception))

    # SSRF attack vectors
    def test_invalid_localhost_url(self):
        """localhost URL should work (validation allows any HTTPS)"""
        # Note: If you uncomment the allowlist in _validate_git_url, this should fail
        # For now, it passes because only protocol is checked
        self.service._validate_git_url('https://localhost/repo.git')

    def test_invalid_internal_ip(self):
        """Internal IP URL should work (validation allows any HTTPS)"""
        # Note: If you uncomment the allowlist in _validate_git_url, this should fail
        self.service._validate_git_url('https://192.168.1.1/repo.git')

    # Malformed URLs
    def test_invalid_empty_url(self):
        """Empty URL should be rejected"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_git_url('')
        self.assertIn('cannot be empty', str(cm.exception))

    def test_invalid_whitespace_url(self):
        """Whitespace-only URL should be rejected"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_git_url('   ')
        self.assertIn('cannot be empty', str(cm.exception))

    def test_invalid_no_hostname(self):
        """URL without hostname should be rejected"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_git_url('https:///repo.git')
        self.assertIn('hostname', str(cm.exception).lower())

    def test_invalid_malformed_url(self):
        """Malformed URL should be rejected"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_git_url('not-a-valid-url')
        # Should fail either on protocol check or URL parsing
        self.assertTrue('HTTPS' in str(cm.exception) or 'Invalid URL' in str(cm.exception))


if __name__ == '__main__':
    unittest.main()
