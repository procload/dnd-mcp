# D&D Knowledge Navigator Package Structure

This document provides a comprehensive overview of the D&D Knowledge Navigator package structure and organization.

## Overview

The D&D Knowledge Navigator is organized as a Python package following standard Python packaging conventions. This structure makes it easy to install, distribute, and maintain the codebase.

## Directory Structure

```
dnd-knowledge-navigator/
├── dnd_mcp_server.py      # Main server entry point
├── run_tests.py           # Script to run all tests
├── setup.py               # Package installation configuration
├── test_package.py        # Script to test package imports
├── src/                   # Source code directory
│   ├── __init__.py        # Package initialization
│   ├── README.md          # Source code documentation
│   ├── attribution/       # Source attribution system
│   │   ├── __init__.py
│   │   ├── citation.py    # Citation formatting
│   │   ├── confidence.py  # Confidence scoring
│   │   ├── core.py        # Core attribution classes
│   │   ├── formatters.py  # Attribution formatters
│   │   ├── source_tracking.py  # Source tracking
│   │   └── tool_tracking.py    # Tool usage tracking
│   ├── core/              # Core functionality
│   │   ├── __init__.py
│   │   ├── api_helpers.py # API interaction helpers
│   │   ├── cache.py       # Caching system
│   │   ├── formatters.py  # Response formatters
│   │   ├── prompts.py     # MCP prompts
│   │   ├── resources.py   # MCP resources
│   │   └── tools.py       # MCP tools
│   ├── query_enhancement/ # Query enhancement system
│   │   ├── __init__.py
│   │   ├── category_prioritization.py  # Category prioritization
│   │   ├── fuzzy_matching.py           # Fuzzy matching
│   │   ├── synonyms.py                 # Synonym expansion
│   │   └── tokenizer.py                # Special term tokenization
│   └── templates/         # Response formatting templates
│       ├── __init__.py
│       ├── config.py      # Template configuration
│       ├── equipment.py   # Equipment templates
│       ├── formatter.py   # Main formatter
│       ├── monster.py     # Monster templates
│       └── spell.py       # Spell templates
├── tests/                 # Test directory
│   ├── __init__.py        # Test package initialization
│   ├── README.md          # Test documentation
│   ├── test_attribution.py          # Attribution tests
│   ├── test_mcp_attribution.py      # MCP attribution tests
│   ├── test_query_enhancement.py    # Query enhancement tests
│   ├── test_search_enhancement.py   # Search enhancement tests
│   ├── test_template_integration.py # Template integration tests
│   └── test_templates.py            # Template tests
└── docs/                  # Documentation
    ├── architecture.md    # System architecture
    ├── example_queries.md # Example queries
    ├── plan.md            # Development plan
    ├── query_enhancement.md  # Query enhancement docs
    ├── source_attribution.md # Source attribution docs
    ├── todo.md            # Todo list
    ├── troubleshooting.md # Troubleshooting guide
    └── usage_guide.md     # Usage guide
```

## Key Components

### Main Server (`dnd_mcp_server.py`)

The main entry point for the D&D Knowledge Navigator server. It initializes the FastMCP server, sets up logging, and registers all the necessary components.

### Source Code (`src/`)

The source code is organized into several modules:

1. **Attribution System** (`src/attribution/`): Handles tracking and formatting of source attributions for D&D information.

2. **Core Functionality** (`src/core/`): Contains the core components of the system, including API helpers, caching, and MCP integration.

3. **Query Enhancement** (`src/query_enhancement/`): Improves search queries by handling synonyms, special terms, and fuzzy matching.

4. **Templates** (`src/templates/`): Formats responses for different types of D&D content (spells, monsters, equipment).

### Tests (`tests/`)

Contains unit tests and integration tests for all components of the system. The `run_tests.py` script in the root directory can be used to run all tests.

### Documentation (`docs/`)

Comprehensive documentation for the system, including architecture, usage guides, and development plans.

## Package Installation

The `setup.py` file allows the package to be installed using pip:

```bash
# Install in development mode
pip install -e .

# Install for regular use
pip install .
```

## Running the Server

To start the D&D Knowledge Navigator server:

```bash
python dnd_mcp_server.py
```

## Running Tests

To run all tests:

```bash
./run_tests.py
```

## Development Workflow

1. Make changes to the source code in the `src/` directory.
2. Write tests for new functionality in the `tests/` directory.
3. Run tests to ensure everything works correctly.
4. Update documentation as needed.
5. Run the server to test the changes in action.

## Conclusion

The D&D Knowledge Navigator package structure follows Python best practices and is designed to be modular, maintainable, and easy to understand. Each component has a specific responsibility, making it easier to extend and improve the system over time.
