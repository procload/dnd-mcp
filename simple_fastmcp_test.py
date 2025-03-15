#!/usr/bin/env python3
import asyncio
import logging
import sys
import traceback
from mcp.server.fastmcp import FastMCP
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add debug output
print("Starting Simple FastMCP Test...", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)

try:
    # Create FastMCP server
    print("Creating FastMCP server...", file=sys.stderr)
    app = FastMCP("simple-fastmcp-test")
    print("FastMCP server created successfully", file=sys.stderr)

    # Define a simple tool using the decorator syntax
    @app.tool()
    async def hello_world(name: str = "World") -> str:
        """Say hello to someone.

        Args:
            name: The name to greet
        """
        return f"Hello, {name}!"

    # Define a simple prompt list function
    @app.list_prompts
    async def list_prompts():
        """List available prompts."""
        return [
            types.Prompt(
                name="greeting",
                description="Generate a greeting",
                arguments=[
                    types.PromptArgument(
                        name="name",
                        description="The name to greet",
                        required=False
                    )
                ]
            )
        ]

    # Define a simple get prompt function
    @app.get_prompt
    async def get_prompt(name: str, arguments: dict[str, str] | None = None):
        """Get a specific prompt."""
        if name == "greeting":
            person_name = arguments.get(
                "name", "World") if arguments else "World"
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"Generate a friendly greeting for {person_name}."
                        )
                    )
                ]
            )
        else:
            raise ValueError(f"Prompt not found: {name}")

    async def main():
        """Run the server."""
        print("Starting main function", file=sys.stderr)
        try:
            print("Running FastMCP app...", file=sys.stderr)
            await app.run_async(transport='stdio')
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
