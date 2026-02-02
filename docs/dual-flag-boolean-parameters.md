# Dual-Flag Boolean Parameters

## Overview

Dual-flag boolean parameters allow you to specify different command-line flags for `true` and `false` values, enabling CLI patterns like:

- `--verbose` (if true) / `--quiet` (if false)
- `--enable-cache` (if true) / `--disable-cache` (if false)
- `--color` (if true) / `--no-color` (if false)

## Use Cases

This feature is useful when:
1. Your script uses opposing flag patterns (enable/disable, verbose/quiet, etc.)
2. You want explicit flags for both states rather than a single flag with a value
3. You're wrapping existing CLI tools that use dual-flag patterns

## Configuration

### Basic Structure

```json
{
  "name": "verbosity",
  "description": "Control output verbosity",
  "type": "list",
  "values": ["true", "false"],
  "dual_flags": true,
  "param_true": "--verbose",
  "param_false": "--quiet",
  "default": "false"
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Must be `"list"` |
| `values` | array | Must be `["true", "false"]` |
| `dual_flags` | boolean | Set to `true` to enable dual-flag mode |
| `param_true` | string | Flag to use when value is true |
| `param_false` | string | Flag to use when value is false |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `default` | string | Default value: `"true"` or `"false"` |
| `required` | boolean | Whether parameter is required |
| `description` | string | Help text for users |

## Behavior

### Command-Line Generation

**When user selects `true`:**
```bash
script.sh --verbose
```

**When user selects `false`:**
```bash
script.sh --quiet
```

### Comparison with Regular Boolean

**Regular boolean (single flag with value):**
```json
{
  "name": "enabled",
  "type": "list",
  "values": ["true", "false"],
  "param": "--enabled"
}
```
Generates: `--enabled true` or `--enabled false`

**Dual-flag boolean:**
```json
{
  "name": "enabled",
  "type": "list",
  "values": ["true", "false"],
  "dual_flags": true,
  "param_true": "--enable",
  "param_false": "--disable"
}
```
Generates: `--enable` or `--disable`

## UI Behavior

In the admin interface, when editing a boolean parameter:

1. **Flag mode selection:**
   - Single flag with value (default)
   - Dual flags (different flags for true/false)

2. **Single flag mode:**
   - Shows "Param" field for the flag name
   - "Combine param with value" checkbox available

3. **Dual flags mode:**
   - Shows "Flag if true" and "Flag if false" fields
   - "Combine param with value" checkbox is disabled (not applicable)

## Complete Example

```json
{
  "name": "Dual Flag Demo",
  "script_path": "scripts/demo.sh",
  "parameters": [
    {
      "name": "verbosity",
      "description": "Control output verbosity",
      "type": "list",
      "values": ["true", "false"],
      "dual_flags": true,
      "param_true": "--verbose",
      "param_false": "--quiet",
      "default": "false"
    },
    {
      "name": "cache",
      "description": "Enable or disable caching",
      "type": "list",
      "values": ["true", "false"],
      "dual_flags": true,
      "param_true": "--enable-cache",
      "param_false": "--disable-cache",
      "default": "true"
    }
  ]
}
```

**Execution with `verbosity=true` and `cache=false`:**
```bash
scripts/demo.sh --verbose --disable-cache
```

## Backward Compatibility

- Existing boolean parameters (without `dual_flags`) continue to work as before
- When loading old configs, they default to single-flag mode
- Setting `dual_flags: false` or omitting it uses traditional behavior

## Validation

The server validates that:
1. When `dual_flags: true`, both `param_true` and `param_false` are provided
2. The parameter type is `list` with values `["true", "false"]`
3. Values are converted to boolean using standard truthiness rules

## Implementation Details

### Backend

- **Parameter Model** (`src/model/parameter_config.py`):
  - Added `dual_flags`, `param_true`, `param_false` fields
  - Validates dual-flag configuration on load

- **Executor** (`src/execution/executor.py`):
  - `_build_param_args()` checks for `dual_flags` first
  - Uses `param_true` or `param_false` based on boolean value
  - Skips value passing (just adds the flag)

### Frontend

- **Parameter Form** (`web-src/src/admin/components/scripts-config/ParameterConfigForm.vue`):
  - Added "Boolean flag mode" radio buttons for bool type
  - Shows dual-flag input fields when mode is "dual"
  - Disables "Combine param with value" in dual-flag mode
  - Serializes to backend with `dual_flags`, `param_true`, `param_false`

## Migration from Regular Boolean

To convert a regular boolean to dual-flag:

**Before:**
```json
{
  "name": "verbose",
  "type": "list",
  "values": ["true", "false"],
  "param": "--verbose"
}
```

**After:**
```json
{
  "name": "verbose",
  "type": "list",
  "values": ["true", "false"],
  "dual_flags": true,
  "param_true": "--verbose",
  "param_false": "--quiet"
}
```

The UI will automatically detect and display this correctly when editing the parameter.
