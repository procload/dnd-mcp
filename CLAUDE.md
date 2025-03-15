# DND-MCP Development Guide

## Commands
- Run server: `uv run python dnd_mcp_server.py`
- Run tests: `uv run python simple_fastmcp_test.py`
- Install dependencies: `uv pip install -r requirements.txt`

## Code Style
- **Imports**: Group imports: standard library, third-party, local
- **Formatting**: 4-space indentation, max line length ~100 chars
- **Types**: Use typing hints (`from typing import List, Dict, Any, Optional`)
- **Error handling**: Use try/except with specific exceptions and logging
- **Logging**: Use Python's logging module with appropriate levels
- **Documentation**: Docstrings for all functions/classes following Google style
- **Variable naming**: snake_case for variables/functions, UPPER_CASE for constants

## Architecture
- MCP server using FastMCP framework
- Resources for D&D API access with persistent caching
- Handle API failures gracefully with informative error messages
- Use async/await patterns for concurrent operations