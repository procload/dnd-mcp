#!/usr/bin/env python3
import asyncio
import logging
import sys
import traceback
from mcp.server import Server
from mcp.server.stdio import stdio_server
import api_helpers
import formatters
import prompts
import tools

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add debug output
print("Starting D&D MCP server...", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Current directory: {sys.path}", file=sys.stderr)

try:
    # Create server
    print("Creating server...", file=sys.stderr)
    app = Server("dnd-mcp-server")
    print("Server created successfully", file=sys.stderr)

    # Register prompts and tools
    prompts.register_prompts(app)
    tools.register_tools(app)

    async def main():
        """Run the server."""
        print("Starting main function", file=sys.stderr)
        try:
            print("Creating stdio_server...", file=sys.stderr)
            async with stdio_server() as streams:
                print("stdio_server created", file=sys.stderr)
                print("Running app...", file=sys.stderr)
                await app.run(
                    streams[0],
                    streams[1],
                    app.create_initialization_options()
                )
                print("App run completed", file=sys.stderr)
        except Exception as e:
            print(f"Error in main: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise

    if __name__ == "__main__":
        print("Running main function", file=sys.stderr)
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"Fatal error: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)
except Exception as e:
    print(f"Initialization error: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
