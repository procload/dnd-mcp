#!/usr/bin/env python3
import asyncio
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server
import sys

# Add debug output
print("Starting simple_dnd_server.py...", file=sys.stderr)

# Create a simple server
app = Server("simple-dnd-server")

# Define a simple prompt


@app.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    """List available prompts."""
    print("list_prompts called", file=sys.stderr)
    return [
        types.Prompt(
            name="character-concept",
            description="Generate a D&D character concept",
            arguments=[
                types.PromptArgument(
                    name="class_name",
                    description="The character's class (e.g., wizard, fighter)",
                    required=True
                ),
                types.PromptArgument(
                    name="race",
                    description="The character's race (e.g., elf, dwarf)",
                    required=True
                )
            ]
        )
    ]


@app.get_prompt()
async def get_prompt(
    name: str, arguments: dict[str, str] | None = None
) -> types.GetPromptResult:
    """Get a specific prompt."""
    print(
        f"get_prompt called with name={name}, arguments={arguments}", file=sys.stderr)
    if name == "character-concept":
        class_name = arguments.get("class_name", "") if arguments else ""
        race = arguments.get("race", "") if arguments else ""

        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Create a concept for a D&D {race} {class_name} character."
                    )
                )
            ]
        )

    raise ValueError(f"Prompt not found: {name}")

# Define a simple tool


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools."""
    print("list_tools called", file=sys.stderr)
    return [
        types.Tool(
            name="hello",
            description="Say hello",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name to greet"
                    }
                },
                "required": ["name"]
            }
        )
    ]


@app.call_tool()
async def call_tool(
    name: str,
    arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Call a tool."""
    print(
        f"call_tool called with name={name}, arguments={arguments}", file=sys.stderr)
    if name == "hello":
        person_name = arguments.get("name", "world")
        return [types.TextContent(type="text", text=f"Hello, {person_name}!")]

    raise ValueError(f"Tool not found: {name}")


async def main():
    """Run the server."""
    print("Starting main function", file=sys.stderr)
    try:
        async with stdio_server() as streams:
            print("stdio_server created", file=sys.stderr)
            await app.run(
                streams[0],
                streams[1],
                app.create_initialization_options()
            )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    print("Running main function", file=sys.stderr)
    asyncio.run(main())
