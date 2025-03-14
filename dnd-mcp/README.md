# D&D MCP Server

A Python-based server implementing the Model Context Protocol (MCP) that connects Claude and other AI assistants to Dungeons & Dragons 5e game information.

## What is MCP?

The Model Context Protocol (MCP) is a framework developed by Anthropic that enables AI assistants like Claude to communicate with external tools and services. This server leverages FastMCP, Anthropic's Python implementation of the protocol, to create a structured bridge between AI assistants and the D&D 5e API.

## Features

- **FastMCP Integration**: Provides AI assistants with tools and resources to query D&D game data
- **D&D 5e API Integration**: Complete access to spells, monsters, equipment, classes, races, and more
- **Efficient Caching**: Persistent local storage of API responses for improved performance
- **Structured Data Access**: Well-defined resources and tools for consistent AI interactions
- **Source Attribution**: Comprehensive tracking and display of information sources
- **Visual Formatting**: Markdown templates for beautiful presentation of D&D content
- **Query Enhancement**: Intelligent processing of D&D queries with synonym handling and fuzzy matching

## Setup

1. Install dependencies:

   ```
   uv pip install -r requirements.txt
   ```

   or

   ```
   pip install .
   ```

2. Run the server:
   ```
   uv run python dnd_mcp_server.py
   ```

## MCP Tool Usage

When connected to an AI assistant, the following tools are available:

- `search_all_categories`: Search across all D&D resources for specific terms
- `verify_with_api`: Verify D&D statements against official API data
- `check_api_health`: Check the health and status of the D&D 5e API

## Source Attribution System

The server includes a comprehensive source attribution system that:

- Tracks the source of all information returned to the user
- Provides confidence levels for each piece of information
- Includes API endpoints and relevance scores
- Formats attribution information for clear presentation

## Template System

The server includes a template system for formatting D&D content:

- Monster stat blocks with organized attributes and abilities
- Spell descriptions with formatted components and effects
- Equipment details with organized properties
- Configurable formatting options (tables, emojis, compact mode)

To disable templates, set `TEMPLATES_ENABLED = False` in `src/templates/config.py`.

## Query Enhancement System

The server includes a query enhancement system that improves search results:

- Synonym handling for D&D terminology (e.g., "AC" → "armor class")
- Special term recognition for game-specific notation (e.g., "2d6+3", "STR save")
- Fuzzy matching for common misspellings (e.g., "firball" → "fireball")
- Category prioritization to focus searches on relevant content

To disable query enhancement, set parameters in the `enhance_query` function to `False`.

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- [Usage Guide](docs/usage_guide.md): How to use the D&D Knowledge Navigator with Claude Desktop
- [Example Queries](docs/example_queries.md): Sample queries and expected responses
- [Troubleshooting Guide](docs/troubleshooting.md): Solutions for common issues
- [Source Attribution](docs/source_attribution.md): Details about the attribution system
- [Query Enhancement](docs/query_enhancement.md): Information about the query enhancement system

## Cached Resources

The server maintains a local cache in the `cache/` directory to minimize API calls and improve response time.

## Configuration

Edit `prompts.py` to modify or add new prompt templates, or `resources.py` to adjust resource endpoints.
