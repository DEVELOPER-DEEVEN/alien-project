# network Parsing Tests

This directory contains tests for validating `Tasknetwork.from_json()` and `from_dict()` methods with real log data.

## Test Files

### 1. `test_network_parsing.py`
**Main test script** - Comprehensive test that validates parsing of `network_before` and `network_after` fields from response logs.

**Usage:**
```bash
python tests/cluster/network/test_network_parsing.py
```

**What it tests:**
- Parses each line in `logs/cluster/task_1/response.log`
- Tests both `network_before` and `network_after` fields
- Reports success/failure for each parsing attempt
- Provides detailed error messages

### 2. `test_network_parsing_debug.py`
**Debug utility** - Examines the structure of network JSON data to identify format issues.

**Usage:**
```bash
python tests/cluster/network/test_network_parsing_debug.py
```

**What it does:**
- Inspects JSON structure
- Identifies data type issues
- Validates JSON format
- Reports problematic fields

### 3. `test_network_tasks_debug.py`
**Detailed field inspector** - Focuses on debugging the `tasks` field specifically.

**Usage:**
```bash
python tests/cluster/network/test_network_tasks_debug.py
```

**What it does:**
- Examines the `tasks` field in detail
- Compares working vs broken examples
- Shows actual data types
- Identifies string vs dict issues

### 4. `test_network_summary.py`
**Comprehensive summary** - Provides a full analysis with examples and recommendations.

**Usage:**
```bash
python tests/cluster/network/test_network_summary.py
```

**What it provides:**
- Summary of all test results
- Root cause analysis
- Code examples showing the problem
- Recommendations for fixes

## Test Data

These tests use log data from:
```
logs/cluster/task_1/response.log
```

This is a JSONL (JSON Lines) file where each line contains a response log entry with:
- `network_before`: State before modification
- `network_after`: State after modification

## Known Issues

### Issue: String Representation in Tasks Field

**Problem:** Some `network_before` entries contain malformed data where the `tasks` field is a Python string representation instead of a proper JSON object.

**Example of broken data:**
```json
{
  "tasks": "{'t1': {'task_id': 't1', ...}}"  // WRONG - Python str
}
```

**Example of correct data:**
```json
{
  "tasks": {"t1": {"task_id": "t1", ...}}   // CORRECT - JSON object
}
```

**Root Cause:** The logging code is using `str()` or `repr()` instead of `json.dumps()` when serializing the network.

**Fix:** Update the code that generates `network_before` to use proper JSON serialization.

## Test Results Summary

Based on the last test run with `logs/cluster/task_1/response.log`:

| Field | Success Rate | Notes |
|-------|-------------|-------|
| `network_after` | 80% (4/5) | Line 5 failed |
| `network_before` | 0% (0/4) | All failed due to string repr in tasks field |
| **Overall** | 44.4% (4/9) | See detailed report in `docs/network_PARSING_TEST_REPORT.md` |

## Related Documentation

- Full test report: `docs/network_PARSING_TEST_REPORT.md`
- Tasknetwork implementation: `cluster/network/task_network.py`

## Running All Tests

### Quick Start - Run All Tests

```bash
# Activate virtual environment
.\scripts\activate.ps1

# Run all tests in sequence
python tests/cluster/network/run_all_tests.py
```

### Run Individual Tests

```bash
# Activate virtual environment
.\scripts\activate.ps1

# Run main test
python tests/cluster/network/test_network_parsing.py

# Run debug tests if issues found
python tests/cluster/network/test_network_parsing_debug.py
python tests/cluster/network/test_network_tasks_debug.py

# Run comprehensive summary
python tests/cluster/network/test_network_summary.py
```

## Expected Output

When tests pass:
```
✓ Successfully parsed network_after
  - network ID: network_2753954b_20251021_180630
  - Tasks: 5
  - Dependencies: 4
  - State: created
```

When tests fail:
```
✗ Failed to parse network_before: AttributeError: 'str' object has no attribute 'items'
```
