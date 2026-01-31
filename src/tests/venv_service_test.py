import unittest
import tempfile
import shutil
from pathlib import Path

from venv_manager.venv_service import VenvService


class TestPackageNameValidation(unittest.TestCase):
    """Test package name validation to prevent command injection"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.service = VenvService(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # Valid package names
    def test_valid_package_name_simple(self):
        """Valid simple package name should not raise"""
        self.service._validate_package_name('requests')

    def test_valid_package_name_with_hyphen(self):
        """Valid package name with hyphen should not raise"""
        self.service._validate_package_name('django-rest-framework')

    def test_valid_package_name_with_underscore(self):
        """Valid package name with underscore should not raise"""
        self.service._validate_package_name('google_api_python_client')

    def test_valid_package_name_with_period(self):
        """Valid package name with period should not raise"""
        self.service._validate_package_name('zope.interface')

    def test_valid_package_name_mixed(self):
        """Valid package name with mixed valid characters should not raise"""
        self.service._validate_package_name('Py-Test_Utils.Core')

    # Invalid package names - pip option injection
    def test_invalid_package_name_starts_with_dash(self):
        """Package name starting with dash should raise (pip option injection)"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_package_name('--index-url=https://evil.com')
        self.assertIn('cannot start with "-"', str(cm.exception))

    def test_invalid_package_name_double_dash(self):
        """Package name with double dash should raise (pip option)"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_package_name('--no-deps')
        self.assertIn('cannot start with "-"', str(cm.exception))

    def test_invalid_package_name_single_dash_option(self):
        """Package name as single dash option should raise"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_package_name('-i')
        self.assertIn('cannot start with "-"', str(cm.exception))

    # Invalid package names - spaces (allow multiple arguments)
    def test_invalid_package_name_with_space(self):
        """Package name with space should raise (prevents multiple arguments)"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_package_name('requests malware')
        self.assertIn('cannot contain spaces', str(cm.exception))

    def test_invalid_package_name_with_tab(self):
        """Package name with special characters should raise"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_package_name('requests\tmalware')
        self.assertIn('Only alphanumerics', str(cm.exception))

    # Invalid package names - special characters
    def test_invalid_package_name_with_semicolon(self):
        """Package name with semicolon should raise"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_package_name('requests;malware')
        self.assertIn('Only alphanumerics', str(cm.exception))

    def test_invalid_package_name_with_ampersand(self):
        """Package name with ampersand should raise"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_package_name('requests&malware')
        self.assertIn('Only alphanumerics', str(cm.exception))

    def test_invalid_package_name_with_pipe(self):
        """Package name with pipe should raise"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_package_name('requests|malware')
        self.assertIn('Only alphanumerics', str(cm.exception))

    def test_invalid_package_name_with_backtick(self):
        """Package name with backtick should raise"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_package_name('requests`whoami`')
        self.assertIn('Only alphanumerics', str(cm.exception))

    # Edge cases
    def test_invalid_package_name_empty(self):
        """Empty package name should raise"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_package_name('')
        self.assertIn('cannot be empty', str(cm.exception))

    def test_invalid_package_name_whitespace(self):
        """Whitespace-only package name should raise"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_package_name('   ')
        self.assertIn('cannot be empty', str(cm.exception))


class TestVersionValidation(unittest.TestCase):
    """Test version string validation to prevent command injection"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.service = VenvService(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # Valid versions
    def test_valid_version_simple(self):
        """Valid simple version should not raise"""
        self.service._validate_version('1.0.0')

    def test_valid_version_with_prerelease(self):
        """Valid version with prerelease should not raise"""
        self.service._validate_version('1.0.0-alpha')

    def test_valid_version_with_build(self):
        """Valid version with build metadata should not raise"""
        self.service._validate_version('1.0.0+build123')

    def test_valid_version_complex(self):
        """Valid complex version should not raise"""
        self.service._validate_version('2.1.3-rc1+build.456')

    def test_valid_version_with_underscore(self):
        """Valid version with underscore should not raise"""
        self.service._validate_version('1.0_alpha')

    def test_valid_version_none(self):
        """None version (optional) should not raise"""
        self.service._validate_version(None)

    def test_valid_version_empty(self):
        """Empty version (optional) should not raise"""
        self.service._validate_version('')

    # Invalid versions
    def test_invalid_version_with_space(self):
        """Version with space should raise"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_version('1.0 malicious')
        self.assertIn('Invalid version', str(cm.exception))

    def test_invalid_version_starts_with_dash(self):
        """Version starting with dash should raise (pip option)"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_version('--upgrade')
        self.assertIn('Invalid version', str(cm.exception))

    def test_invalid_version_with_semicolon(self):
        """Version with semicolon should raise"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_version('1.0;malicious')
        self.assertIn('Only alphanumerics', str(cm.exception))

    def test_invalid_version_with_slash(self):
        """Version with slash should raise"""
        with self.assertRaises(ValueError) as cm:
            self.service._validate_version('1.0/malicious')
        self.assertIn('Only alphanumerics', str(cm.exception))


class TestInstallPackageValidation(unittest.TestCase):
    """Test that install_package uses validation"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.service = VenvService(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_install_package_validates_package_name(self):
        """install_package should validate package name"""
        with self.assertRaises(ValueError) as cm:
            self.service.install_package('--index-url=https://evil.com')
        self.assertIn('cannot start with "-"', str(cm.exception))

    def test_install_package_validates_version(self):
        """install_package should validate version"""
        with self.assertRaises(ValueError) as cm:
            self.service.install_package('requests', '--upgrade')
        self.assertIn('Invalid version', str(cm.exception))

    def test_install_package_strips_whitespace(self):
        """install_package should strip whitespace before validation"""
        with self.assertRaises(ValueError) as cm:
            self.service.install_package('  --malicious  ')
        self.assertIn('cannot start with "-"', str(cm.exception))


class TestUninstallPackageValidation(unittest.TestCase):
    """Test that uninstall_package uses validation"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.service = VenvService(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_uninstall_package_validates_package_name(self):
        """uninstall_package should validate package name"""
        with self.assertRaises(ValueError) as cm:
            self.service.uninstall_package('--yes malware')
        self.assertIn('cannot start with "-"', str(cm.exception))

    def test_uninstall_package_rejects_spaces(self):
        """uninstall_package should reject package names with spaces"""
        with self.assertRaises(ValueError) as cm:
            self.service.uninstall_package('package malware')
        self.assertIn('cannot contain spaces', str(cm.exception))


if __name__ == '__main__':
    unittest.main()
