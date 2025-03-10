#!/usr/bin/env python3
import logging
import sys
import traceback
import os
from mcp.server.fastmcp import FastMCP
import api_helpers
import formatters
import prompts
import tools
import resources
from cache import APICache

# Configure more detailed logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "dnd_mcp_server.log")

# Configure logging with both console and file output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Add debug output
print("Starting D&D MCP server with FastMCP...", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Current directory: {sys.path}", file=sys.stderr)
print(f"Logs will be saved to: {os.path.abspath(log_file)}", file=sys.stderr)

try:
    # Create FastMCP server
    print("Creating FastMCP server...", file=sys.stderr)
    app = FastMCP("dnd-mcp-server")
    print("FastMCP server created successfully", file=sys.stderr)

    # Create shared cache with 24-hour TTL and persistence
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")
    cache = APICache(ttl_hours=24, persistent=True, cache_dir=cache_dir)
    print(
        f"API cache initialized (24-hour TTL, persistent cache in {cache_dir})", file=sys.stderr)

    # Register components
    resources.register_resources(app, cache)
    tools.register_tools(app, cache)
    prompts.register_prompts(app)

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
