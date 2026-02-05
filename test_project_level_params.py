#!/usr/bin/env python3
"""
Test script for project-level parameters backend.
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from project_manager.project_service import ProjectService
from model.script_config import ConfigModel
from utils.process_utils import ProcessInvoker

def test_project_service():
    """Test ProjectService methods for parameters and verbs."""
    print("=" * 80)
    print("TEST 1: ProjectService - Load project metadata")
    print("=" * 80)

    project_service = ProjectService('.')
    project = project_service.get_project('gmail-trim-3')

    print(f"\n✓ Project loaded: {project['name']}")
    print(f"  ID: {project['id']}")
    print(f"  Import type: {project['import_type']}")

    # Check parameters
    parameters = project.get('parameters', [])
    print(f"\n✓ Parameters defined: {len(parameters)}")
    for param in parameters:
        print(f"  - {param['name']} ({param['type']}): {param.get('description', 'No description')}")

    # Check verbs
    verbs = project.get('verbs')
    if verbs:
        print(f"\n✓ Verbs configured:")
        print(f"  Parameter name: {verbs['parameter_name']}")
        print(f"  Default: {verbs['default']}")
        print(f"  Options: {len(verbs['options'])}")
        for verb in verbs['options']:
            print(f"    - {verb['name']}: {verb['label']}")
            print(f"      Parameters: {', '.join(verb['parameters'])}")

    # Check shared parameters
    shared_params = project.get('shared_parameters', [])
    print(f"\n✓ Shared parameters: {', '.join(shared_params) if shared_params else 'None'}")

    return True

def test_config_loading():
    """Test ConfigModel loading from project."""
    print("\n" + "=" * 80)
    print("TEST 2: ConfigModel - Load instance config with project_id")
    print("=" * 80)

    # Load the test instance config
    config_path = Path('conf/runners/Gmail Trim Test Instance.json')
    with open(config_path, 'r') as f:
        config_object = json.load(f)

    print(f"\n✓ Instance config loaded: {config_object['name']}")
    print(f"  Project ID: {config_object.get('project_id')}")

    instance_config = config_object.get('instance_config', {})
    print(f"\n✓ Instance configuration:")
    print(f"  Included parameters: {', '.join(instance_config['included_parameters'])}")
    print(f"  Parameter values: {json.dumps(instance_config['parameter_values'], indent=4)}")
    print(f"  Selected verb: {instance_config.get('selected_verb')}")

    # Create ConfigModel
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
        print(f"    Param flag: {param.param}")

    # Check verbs
    if config_model.verbs_config and config_model.verbs_config.enabled:
        print(f"\n✓ Verbs configuration:")
        print(f"  Enabled: {config_model.verbs_config.enabled}")
        print(f"  Parameter name: {config_model.verbs_config.parameter_name}")
        print(f"  Default verb: {config_model.verbs_config.default}")
        print(f"  Number of verbs: {len(config_model.verbs_config.options)}")

        # Check selected verb
        verb_param_name = config_model.verbs_config.parameter_name
        if verb_param_name in config_model.parameter_values:
            verb_value = config_model.parameter_values[verb_param_name]
            print(f"  Selected verb: {verb_value.user_value if hasattr(verb_value, 'user_value') else verb_value}")

    # Check parameter values
    print(f"\n✓ Parameter values:")
    for param_name, value_wrapper in config_model.parameter_values.items():
        if hasattr(value_wrapper, 'user_value'):
            print(f"  {param_name}: {value_wrapper.user_value}")
        else:
            print(f"  {param_name}: {value_wrapper}")

    return True

def test_parameter_filtering():
    """Test that only included parameters are loaded."""
    print("\n" + "=" * 80)
    print("TEST 3: Parameter Filtering - Verify only included params loaded")
    print("=" * 80)

    # Load config
    config_path = Path('conf/runners/Gmail Trim Test Instance.json')
    with open(config_path, 'r') as f:
        config_object = json.load(f)

    instance_config = config_object.get('instance_config', {})
    included_params = set(instance_config['included_parameters'])

    # Load project to get all available parameters
    project_service = ProjectService('.')
    project = project_service.get_project('gmail-trim-3')
    all_params = {p['name'] for p in project.get('parameters', [])}

    print(f"\n✓ All parameters in project: {', '.join(sorted(all_params))}")
    print(f"✓ Included in instance: {', '.join(sorted(included_params))}")

    excluded_params = all_params - included_params
    print(f"✓ Excluded from instance: {', '.join(sorted(excluded_params)) if excluded_params else 'None'}")

    # Load ConfigModel and verify
    process_invoker = ProcessInvoker(env_vars={})
    config_model = ConfigModel(
        config_object=config_object,
        path=str(config_path),
        username='test_user',
        audit_name='Test User',
        group_by_folders=False,
        script_configs_folder='conf/runners',
        process_invoker=process_invoker
    )

    loaded_params = {p.name for p in config_model.parameters}
    print(f"\n✓ Parameters loaded in ConfigModel: {', '.join(sorted(loaded_params))}")

    # Verify filtering worked
    if loaded_params == included_params:
        print(f"\n✅ PASS: Parameter filtering works correctly!")
        print(f"   Only included parameters were loaded.")
    else:
        unexpected = loaded_params - included_params
        missing = included_params - loaded_params
        print(f"\n❌ FAIL: Parameter filtering incorrect!")
        if unexpected:
            print(f"   Unexpected parameters: {', '.join(unexpected)}")
        if missing:
            print(f"   Missing parameters: {', '.join(missing)}")
        return False

    return True

def test_value_overrides():
    """Test that instance parameter values override defaults."""
    print("\n" + "=" * 80)
    print("TEST 4: Value Overrides - Verify instance values override defaults")
    print("=" * 80)

    # Load config
    config_path = Path('conf/runners/Gmail Trim Test Instance.json')
    with open(config_path, 'r') as f:
        config_object = json.load(f)

    instance_values = config_object['instance_config']['parameter_values']
    print(f"\n✓ Instance value overrides: {json.dumps(instance_values, indent=2)}")

    # Load ConfigModel
    process_invoker = ProcessInvoker(env_vars={})
    config_model = ConfigModel(
        config_object=config_object,
        path=str(config_path),
        username='test_user',
        audit_name='Test User',
        group_by_folders=False,
        script_configs_folder='conf/runners',
        process_invoker=process_invoker
    )

    print(f"\n✓ Checking parameter defaults:")
    all_correct = True

    for param in config_model.parameters:
        expected_default = instance_values.get(param.name, param._original_config.get('default'))
        actual_default = param._default

        match_status = "✓" if actual_default == expected_default else "✗"
        print(f"  {match_status} {param.name}: {actual_default} (expected: {expected_default})")

        if actual_default != expected_default:
            all_correct = False

    if all_correct:
        print(f"\n✅ PASS: All value overrides applied correctly!")
    else:
        print(f"\n❌ FAIL: Some value overrides were not applied!")
        return False

    return True

def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "PROJECT-LEVEL PARAMETERS BACKEND TEST" + " " * 21 + "║")
    print("╚" + "=" * 78 + "╝")

    tests = [
        ("ProjectService", test_project_service),
        ("ConfigModel Loading", test_config_loading),
        ("Parameter Filtering", test_parameter_filtering),
        ("Value Overrides", test_value_overrides)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False, str(e)))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, passed, error in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if error:
            print(f"       Error: {error}")

    total_tests = len(results)
    passed_tests = sum(1 for _, passed, _ in results if passed)

    print(f"\n{passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Backend implementation is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Review output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
