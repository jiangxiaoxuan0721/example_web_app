# MCP Tools Test Suite

Comprehensive test suite for MCP tools functionality.

## Prerequisites

1. Backend server must be running on `http://localhost:8001`
2. Install dependencies:
   ```bash
   pip install -r tests/requirements.txt
   ```

## Running Tests

### Run all tests
```bash
pytest tests/test_mcp_tools.py -v
```

### Run specific test classes
```bash
pytest tests/test_mcp_tools.py::TestFieldOperations -v
pytest tests/test_mcp_tools.py::TestBlockOperations -v
pytest tests/test_mcp_tools.py::TestActionOperations -v
pytest tests/test_mcp_tools.py::TestPatchUIState -v
pytest tests/test_mcp_tools.py::TestSchemaOperations -v
pytest tests/test_mcp_tools.py::TestValidation -v
pytest tests/test_mcp_tools.py::TestEdgeCases -v
pytest tests/test_mcp_tools.py::TestComplexScenarios -v
```

### Run specific test methods
```bash
pytest tests/test_mcp_tools.py::TestFieldOperations::test_add_text_field -v
pytest tests/test_mcp_tools.py::TestActionOperations::test_add_global_action_set -v
```

### Run with detailed output
```bash
pytest tests/test_mcp_tools.py -v -s
```

## Test Coverage

### TestFieldOperations (17 tests)
- Testing all 17 field types:
  - Input fields: text, number, textarea, checkbox, json
  - Selection fields: select, radio, multiselect
  - Display fields: html, image, tag, progress, badge, table, modal
- Update field properties (label, type, multiple properties)
- Remove field (single and all matching)

### TestBlockOperations (7 tests)
- Add form blocks (at end, start, specific index)
- Add display blocks
- Add blocks with actions
- Remove blocks (single and all matching)

### TestActionOperations (13 tests)
- Global actions with different handlers:
  - set, increment, decrement, toggle, template
  - navigate
  - append_to_list, update_list_item operations
- Block-level actions
- Remove actions (global, block-level, all matching)

### TestPatchUIState (14 tests)
- Set state values (single and multiple)
- Add/update/remove fields via patch
- Add/remove blocks via patch
- Add/remove actions via patch
- Create/delete instances
- Batch operations

### TestSchemaOperations (8 tests)
- Get schema (default and specific instance)
- Validate schema structure
- List instances
- Access instances

### TestValidation (7 tests)
- Validate field existence
- Validate field values
- Validate block count
- Validate action existence
- Validate multiple criteria
- Validate custom conditions
- Get recommendations

### TestEdgeCases (10 tests)
- Empty patches array
- Invalid instance IDs
- Update/remove non-existent fields
- Invalid block indices
- Remove non-existent blocks
- Invalid block positions
- Mixed operations in single patch

### TestComplexScenarios (3 tests)
- Create form with validation
- Dynamic table management
- Template rendering with timestamps

## Test Statistics

- Total test cases: ~79 tests
- Coverage: All 12 MCP tools
- Field types: All 17 types tested
- Handler types: All 9 types tested
- Operations: set, add, remove, insert, create, delete tested

## Notes

- Tests require backend server to be running
- Some tests create temporary instances that are cleaned up
- Tests are independent and can be run in any order
- Use `-v` flag for verbose output
- Use `-s` flag to see print statements
