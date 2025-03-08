#!/usr/bin/env python3
import asyncio
import logging
import sys
import traceback
import json
import urllib.request
import urllib.error
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

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

    # D&D API endpoint
    API_BASE_URL = "https://www.dnd5eapi.co/api"

    # Define prompts
    print("Defining prompts...", file=sys.stderr)

    @app.list_prompts()
    async def list_prompts() -> list[types.Prompt]:
        """List available prompts."""
        print("list_prompts called", file=sys.stderr)
        try:
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
                        ),
                        types.PromptArgument(
                            name="background",
                            description="The character's background (optional)",
                            required=False
                        )
                    ]
                ),
                types.Prompt(
                    name="adventure-hook",
                    description="Generate a D&D adventure hook",
                    arguments=[
                        types.PromptArgument(
                            name="setting",
                            description="The adventure setting (e.g., dungeon, forest)",
                            required=True
                        ),
                        types.PromptArgument(
                            name="level_range",
                            description="The level range (e.g., 1-5, 5-10)",
                            required=True
                        ),
                        types.PromptArgument(
                            name="theme",
                            description="The adventure theme (optional)",
                            required=False
                        )
                    ]
                )
            ]
        except Exception as e:
            print(f"Error in list_prompts: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise

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
            background = arguments.get(
                "background", "Any") if arguments else "Any"

            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"""Create a concept for a D&D character with the following parameters:

Class: {class_name}
Race: {race}
Background: {background}

Please include:
1. A brief character backstory
2. Personality traits
3. Ideals, bonds, and flaws
4. Suggested ability score priorities
5. Recommended skills and equipment
6. A few roleplaying tips
"""
                        )
                    )
                ]
            )

        elif name == "adventure-hook":
            setting = arguments.get("setting", "") if arguments else ""
            level_range = arguments.get("level_range", "") if arguments else ""
            theme = arguments.get("theme", "Any") if arguments else "Any"

            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"""Create a D&D adventure hook with the following parameters:

Setting: {setting}
Level Range: {level_range}
Theme: {theme}

Please include:
1. A compelling hook to draw players in
2. Key NPCs involved
3. Main conflict or challenge
4. Potential rewards
5. A few interesting encounters
6. A plot twist or complication
"""
                        )
                    )
                ]
            )

        raise ValueError(f"Prompt not found: {name}")

    # Define tools

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """List available tools."""
        print("list_tools called", file=sys.stderr)
        return [
            types.Tool(
                name="query_monster",
                description="Get information about a D&D monster",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the monster (e.g., goblin, dragon)"
                        }
                    },
                    "required": ["name"]
                }
            ),
            types.Tool(
                name="get_spell",
                description="Get detailed information about a D&D spell",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the spell (e.g., fireball, magic missile)"
                        }
                    },
                    "required": ["name"]
                }
            ),
            types.Tool(
                name="get_class",
                description="Get information about a D&D character class",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the class (e.g., wizard, fighter)"
                        }
                    },
                    "required": ["name"]
                }
            ),
            types.Tool(
                name="search_api",
                description="Search the D&D API for specific content",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "endpoint": {
                            "type": "string",
                            "description": "The API endpoint to search (e.g., spells, monsters, classes)"
                        },
                        "query": {
                            "type": "string",
                            "description": "The search term"
                        }
                    },
                    "required": ["endpoint", "query"]
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

        try:
            if name == "query_monster":
                monster_name = arguments.get("name", "")
                response = urllib.request.urlopen(
                    f"{API_BASE_URL}/monsters/{monster_name.lower()}")

                if response.status == 200:
                    monster_data = json.loads(response.read())
                    formatted_data = format_monster_data(monster_data)
                    return [types.TextContent(type="text", text=formatted_data)]
                else:
                    return [types.TextContent(type="text", text=f"Error: Monster '{monster_name}' not found")]

            elif name == "get_spell":
                spell_name = arguments.get("name", "")
                response = urllib.request.urlopen(
                    f"{API_BASE_URL}/spells/{spell_name.lower().replace(' ', '-')}")

                if response.status == 200:
                    spell_data = json.loads(response.read())
                    formatted_data = format_spell_data(spell_data)
                    return [types.TextContent(type="text", text=formatted_data)]
                else:
                    return [types.TextContent(type="text", text=f"Error: Spell '{spell_name}' not found")]

            elif name == "get_class":
                class_name = arguments.get("name", "")
                response = urllib.request.urlopen(
                    f"{API_BASE_URL}/classes/{class_name.lower()}")

                if response.status == 200:
                    class_data = json.loads(response.read())
                    formatted_data = format_class_data(class_data)
                    return [types.TextContent(type="text", text=formatted_data)]
                else:
                    return [types.TextContent(type="text", text=f"Error: Class '{class_name}' not found")]

            elif name == "search_api":
                endpoint = arguments.get("endpoint", "")
                query = arguments.get("query", "")

                valid_endpoints = ["spells", "monsters", "equipment",
                                   "classes", "races", "magic-items", "features"]

                if endpoint not in valid_endpoints:
                    return [types.TextContent(type="text", text=f"Error: Invalid endpoint. Valid options are: {', '.join(valid_endpoints)}")]

                response = urllib.request.urlopen(
                    f"{API_BASE_URL}/{endpoint}?name={query}")

                if response.status == 200:
                    results = json.loads(response.read())
                    if results["count"] == 0:
                        return [types.TextContent(type="text", text=f"No results found for '{query}' in {endpoint}.")]

                    items = [
                        f"- {item['name']}" for item in results["results"]]
                    result_text = f"Found {results['count']} results for '{query}' in {endpoint}:\n" + "\n".join(
                        items)
                    return [types.TextContent(type="text", text=result_text)]
                else:
                    return [types.TextContent(type="text", text=f"Error: Could not search {endpoint}")]

            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

        except Exception as e:
            logger.error(f"Error in call_tool: {str(e)}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    # Helper functions for formatting data

    def format_monster_data(data):
        """Format monster data into a readable string."""
        result = f"# {data['name']}\n"
        result += f"Size: {data.get('size', 'Unknown')}\n"
        result += f"Type: {data.get('type', 'Unknown')}\n"
        result += f"Alignment: {data.get('alignment', 'Unknown')}\n"
        result += f"Armor Class: {data.get('armor_class', 'Unknown')}\n"
        result += f"Hit Points: {data.get('hit_points', 'Unknown')} ({data.get('hit_dice', 'Unknown')})\n"
        result += f"Speed: {', '.join([f'{k} {v}' for k,
                                      v in data.get('speed', {}).items()])}\n\n"

        # Ability scores
        result += "## Abilities\n"
        for ability in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
            if ability in data:
                result += f"{ability.capitalize()}: {data[ability]}\n"

        # Special abilities
        if "special_abilities" in data and data["special_abilities"]:
            result += "\n## Special Abilities\n"
            for ability in data["special_abilities"]:
                result += f"**{ability.get('name', 'Unknown')}**: {ability.get('desc', 'No description')}\n"

        # Actions
        if "actions" in data and data["actions"]:
            result += "\n## Actions\n"
            for action in data["actions"]:
                result += f"**{action.get('name', 'Unknown')}**: {action.get('desc', 'No description')}\n"

        return result

    def format_spell_data(data):
        """Format spell data into a readable string."""
        result = f"# {data['name']}\n"
        result += f"Level: {data.get('level', 'Unknown')}\n"
        result += f"School: {data.get('school', {}).get('name', 'Unknown')}\n"
        result += f"Casting Time: {data.get('casting_time', 'Unknown')}\n"
        result += f"Range: {data.get('range', 'Unknown')}\n"
        result += f"Components: {', '.join(data.get('components', []))}\n"
        result += f"Duration: {data.get('duration', 'Unknown')}\n\n"

        if "desc" in data:
            result += "## Description\n"
            for desc in data["desc"]:
                result += f"{desc}\n"

        if "higher_level" in data and data["higher_level"]:
            result += "\n## At Higher Levels\n"
            for desc in data["higher_level"]:
                result += f"{desc}\n"

        return result

    def format_class_data(data):
        """Format class data into a readable string."""
        result = f"# {data['name']}\n"
        result += f"Hit Die: d{data.get('hit_die', 'Unknown')}\n"

        if "proficiencies" in data:
            result += "\n## Proficiencies\n"
            for prof in data["proficiencies"]:
                result += f"- {prof.get('name', 'Unknown')}\n"

        if "proficiency_choices" in data:
            result += "\n## Proficiency Choices\n"
            for choice in data["proficiency_choices"]:
                result += f"Choose {choice.get('choose', 0)} from:\n"
                for option in choice.get("from", {}).get("options", []):
                    result += f"- {option.get('item', {}).get('name', 'Unknown')}\n"

        if "starting_equipment" in data:
            result += "\n## Starting Equipment\n"
            for item in data["starting_equipment"]:
                result += f"- {item.get('equipment', {}).get('name', 'Unknown')} (Quantity: {item.get('quantity', 1)})\n"

        return result

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
