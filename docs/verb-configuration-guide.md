# Verb Configuration Guide

## Overview

Verbs allow scripts to have multiple subcommands (like `git clone`, `docker run`, etc.). This guide explains how to configure verbs in the Project Config Modal.

---

## Verb Option Configuration

Each verb option has:

### 1. **Verb Name** (Value)
- **What it is:** The actual value passed to your script
- **Example:** `list`, `create`, `delete`
- **Used in:** Command line as the verb value

### 2. **Label** (Display Text)
- **What it is:** The text shown in the UI dropdown
- **Example:** `List Items`, `Create Item`, `Delete Item`
- **Used in:** User interface only

### 3. **Description**
- **What it is:** Help text shown when user selects this verb
- **Example:** `List all items with optional filtering`

---

## Verb Configuration (How Verbs Are Passed)

At the bottom of the Verbs tab, you configure HOW the verb parameter is passed:

### Parameter Name
- **Default:** `verb`
- **Purpose:** Internal parameter name
- **Example:** If set to `command`, the verb becomes the "command" parameter

### Pass As (Dropdown)

Choose how the verb value is passed on the command line:

#### 1. **Flag with value** (Default)
```bash
script.py --command list
script.py --verb create
```
- CLI Flag field: `--command` or `--verb`
- Verb value passed as argument to the flag

#### 2. **Positional**
```bash
script.py list
script.py create
```
- Verb value passed as first positional argument
- CLI Flag field: Leave empty or will be ignored

#### 3. **Long option with =**
```bash
script.py --command=list
script.py --verb=create
```
- CLI Flag field: Automatically set to `--command=` or `--verb=`
- Verb value passed after the equals sign
- Common in GNU-style command line tools

### CLI Flag
- **Purpose:** Specify the command line flag
- **Examples:**
  - `--command` → produces `--command list`
  - `-c` → produces `-c list`
  - `command=` → produces `command=list`
  - (empty) → produces `list` (positional)

### Flag Only
- **When checked:** Only the flag is passed, not the verb value
- **Example:** If checked with `--batch`, produces just `--batch` (no verb value)
- **Use case:** Rare - only if the verb parameter itself is a boolean flag

### Verb Required
- **When checked:** User must select a verb to execute the script
- **When unchecked:** Verb selection is optional

### Default Verb
- **Purpose:** Pre-select a verb in the UI
- **Options:** Dropdown shows all defined verb options
- **Example:** Set to "List Items" to have that verb selected by default

---

## Complete Example

### Configuration:
```
Parameter Name: command
Pass As: Flag with value
CLI Flag: --command
Default Verb: run
Verb Required: ✓ checked

Verb Options:
  1. Name: run, Label: Run Cleanup
  2. Name: auth, Label: Authenticate  
  3. Name: labels, Label: List Labels
```

### Results in:
```bash
# When user selects "Run Cleanup"
script.py --command run [other params...]

# When user selects "Authenticate"
script.py --command auth [other params...]

# When user selects "List Labels"
script.py --command labels [other params...]
```

---

## Common Patterns

### Git-style (positional)
```
Parameter Name: action
Pass As: Positional
CLI Flag: (empty)

Verbs: clone, pull, push, commit
Result: script.py clone [params...]
```

### Docker-style (positional)
```
Parameter Name: command  
Pass As: Positional
CLI Flag: (empty)

Verbs: run, build, ps, logs
Result: script.py run [params...]
```

### Traditional flags
```
Parameter Name: operation
Pass As: Flag with value
CLI Flag: --operation

Verbs: start, stop, restart
Result: script.py --operation start [params...]
```

### Long option with = style
```
Parameter Name: action
Pass As: Long option with =
CLI Flag: --action=

Verbs: list, create, delete
Result: script.py --action=list [params...]
```

---

## Tips

1. **Use Positional for CLI tools** - Most modern CLI tools use positional verbs (git, docker, kubectl)

2. **Use Flag with value for legacy scripts** - Older scripts often use `--command value` format

3. **Keep verb names short** - They're typed on command line, so `run` is better than `run-cleanup-process`

4. **Make labels descriptive** - Users see these in the UI, so `Run Cleanup Process` is clear

5. **Set a sensible default** - Most-used verb should be the default to save clicks

6. **Test the command** - After saving, create an instance and check the generated command in execution logs

---

## Troubleshooting

**Q: Verb value not appearing in command?**  
A: Check "Flag Only" is unchecked. If checked, only the flag is passed.

**Q: Getting `--verb verb` instead of `--verb list`?**  
A: The parameter_name is being used instead of the verb value. Check your backend script configuration.

**Q: Verb appears twice in command?**  
A: You might have both "Pass As: Positional" and "CLI Flag" set. Choose one.

**Q: Can't save - Save button disabled?**  
A: You need at least one verb option defined. Click "Add Verb Option" first.

---

**Updated:** 2026-02-02
