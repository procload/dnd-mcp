import requests
import logging
from mcp.server.fastmcp import FastMCP
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define prompts
PROMPTS = {
    "character-concept": types.Prompt(
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
    )
}

# Initialize FastMCP server
mcp = FastMCP("dnd")

# Register prompt handlers


@mcp.list_prompts
async def list_prompts() -> list[types.Prompt]:
    """List available prompts."""
    logger.info("Listing available prompts")
    return list(PROMPTS.values())


@mcp.get_prompt
async def get_prompt(name: str, arguments: dict[str, str] | None = None) -> types.GetPromptResult:
    """Get a specific prompt with arguments."""
    logger.info(f"Getting prompt: {name} with arguments: {arguments}")

    if name not in PROMPTS:
        raise ValueError(f"Prompt not found: {name}")

    if name == "character-concept":
        class_name = arguments.get("class_name", "") if arguments else ""
        race = arguments.get("race", "") if arguments else ""
        background = arguments.get("background", "Any") if arguments else "Any"

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

    raise ValueError("Prompt implementation not found")

# D&D API endpoint
API_BASE_URL = "https://www.dnd5eapi.co/api"


@mcp.tool()
async def query_monster(name: str) -> str:
    """Get information about a D&D monster.

    Args:
        name: The name of the monster (e.g., goblin, dragon)
    """
    logger.info(f"Querying monster: {name}")

    try:
        response = requests.get(f"{API_BASE_URL}/monsters/{name.lower()}")
        if response.status_code == 200:
            monster_data = response.json()
            return format_monster_data(monster_data)
        else:
            return f"Error: Monster '{name}' not found"
    except Exception as e:
        logger.error(f"API query error: {str(e)}")
        return f"Error querying D&D API: {str(e)}"


@mcp.tool()
async def list_monster_types() -> str:
    """List all available monster types in D&D 5e."""
    logger.info("Listing monster types")

    try:
        response = requests.get(f"{API_BASE_URL}/monster-types")
        if response.status_code == 200:
            types_data = response.json()
            types_list = [item["name"]
                          for item in types_data.get("results", [])]
            return f"Available monster types:\n{', '.join(types_list)}"
        else:
            return "Error: Could not retrieve monster types"
    except Exception as e:
        logger.error(f"API query error: {str(e)}")
        return f"Error querying D&D API: {str(e)}"


@mcp.tool()
async def get_spell(name: str) -> str:
    """Get detailed information about a D&D spell.

    Args:
        name: The name of the spell (e.g., fireball, magic missile)
    """
    logger.info(f"Querying spell: {name}")

    try:
        response = requests.get(
            f"{API_BASE_URL}/spells/{name.lower().replace(' ', '-')}")
        if response.status_code == 200:
            spell_data = response.json()
            return format_spell_data(spell_data)
        else:
            return f"Error: Spell '{name}' not found"
    except Exception as e:
        logger.error(f"API query error: {str(e)}")
        return f"Error querying D&D API: {str(e)}"


@mcp.tool()
async def get_class(name: str) -> str:
    """Get information about a D&D character class.

    Args:
        name: The name of the class (e.g., wizard, fighter)
    """
    logger.info(f"Querying class: {name}")

    try:
        response = requests.get(f"{API_BASE_URL}/classes/{name.lower()}")
        if response.status_code == 200:
            class_data = response.json()
            return format_class_data(class_data)
        else:
            return f"Error: Class '{name}' not found"
    except Exception as e:
        logger.error(f"API query error: {str(e)}")
        return f"Error querying D&D API: {str(e)}"


@mcp.tool()
async def get_equipment(name: str) -> str:
    """Get information about D&D equipment.

    Args:
        name: The name of the equipment (e.g., longsword, plate armor)
    """
    logger.info(f"Querying equipment: {name}")

    try:
        response = requests.get(
            f"{API_BASE_URL}/equipment/{name.lower().replace(' ', '-')}")
        if response.status_code == 200:
            equipment_data = response.json()
            return format_equipment_data(equipment_data)
        else:
            return f"Error: Equipment '{name}' not found"
    except Exception as e:
        logger.error(f"API query error: {str(e)}")
        return f"Error querying D&D API: {str(e)}"


@mcp.tool()
async def get_race(name: str) -> str:
    """Get information about a D&D race.

    Args:
        name: The name of the race (e.g., elf, dwarf)
    """
    logger.info(f"Querying race: {name}")

    try:
        response = requests.get(f"{API_BASE_URL}/races/{name.lower()}")
        if response.status_code == 200:
            race_data = response.json()
            return format_race_data(race_data)
        else:
            return f"Error: Race '{name}' not found"
    except Exception as e:
        logger.error(f"API query error: {str(e)}")
        return f"Error querying D&D API: {str(e)}"


@mcp.tool()
async def search_api(endpoint: str, query: str) -> str:
    """Search the D&D API for specific content.

    Args:
        endpoint: The API endpoint to search (e.g., spells, monsters, classes)
        query: The search term
    """
    logger.info(f"Searching {endpoint} for: {query}")

    valid_endpoints = ["spells", "monsters", "equipment",
                       "classes", "races", "magic-items", "features"]

    if endpoint not in valid_endpoints:
        return f"Error: Invalid endpoint. Valid options are: {', '.join(valid_endpoints)}"

    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}?name={query}")
        if response.status_code == 200:
            results = response.json()
            if results["count"] == 0:
                return f"No results found for '{query}' in {endpoint}."

            items = [f"- {item['name']}" for item in results["results"]]
            return f"Found {results['count']} results for '{query}' in {endpoint}:\n" + "\n".join(items)
        else:
            return f"Error: Could not search {endpoint}"
    except Exception as e:
        logger.error(f"API query error: {str(e)}")
        return f"Error querying D&D API: {str(e)}"


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


def format_equipment_data(data):
    """Format equipment data into a readable string."""
    result = f"# {data['name']}\n"
    result += f"Category: {data.get('equipment_category', {}).get('name', 'Unknown')}\n"

    if "weapon_category" in data:
        result += f"Weapon Category: {data.get('weapon_category', 'Unknown')}\n"
        result += f"Weapon Range: {data.get('weapon_range', 'Unknown')}\n"

        if "damage" in data:
            result += f"Damage: {data.get('damage', {}).get('damage_dice', 'Unknown')} {data.get('damage', {}).get('damage_type', {}).get('name', 'Unknown')}\n"

    if "armor_category" in data:
        result += f"Armor Category: {data.get('armor_category', 'Unknown')}\n"
        result += f"AC: {data.get('armor_class', {}).get('base', 'Unknown')}\n"
        if data.get('str_minimum', 0) > 0:
            result += f"Strength Minimum: {data.get('str_minimum', 'Unknown')}\n"
        if data.get('stealth_disadvantage', False):
            result += "Stealth: Disadvantage\n"

    result += f"Cost: {data.get('cost', {}).get('quantity', 'Unknown')} {data.get('cost', {}).get('unit', 'Unknown')}\n"
    result += f"Weight: {data.get('weight', 'Unknown')} lbs\n"

    if "desc" in data and data["desc"]:
        result += "\n## Description\n"
        for desc in data["desc"]:
            result += f"{desc}\n"

    return result


def format_race_data(data):
    """Format race data into a readable string."""
    result = f"# {data['name']}\n"
    result += f"Speed: {data.get('speed', 'Unknown')}\n"

    if "ability_bonuses" in data:
        result += "\n## Ability Bonuses\n"
        for bonus in data["ability_bonuses"]:
            result += f"- {bonus.get('ability_score', {}).get('name', 'Unknown')}: +{bonus.get('bonus', 0)}\n"

    if "traits" in data:
        result += "\n## Traits\n"
        for trait in data["traits"]:
            result += f"- {trait.get('name', 'Unknown')}\n"

    if "languages" in data:
        result += "\n## Languages\n"
        for lang in data["languages"]:
            result += f"- {lang.get('name', 'Unknown')}\n"

    return result


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
