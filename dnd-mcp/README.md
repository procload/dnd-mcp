# D&D MCP Server

A Python-based MCP server that queries D&D 5e API to retrieve game information.

## Features

- MCP server for client-server communication
- REST API endpoints for alternative data access
- D&D 5e API integration for monster data

## Setup

1. Install dependencies:
   ```
   pip install .
   ```

2. Run the server:
   ```
   python -m dnd-mcp.main
   ```

## MCP Client Connection

Connect to the MCP server on port 4000 and use the following event:

- Send `query_monster` event with data `{"name": "goblin"}` to get monster information
- Receive `monster_data` event with the monster details

## REST API

The REST API is available on port 8000:

- `GET /` - Check server status
- `GET /api/monsters/{name}` - Get monster information

## Configuration

Edit `main.py` to modify API endpoints or add new functionality.