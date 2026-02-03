#!/usr/bin/env python3
"""
Test backend loading of project-level parameters and verbs.
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from project_manager.project_service import ProjectService
from model.script_config import ConfigModel
from utils.process_utils import ProcessInvoker


def test_project_metadata():
    """Test loading project metadata with parameters and verbs."""
    print("=" * 80)
    print("TEST 1: Load project metadata with parameters and verbs")
    print("=" * 80)

    project_service = ProjectService('.')
    project = project_service.get_project('gmail-trim-3')

    if not project:
        print("\n✗ FAILED: Project gmail-trim-3 not found")
        return False

    print(f"\n✓ Project loaded: {project['name']}")
    print(f"  ID: {project['id']}")
    print(f"  Import type: {project['import_type']}")

    # Check parameters
    parameters = project.get('parameters', [])
    print(f"\n✓ Parameters defined: {len(parameters)}")
    for param in parameters:
        print(f"  - {param['name']} ({param['type']}): {param.get('description', 'No description')}")
        if 'default' in param:
            print(f"    Default: {param['default']}")

    # Check verbs
    verbs = project.get('verbs')
    if verbs:
        print(f"\n✓ Verbs configured:")
        print(f"  Parameter name: {verbs['parameter_name']}")
        print(f"  Default: {verbs['default']}")
        print(f"  Required: {verbs.get('required', False)}")
        print(f"  Options: {len(verbs['options'])}")
        for verb in verbs['options']:
            print(f"\n    - {verb['name']}: {verb['label']}")
            print(f"      Description: {verb['description']}")
            print(f"      Parameters: {', '.join(verb['parameters'])}")
            if verb.get('required_parameters'):
                print(f"      Required: {', '.join(verb['required_parameters'])}")

    # Check shared parameters
    shared_params = project.get('shared_parameters', [])
    print(f"\n✓ Shared parameters: {', '.join(shared_params) if shared_params else 'None'}")

    return True


def test_instance_config(config_name):
    """Test loading an instance config."""
    print("\n" + "=" * 80)
    print(f"TEST 2: Load instance config - {config_name}")
    print("=" * 80)

    config_path = Path(f'conf/runners/{config_name}.json')
    if not config_path.exists():
        print(f"\n✗ FAILED: Config file not found: {config_path}")
        return False

    with open(config_path, 'r') as f:
        config_object = json.load(f)

    print(f"\n✓ Instance config loaded: {config_object['name']}")
    print(f"  Project ID: {config_object.get('project_id')}")

    instance_config = config_object.get('instance_config', {})
    print(f"\n✓ Instance configuration:")
    print(f"  Selected verb: {instance_config.get('selected_verb')}")
    print(f"  Included parameters: {', '.join(instance_config['included_parameters'])}")
    if instance_config['parameter_values']:
        print(f"  Parameter overrides:")
        for key, value in instance_config['parameter_values'].items():
            print(f"    - {key}: {value}")
    else:
        print(f"  Parameter overrides: None (using all defaults)")

    # Create ConfigModel to test parameter loading
    try:
        process_invoker = ProcessInvoker(env_vars={})
        config_model = ConfigModel(
            config_object=config_object,
            path=str(config_path),
            username='test_user',
            audit_name='Test User',
            group_by_folders=False,
            script_configs_folder='conf/runners',
            process_invoker=process_invoker,
            pty_enabled_default=True
        )

        print(f"\n✓ ConfigModel created:")
        print(f"  Name: {config_model.name}")
        print(f"  Parameters loaded: {len(config_model.parameters)}")

        # Check parameters
        print(f"\n✓ Parameter details:")
        for param in config_model.parameters:
            default_value = param._default
            print(f"  - {param.name} ({param.type})")
            print(f"    Default: {default_value}")
            print(f"    Required: {param.required}")
            if param.param:
                print(f"    CLI flag: {param.param}")

        # Check verbs
        if config_model.verbs_config and config_model.verbs_config.enabled:
            print(f"\n✓ Verb configuration:")
            print(f"  Enabled: {config_model.verbs_config.enabled}")
            print(f"  Parameter name: {config_model.verbs_config.parameter_name}")
            print(f"  Default verb: {config_model.verbs_config.default}")
            print(f"  Number of options: {len(config_model.verbs_config.options)}")

        return True

    except Exception as e:
        print(f"\n✗ FAILED to create ConfigModel: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("PROJECT-LEVEL PARAMETERS & VERBS - BACKEND TESTS")
    print("=" * 80 + "\n")

    success = True

    # Test 1: Project metadata
    if not test_project_metadata():
        success = False

    # Test 2: Instance configs
    for config_name in ['Gmail Trim A', 'Gmail Trim B', 'Gmail List Labels']:
        if not test_instance_config(config_name):
            success = False

    # Summary
    print("\n" + "=" * 80)
    if success:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 80 + "\n")

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
