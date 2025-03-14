# D&D Knowledge Navigator Tests

This directory contains tests for the D&D Knowledge Navigator.

## Running Tests

You can run all tests using the `run_tests.py` script in the root directory:

```bash
./run_tests.py
```

Or run individual tests:

```bash
python -m unittest tests/test_attribution.py
```

## Test Files

- `test_attribution.py`: Tests for the source attribution system
- `test_mcp_attribution.py`: Tests for MCP integration with attribution
- `test_query_enhancement.py`: Tests for the query enhancement system
- `test_search_enhancement.py`: Tests for search enhancement integration
- `test_template_integration.py`: Tests for template system integration
- `test_templates.py`: Tests for the template system
