#!/usr/bin/env python3
import logging
import sys
import traceback
from mcp.server.fastmcp import FastMCP
import api_helpers
import formatters
import prompts
import tools  # Updated import for renamed tools file

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add debug output
print("Starting D&D MCP server with FastMCP...", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Current directory: {sys.path}", file=sys.stderr)

try:
    # Create FastMCP server
    print("Creating FastMCP server...", file=sys.stderr)
    app = FastMCP("dnd-mcp-server")
    print("FastMCP server created successfully", file=sys.stderr)

    # Register prompts and tools
    prompts.register_prompts(app)
    tools.register_tools(app)  # Updated module name

    # For direct execution, we use the run() method
    if __name__ == "__main__":
        print("Running FastMCP app...", file=sys.stderr)
        try:
            # Use the simple run method
            app.run()
            print("App run completed", file=sys.stderr)
        except Exception as e:
            print(f"Error running app: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)
except Exception as e:
    print(f"Initialization error: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
