"""
Script Validation Service
Validates script configurations by checking if script files exist.
"""
import json
import logging
import os
from pathlib import Path
from typing import Dict, List

LOGGER = logging.getLogger('script_server.ScriptValidator')


class ScriptValidator:
    """Validates script configurations"""

    def __init__(self):
        self.validation_cache = {}  # script_name -> validation_result

    def _extract_script_path(self, script_path: str) -> str:
        """
        Extract the actual script file path from a command string.

        script_path can be:
        - Just a script: /path/to/script.sh
        - Python command: /path/to/python /path/to/script.py
        - Other interpreter: /usr/bin/bash /path/to/script.sh

        Returns the actual script file path to validate.
        """
        if not script_path or not script_path.strip():
            return script_path

        parts = script_path.split()
        if len(parts) == 1:
            # Single path - this is the script
            return parts[0]

        # Multiple parts - likely "interpreter script args..."
        # Check if first part looks like a Python interpreter
        first = parts[0]
        if 'python' in first.lower() or first.endswith('/python3') or first.endswith('/python'):
            # Python interpreter - second part should be the script
            if len(parts) >= 2:
                return parts[1]

        # For other cases, assume first part is the script
        # (e.g., /path/to/script.sh --args or bash /path/to/script.sh)
        # Check if first part is an interpreter (bash, sh, etc.)
        if first.endswith('/bash') or first.endswith('/sh') or first in ['bash', 'sh']:
            if len(parts) >= 2:
                return parts[1]

        # Default: first part is the script
        return parts[0]

    def validate_script(self, script_name: str, script_path: str, working_dir: str = None) -> Dict:
        """
        Validate a single script configuration.

        Args:
            script_name: Name of the script
            script_path: Command to run the script (may include interpreter)
            working_dir: Working directory for the script

        Returns:
            Dict with 'valid' (bool), 'error' (str or None), 'warning' (str or None)
        """
        result = {
            'valid': True,
            'error': None,
            'warning': None
        }

        # Check if script file exists
        if not script_path:
            result['valid'] = False
            result['error'] = 'No script path configured'
            self.validation_cache[script_name] = result
            LOGGER.info(f'Cached validation for "{script_name}": valid={result["valid"]}, cache_size={len(self.validation_cache)}')
            return result

        # Extract actual script file path from command
        actual_script_path = self._extract_script_path(script_path)

        # Handle relative paths
        if not os.path.isabs(actual_script_path):
            # Try relative to working_dir first
            if working_dir and os.path.isabs(working_dir):
                full_path = os.path.join(working_dir, actual_script_path)
                if os.path.isfile(full_path):
                    actual_script_path = full_path
            # If not found, it will be checked as-is below

        # Check if file exists
        if not os.path.isfile(actual_script_path):
            result['valid'] = False
            result['error'] = f'Script file not found: {actual_script_path}'
            self.validation_cache[script_name] = result
            LOGGER.info(f'Cached validation for "{script_name}": valid={result["valid"]}, cache_size={len(self.validation_cache)}')
            return result

        # Check if file is readable
        if not os.access(actual_script_path, os.R_OK):
            result['valid'] = False
            result['error'] = f'Script file not readable: {actual_script_path}'
            self.validation_cache[script_name] = result
            LOGGER.info(f'Cached validation for "{script_name}": valid={result["valid"]}, cache_size={len(self.validation_cache)}')
            return result

        # Store in cache (for valid scripts)
        self.validation_cache[script_name] = result
        LOGGER.info(f'Cached validation for "{script_name}": valid={result["valid"]}, cache_size={len(self.validation_cache)}')
        return result

    def validate_all_scripts(self, script_configs: List) -> Dict[str, Dict]:
        """
        Validate all script configurations.

        Args:
            script_configs: List of script config objects (can be ShortConfig or full Config)

        Returns:
            Dict mapping script_name -> validation_result
        """
        results = {}

        for config in script_configs:
            script_name = getattr(config, 'name', None)

            # Try to get script_command (full config) or script_path (might be in config)
            script_path = getattr(config, 'script_command', None)
            if not script_path:
                # For ShortConfig, try to load from the actual config file
                # Skip validation for short configs - they'll be validated on full load
                continue

            working_dir = getattr(config, 'working_directory', None)

            if script_name:
                result = self.validate_script(script_name, script_path, working_dir)
                results[script_name] = result

                if not result['valid']:
                    LOGGER.warning(f"Script validation failed for '{script_name}': {result['error']}")

        return results

    def get_validation_status(self, script_name: str) -> Dict:
        """Get cached validation status for a script"""
        result = self.validation_cache.get(script_name, {
            'valid': True,
            'error': None,
            'warning': None
        })
        in_cache = script_name in self.validation_cache
        LOGGER.debug(f'get_validation_status("{script_name}"): in_cache={in_cache}, valid={result["valid"]}, cache_size={len(self.validation_cache)}')
        return result

    def validate_from_config_folder(self, config_folder: str) -> Dict[str, Dict]:
        """
        Validate all scripts by reading config files directly from folder.

        Args:
            config_folder: Path to conf/runners directory

        Returns:
            Dict mapping script_name -> validation_result
        """
        results = {}
        config_path = Path(config_folder)

        if not config_path.exists():
            LOGGER.warning(f'Config folder not found: {config_folder}')
            return results

        # Find all .json files
        for json_file in config_path.glob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    config_json = json.load(f)

                script_name = config_json.get('name', json_file.stem)
                script_path = config_json.get('script_path')
                working_dir = config_json.get('working_directory')

                result = self.validate_script(script_name, script_path, working_dir)
                results[script_name] = result

                if not result['valid']:
                    LOGGER.debug(f"Script validation failed for '{script_name}': {result['error']}")

            except Exception as e:
                LOGGER.debug(f"Could not validate {json_file.name}: {e}")

        return results

    def clear_cache(self):
        """Clear validation cache"""
        self.validation_cache.clear()
