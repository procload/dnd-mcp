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

    # Helper functions for API interaction
    def validate_dnd_entity(endpoint: str, name: str) -> bool:
        """Check if an entity exists in the D&D API."""
        if not name:
            return False

        try:
            name = name.lower().replace(' ', '-')
            url = f"{API_BASE_URL}/{endpoint}/{name}"
            print(f"Validating entity: {url}", file=sys.stderr)

            with urllib.request.urlopen(url) as response:
                return response.status == 200
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"Entity not found: {endpoint}/{name}", file=sys.stderr)
                return False
            print(f"HTTP error validating entity: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Error validating entity: {e}", file=sys.stderr)
            return False

    def fetch_dnd_entity(endpoint: str, name: str) -> dict:
        """Fetch entity details from the D&D API."""
        if not name:
            return {}

        try:
            name = name.lower().replace(' ', '-')
            url = f"{API_BASE_URL}/{endpoint}/{name}"
            print(f"Fetching entity: {url}", file=sys.stderr)

            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    return json.loads(response.read())
                return {}
        except urllib.error.HTTPError as e:
            print(f"HTTP error fetching entity: {e}", file=sys.stderr)
            return {}
        except Exception as e:
            print(f"Error fetching entity: {e}", file=sys.stderr)
            return {}

    def get_primary_ability(class_name: str) -> str:
        """Return the primary ability for a class."""
        mapping = {
            "barbarian": "Strength",
            "bard": "Charisma",
            "cleric": "Wisdom",
            "druid": "Wisdom",
            "fighter": "Strength or Dexterity",
            "monk": "Dexterity & Wisdom",
            "paladin": "Strength & Charisma",
            "ranger": "Dexterity & Wisdom",
            "rogue": "Dexterity",
            "sorcerer": "Charisma",
            "warlock": "Charisma",
            "wizard": "Intelligence"
        }
        return mapping.get(class_name.lower(), "Unknown")

    def get_asi_text(race_data: dict) -> str:
        """Extract ability score increases from race data."""
        if not race_data or "ability_bonuses" not in race_data:
            return "Unknown"

        bonuses = race_data.get("ability_bonuses", [])
        if not bonuses:
            return "None"

        result = []
        for bonus in bonuses:
            ability = bonus.get("ability_score", {}).get("name", "Unknown")
            bonus_value = bonus.get("bonus", 0)
            if ability and bonus_value:
                result.append(f"{ability} +{bonus_value}")

        return ", ".join(result) if result else "None"

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
                ),
                types.Prompt(
                    name="spell-selection",
                    description="Get spell recommendations for your character",
                    arguments=[
                        types.PromptArgument(
                            name="class_name",
                            description="Your character's class",
                            required=True
                        ),
                        types.PromptArgument(
                            name="level",
                            description="Character level (1-20)",
                            required=True
                        ),
                        types.PromptArgument(
                            name="focus",
                            description="Spell focus (e.g., damage, healing, utility)",
                            required=False
                        )
                    ]
                ),
                types.Prompt(
                    name="encounter-builder",
                    description="Build a balanced combat encounter",
                    arguments=[
                        types.PromptArgument(
                            name="party_level",
                            description="Average party level (1-20)",
                            required=True
                        ),
                        types.PromptArgument(
                            name="party_size",
                            description="Number of players (1-10)",
                            required=True
                        ),
                        types.PromptArgument(
                            name="difficulty",
                            description="Encounter difficulty (easy, medium, hard, deadly)",
                            required=True
                        ),
                        types.PromptArgument(
                            name="environment",
                            description="Battle environment (e.g., forest, dungeon, city)",
                            required=False
                        )
                    ]
                ),
                types.Prompt(
                    name="magic-item-finder",
                    description="Find appropriate magic items for your character",
                    arguments=[
                        types.PromptArgument(
                            name="character_level",
                            description="Character level (1-20)",
                            required=True
                        ),
                        types.PromptArgument(
                            name="character_class",
                            description="Character class",
                            required=True
                        ),
                        types.PromptArgument(
                            name="rarity",
                            description="Item rarity (common, uncommon, rare, very rare, legendary)",
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
        try:
            if name == "character-concept":
                class_name = arguments.get(
                    "class_name", "") if arguments else ""
                race = arguments.get("race", "") if arguments else ""
                background = arguments.get(
                    "background", "") if arguments else ""

                # Validate class and race against API
                class_valid = validate_dnd_entity("classes", class_name)
                race_valid = validate_dnd_entity("races", race)

                # Fetch class and race details if valid
                class_details = {}
                race_details = {}

                if class_valid:
                    class_details = fetch_dnd_entity("classes", class_name)
                if race_valid:
                    race_details = fetch_dnd_entity("races", race)

                # Build prompt with validation and API data
                prompt_text = f"Create a concept for a D&D {race} {class_name} character"
                if background:
                    prompt_text += f" with a {background} background"
                prompt_text += "."

                # Add validation notes
                validation_notes = []
                if not class_valid:
                    validation_notes.append(
                        f"Note: '{class_name}' is not a standard D&D 5e class")
                if not race_valid:
                    validation_notes.append(
                        f"Note: '{race}' is not a standard D&D 5e race")

                if validation_notes:
                    prompt_text += "\n\n" + "\n".join(validation_notes)

                # Add class information if available
                if class_details:
                    hit_die = class_details.get("hit_die", "?")
                    primary_ability = get_primary_ability(class_name)

                    # Extract saving throw proficiencies
                    saving_throws = []
                    for prof in class_details.get("proficiency_choices", []):
                        if "Saving Throw" in str(prof):
                            for option in prof.get("from", {}).get("options", []):
                                if option.get("item", {}).get("name", "").startswith("Saving Throw:"):
                                    saving_throws.append(option.get("item", {}).get(
                                        "name", "").replace("Saving Throw: ", ""))

                    # Extract starting equipment
                    equipment = []
                    for item in class_details.get("starting_equipment", []):
                        equipment.append(
                            item.get("equipment", {}).get("name", "Unknown"))

                    class_info = f"\n\nClass Features:\n- Hit Die: d{hit_die}\n- Primary Ability: {primary_ability}"
                    if saving_throws:
                        class_info += f"\n- Saving Throw Proficiencies: {', '.join(saving_throws)}"
                    if equipment:
                        class_info += f"\n- Starting Equipment includes: {', '.join(equipment[:3])}"

                    prompt_text += class_info

                # Add race information if available
                if race_details:
                    speed = race_details.get("speed", "?")
                    size = race_details.get("size", "?")
                    asi_text = get_asi_text(race_details)

                    # Extract traits
                    traits = []
                    for trait in race_details.get("traits", []):
                        traits.append(trait.get("name", "Unknown"))

                    race_info = f"\n\nRace Features:\n- Speed: {speed}\n- Size: {size}\n- Ability Score Increase: {asi_text}"
                    if traits:
                        race_info += f"\n- Traits: {', '.join(traits)}"

                    prompt_text += race_info

                # Add creative direction
                prompt_text += "\n\nPlease create a compelling character concept that includes:\n1. A brief backstory\n2. Personality traits\n3. Goals and motivations\n4. A unique quirk or characteristic"

                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=prompt_text
                            )
                        )
                    ]
                )
            elif name == "adventure-hook":
                setting = arguments.get("setting", "") if arguments else ""
                level_range = arguments.get(
                    "level_range", "") if arguments else ""
                theme = arguments.get("theme", "") if arguments else ""

                prompt_text = f"Create a D&D adventure hook set in a {setting} for character levels {level_range}"
                if theme:
                    prompt_text += f" with a {theme} theme"
                prompt_text += "."

                prompt_text += "\n\nInclude:\n1. A compelling hook to draw players in\n2. Key NPCs involved\n3. Potential challenges and encounters\n4. Possible rewards"

                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=prompt_text
                            )
                        )
                    ]
                )
            elif name == "spell-selection":
                class_name = arguments.get(
                    "class_name", "") if arguments else ""
                level = arguments.get("level", "") if arguments else ""
                focus = arguments.get("focus", "") if arguments else ""

                # Validate class against API
                class_valid = validate_dnd_entity("classes", class_name)

                # Build prompt with validation and API data
                prompt_text = f"Recommend spells for a level {level} {class_name}"
                if focus:
                    prompt_text += f" focusing on {focus} spells"
                prompt_text += "."

                # Add validation notes
                if not class_valid:
                    prompt_text += f"\n\nNote: '{class_name}' is not a standard D&D 5e class."

                # Fetch spells for this class if valid
                if class_valid:
                    try:
                        url = f"{API_BASE_URL}/classes/{class_name.lower()}/spells"
                        with urllib.request.urlopen(url) as response:
                            if response.status == 200:
                                spells_data = json.loads(response.read())
                                if spells_data.get("count", 0) > 0:
                                    spell_names = [
                                        spell.get("name", "") for spell in spells_data.get("results", [])]
                                    prompt_text += f"\n\nAvailable spells for {class_name} include: {', '.join(spell_names[:10])}"
                                    if len(spell_names) > 10:
                                        prompt_text += f", and {len(spell_names) - 10} more."
                    except Exception as e:
                        print(f"Error fetching spells: {e}", file=sys.stderr)

                # Add guidance
                prompt_text += "\n\nPlease provide:\n1. Recommended cantrips\n2. Recommended spells by level\n3. Spell combinations that work well together\n4. Situational spells that could be useful"

                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=prompt_text
                            )
                        )
                    ]
                )
            elif name == "encounter-builder":
                party_level = arguments.get(
                    "party_level", "") if arguments else ""
                party_size = arguments.get(
                    "party_size", "") if arguments else ""
                difficulty = arguments.get(
                    "difficulty", "") if arguments else ""
                environment = arguments.get(
                    "environment", "") if arguments else ""

                # Calculate appropriate CR range based on party level and difficulty
                try:
                    level = int(party_level)
                    size = int(party_size)

                    # Calculate CR range based on party level and difficulty
                    cr_min = max(0, level - 3)
                    cr_max = level

                    if difficulty.lower() == "easy":
                        cr_min = max(0, level - 4)
                        cr_max = level - 1
                    elif difficulty.lower() == "medium":
                        cr_min = max(0, level - 3)
                        cr_max = level
                    elif difficulty.lower() == "hard":
                        cr_min = max(0, level - 2)
                        cr_max = level + 1
                    elif difficulty.lower() == "deadly":
                        cr_min = max(0, level - 1)
                        cr_max = level + 3

                    # Adjust for party size
                    if size > 4:
                        cr_max += min(3, (size - 4))
                    elif size < 4:
                        cr_max -= min(2, (4 - size))
                        cr_min = max(0, cr_min - min(2, (4 - size)))
                except ValueError:
                    cr_min = 0
                    cr_max = 20

                # Build prompt with API data
                prompt_text = f"Build a {difficulty} combat encounter for {party_size} players at level {party_level}"
                if environment:
                    prompt_text += f" in a {environment} environment"
                prompt_text += "."

                # Fetch monsters in the appropriate CR range
                monster_suggestions = []
                try:
                    # Get all monsters
                    with urllib.request.urlopen(f"{API_BASE_URL}/monsters") as response:
                        if response.status == 200:
                            monsters_data = json.loads(response.read())
                            if monsters_data.get("count", 0) > 0:
                                # We need to check each monster's CR
                                # Limit to avoid too many requests
                                for monster in monsters_data.get("results", [])[:30]:
                                    try:
                                        monster_url = monster.get(
                                            "url", "").lstrip("/api/")
                                        with urllib.request.urlopen(f"{API_BASE_URL}/{monster_url}") as monster_response:
                                            if monster_response.status == 200:
                                                monster_details = json.loads(
                                                    monster_response.read())
                                                monster_cr = monster_details.get(
                                                    "challenge_rating", 0)
                                                if cr_min <= monster_cr <= cr_max:
                                                    monster_suggestions.append({
                                                        "name": monster.get("name", "Unknown"),
                                                        "cr": monster_cr,
                                                        "type": monster_details.get("type", "Unknown"),
                                                        "size": monster_details.get("size", "Unknown")
                                                    })
                                    except Exception as e:
                                        print(
                                            f"Error fetching monster details: {e}", file=sys.stderr)
                                        continue
                except Exception as e:
                    print(f"Error fetching monsters: {e}", file=sys.stderr)

                # Add monster suggestions to prompt
                if monster_suggestions:
                    prompt_text += "\n\nSuggested monsters in appropriate CR range:"
                    # Limit to 8 suggestions
                    for i, monster in enumerate(monster_suggestions[:8]):
                        prompt_text += f"\n{i+1}. {monster['name']} (CR {monster['cr']}, {monster['size']} {monster['type']})"

                # Add encounter building guidance
                prompt_text += "\n\nPlease design an encounter that includes:"
                prompt_text += "\n1. A balanced mix of monsters (consider using the suggestions above)"
                prompt_text += "\n2. Interesting terrain features and environmental elements"
                prompt_text += "\n3. Tactical considerations and monster strategies"
                prompt_text += "\n4. Appropriate treasure and rewards"
                prompt_text += "\n5. Potential for both combat and non-combat resolution"

                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=prompt_text
                            )
                        )
                    ]
                )
            elif name == "magic-item-finder":
                character_level = arguments.get(
                    "character_level", "") if arguments else ""
                character_class = arguments.get(
                    "character_class", "") if arguments else ""
                rarity = arguments.get("rarity", "") if arguments else ""

                # Validate class against API
                class_valid = validate_dnd_entity("classes", character_class)

                # Determine appropriate rarities based on character level
                appropriate_rarities = []
                try:
                    level = int(character_level)
                    if level >= 1:
                        appropriate_rarities.append("common")
                    if level >= 5:
                        appropriate_rarities.append("uncommon")
                    if level >= 11:
                        appropriate_rarities.append("rare")
                    if level >= 17:
                        appropriate_rarities.append("very rare")
                    if level >= 20:
                        appropriate_rarities.append("legendary")
                except ValueError:
                    appropriate_rarities = [
                        "common", "uncommon", "rare", "very rare", "legendary"]

                # Filter by specified rarity if provided
                if rarity and rarity.lower() in ["common", "uncommon", "rare", "very rare", "legendary"]:
                    appropriate_rarities = [rarity.lower()]

                # Build prompt with API data
                prompt_text = f"Recommend magic items for a level {character_level} {character_class}"
                if rarity:
                    prompt_text += f" of {rarity} rarity"
                prompt_text += "."

                # Add validation notes
                if not class_valid:
                    prompt_text += f"\n\nNote: '{character_class}' is not a standard D&D 5e class."

                # Fetch magic items
                magic_items = []
                try:
                    # Get all magic items
                    with urllib.request.urlopen(f"{API_BASE_URL}/magic-items") as response:
                        if response.status == 200:
                            items_data = json.loads(response.read())
                            if items_data.get("count", 0) > 0:
                                # We need to check each item's details
                                # Limit to avoid too many requests
                                for item in items_data.get("results", [])[:30]:
                                    try:
                                        item_url = item.get(
                                            "url", "").lstrip("/api/")
                                        with urllib.request.urlopen(f"{API_BASE_URL}/{item_url}") as item_response:
                                            if item_response.status == 200:
                                                item_details = json.loads(
                                                    item_response.read())
                                                item_rarity = item_details.get("rarity", {}).get(
                                                    "name", "").lower().split(" ")[0]

                                                # Check if item matches our criteria
                                                if item_rarity in appropriate_rarities:
                                                    # Check if item is class-appropriate
                                                    item_desc = item_details.get(
                                                        "desc", [""])[0].lower()
                                                    class_specific = False

                                                    # Simple heuristic for class appropriateness
                                                    class_keywords = {
                                                        "wizard": ["wizard", "spellbook", "arcane", "intelligence"],
                                                        "fighter": ["warrior", "sword", "shield", "martial"],
                                                        "rogue": ["thief", "sneak", "dexterity", "stealth"],
                                                        "cleric": ["holy", "divine", "wisdom", "prayer"],
                                                        "paladin": ["holy", "divine", "oath", "smite"],
                                                        "barbarian": ["rage", "primal", "strength", "tribal"],
                                                        "bard": ["music", "instrument", "charisma", "performance"],
                                                        "druid": ["nature", "wild", "beast", "elemental"],
                                                        "monk": ["ki", "monastery", "discipline", "unarmed"],
                                                        "ranger": ["hunter", "beast", "tracking", "wilderness"],
                                                        "sorcerer": ["innate", "charisma", "bloodline", "magic"],
                                                        "warlock": ["pact", "patron", "eldritch", "charisma"]
                                                    }

                                                    # Check if item is appropriate for the class
                                                    if character_class.lower() in class_keywords:
                                                        for keyword in class_keywords[character_class.lower()]:
                                                            if keyword in item_desc:
                                                                class_specific = True
                                                                break

                                                    magic_items.append({
                                                        "name": item.get("name", "Unknown"),
                                                        "rarity": item_rarity,
                                                        "class_specific": class_specific
                                                    })
                                    except Exception as e:
                                        print(
                                            f"Error fetching item details: {e}", file=sys.stderr)
                                        continue
                except Exception as e:
                    print(f"Error fetching magic items: {e}", file=sys.stderr)

                # Sort items to prioritize class-specific ones
                magic_items.sort(key=lambda x: (
                    0 if x["class_specific"] else 1, x["name"]))

                # Add magic item suggestions to prompt
                if magic_items:
                    prompt_text += "\n\nSuggested magic items:"
                    # Limit to 10 suggestions
                    for i, item in enumerate(magic_items[:10]):
                        prompt_text += f"\n{i+1}. {item['name']} ({item['rarity']})"
                        if item["class_specific"]:
                            prompt_text += " - particularly suitable for your class"

                # Add guidance
                prompt_text += "\n\nPlease provide:"
                prompt_text += "\n1. Recommendations from the suggested items above"
                prompt_text += "\n2. How these items would benefit this character class"
                prompt_text += "\n3. Creative ways to incorporate these items into a character's story"
                prompt_text += "\n4. Alternative items that might not be in the standard rules"

                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=prompt_text
                            )
                        )
                    ]
                )
            else:
                raise ValueError(f"Prompt not found: {name}")
        except Exception as e:
            print(f"Error in get_prompt: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise

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
                monster_name = arguments.get("name", "").lower()
                if not monster_name:
                    return [types.TextContent(type="text", text="Please provide a monster name.")]

                print(
                    f"Searching for monster: {monster_name}", file=sys.stderr)

                # Some monsters have special indices in the API
                special_monsters = {
                    "beholder": "beholder-zombie",  # Beholder is actually "beholder-zombie" in the API
                    "dragon": "adult-black-dragon",  # Default dragon if just "dragon" is specified
                    "devil": "horned-devil",        # Default devil
                    "demon": "balor",               # Default demon
                    "giant": "stone-giant",         # Default giant
                    "lich": "lich",                 # Lich is actually in the API
                    "vampire": "vampire",           # Vampire is in the API
                    "zombie": "zombie"              # Zombie is in the API
                }

                # Check if we have a special case
                if monster_name in special_monsters:
                    print(
                        f"Special monster case: {monster_name} -> {special_monsters[monster_name]}", file=sys.stderr)
                    monster_index = special_monsters[monster_name]
                else:
                    monster_index = monster_name.replace(" ", "-")

                # First try direct access by index (for exact matches)
                try:
                    # Try direct access first
                    direct_url = f"{API_BASE_URL}/monsters/{monster_index}"
                    print(
                        f"Trying direct access: {direct_url}", file=sys.stderr)

                    with urllib.request.urlopen(direct_url) as response:
                        if response.status == 200:
                            print(
                                f"Direct access successful for {monster_index}", file=sys.stderr)
                            monster_data = json.loads(response.read())
                            formatted_data = format_monster_data(monster_data)
                            return [types.TextContent(type="text", text=formatted_data)]
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        print(
                            f"Monster not found by direct index: {monster_index} (404)", file=sys.stderr)
                        # Continue to search
                    else:
                        print(f"HTTP error: {e}", file=sys.stderr)
                        return [types.TextContent(type="text", text=f"Error accessing the D&D API: {str(e)}")]
                except Exception as e:
                    print(f"Error in direct access: {e}", file=sys.stderr)
                    traceback.print_exc(file=sys.stderr)
                    # Continue to search

                # If direct access fails, try searching by name
                try:
                    # Use the monster list endpoint with name filtering
                    search_url = f"{API_BASE_URL}/monsters?name={urllib.parse.quote(monster_name)}"
                    print(
                        f"Searching monsters with URL: {search_url}", file=sys.stderr)

                    with urllib.request.urlopen(search_url) as response:
                        if response.status == 200:
                            search_results = json.loads(response.read())
                            print(
                                f"Search results count: {search_results.get('count', 0)}", file=sys.stderr)

                            if search_results.get("count", 0) == 0:
                                # Try a more general search by removing hyphens and using partial matching
                                general_name = monster_name.replace(
                                    "-", " ").split()[0]  # Get first word
                                if general_name != monster_name:
                                    print(
                                        f"Trying more general search with: {general_name}", file=sys.stderr)
                                    general_url = f"{API_BASE_URL}/monsters?name={urllib.parse.quote(general_name)}"

                                    with urllib.request.urlopen(general_url) as general_response:
                                        if general_response.status == 200:
                                            general_results = json.loads(
                                                general_response.read())
                                            print(
                                                f"General search results count: {general_results.get('count', 0)}", file=sys.stderr)

                                            if general_results.get("count", 0) > 0:
                                                # Found some results with the more general search
                                                monsters_list = "\n".join(
                                                    [f"- {m['name']}" for m in general_results.get("results", [])])
                                                return [types.TextContent(type="text", text=f"Found {general_results.get('count')} monsters related to '{monster_name}':\n\n{monsters_list}\n\nPlease specify a single monster name for detailed information.")]

                                # Try searching with challenge rating if it's a number
                                if monster_name.replace(".", "").isdigit():
                                    cr_search_url = f"{API_BASE_URL}/monsters?challenge_rating={monster_name}"
                                    print(
                                        f"Searching by CR: {cr_search_url}", file=sys.stderr)

                                    with urllib.request.urlopen(cr_search_url) as cr_response:
                                        if cr_response.status == 200:
                                            cr_results = json.loads(
                                                cr_response.read())
                                            if cr_results.get("count", 0) > 0:
                                                monsters_list = "\n".join(
                                                    [f"- {m['name']} (CR {monster_name})" for m in cr_results.get("results", [])])
                                                return [types.TextContent(type="text", text=f"Found {cr_results.get('count')} monsters with Challenge Rating {monster_name}:\n\n{monsters_list}")]

                                # Try a full list search as a last resort
                                print("Trying full monster list search",
                                      file=sys.stderr)
                                full_list_url = f"{API_BASE_URL}/monsters"
                                with urllib.request.urlopen(full_list_url) as full_list_response:
                                    if full_list_response.status == 200:
                                        full_list_results = json.loads(
                                            full_list_response.read())
                                        # Search for partial matches in the full list
                                        matches = []
                                        for m in full_list_results.get("results", []):
                                            if monster_name in m.get("name", "").lower():
                                                matches.append(m)

                                        if matches:
                                            print(
                                                f"Found {len(matches)} partial matches in full list", file=sys.stderr)
                                            monsters_list = "\n".join(
                                                [f"- {m['name']}" for m in matches])
                                            return [types.TextContent(type="text", text=f"Found {len(matches)} monsters related to '{monster_name}':\n\n{monsters_list}\n\nPlease specify a single monster name for detailed information.")]

                                # Special case for common monsters that might not be in the SRD
                                common_monsters = {
                                    "beholder": "The Beholder is an iconic D&D monster but is not included in the SRD API. It's a floating orb-like aberration with a large central eye and multiple eyestalks, each capable of casting different spell-like effects.",
                                    "mind flayer": "The Mind Flayer (Illithid) is an iconic D&D monster but is not included in the SRD API. It's a humanoid creature with an octopus-like head that feeds on the brains of sentient creatures.",
                                    "tarrasque": "The Tarrasque is an iconic D&D monster but is not included in the SRD API. It's a colossal monstrosity and one of the most powerful monsters in D&D, capable of destroying entire cities.",
                                    "displacer beast": "The Displacer Beast is an iconic D&D monster but is not included in the SRD API. It resembles a large panther with six legs and two tentacles sprouting from its shoulders, and has the magical ability to appear to be in a different location than it actually is."
                                }

                                if monster_name in common_monsters:
                                    return [types.TextContent(type="text", text=common_monsters[monster_name])]

                                return [types.TextContent(type="text", text=f"No monsters found matching '{monster_name}'. The D&D 5e SRD API only includes a subset of monsters from the Monster Manual.")]

                            # If we have results, get the first one's details
                            if search_results.get("count", 0) == 1:
                                monster_url = search_results["results"][0]["url"].lstrip(
                                    "/api/")
                                with urllib.request.urlopen(f"{API_BASE_URL}/{monster_url}") as monster_response:
                                    if monster_response.status == 200:
                                        monster_data = json.loads(
                                            monster_response.read())
                                        formatted_data = format_monster_data(
                                            monster_data)
                                        return [types.TextContent(type="text", text=formatted_data)]
                            else:
                                # Multiple results - list them
                                monsters_list = "\n".join(
                                    [f"- {m['name']}" for m in search_results.get("results", [])])
                                return [types.TextContent(type="text", text=f"Found {search_results.get('count')} monsters matching '{monster_name}':\n\n{monsters_list}\n\nPlease specify a single monster name for detailed information.")]
                except urllib.error.HTTPError as e:
                    print(
                        f"HTTP error in monster search: {e}", file=sys.stderr)
                    traceback.print_exc(file=sys.stderr)
                    return [types.TextContent(type="text", text=f"Error searching the D&D API: {str(e)}")]
                except Exception as e:
                    print(f"Error in monster search: {e}", file=sys.stderr)
                    traceback.print_exc(file=sys.stderr)
                    return [types.TextContent(type="text", text=f"Error: {str(e)}")]

                return [types.TextContent(type="text", text=f"Could not find information about '{monster_name}'. The D&D 5e SRD API only includes a subset of monsters from the Monster Manual.")]

            elif name == "get_spell":
                spell_name = arguments.get(
                    "name", "").lower().replace(" ", "-")
                if not spell_name:
                    return [types.TextContent(type="text", text="Please provide a spell name.")]

                try:
                    with urllib.request.urlopen(f"{API_BASE_URL}/spells/{spell_name}") as response:
                        if response.status == 200:
                            spell_data = json.loads(response.read())
                            formatted_data = format_spell_data(spell_data)
                            return [types.TextContent(type="text", text=formatted_data)]
                        else:
                            return [types.TextContent(type="text", text=f"Spell '{arguments.get('name', '')}' not found.")]
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        # Try searching by name if direct access fails
                        try:
                            search_url = f"{API_BASE_URL}/spells?name={urllib.parse.quote(arguments.get('name', ''))}"
                            with urllib.request.urlopen(search_url) as search_response:
                                if search_response.status == 200:
                                    search_results = json.loads(
                                        search_response.read())
                                    if search_results.get("count", 0) > 0:
                                        spell_url = search_results["results"][0]["url"].lstrip(
                                            "/api/")
                                        with urllib.request.urlopen(f"{API_BASE_URL}/{spell_url}") as spell_response:
                                            if spell_response.status == 200:
                                                spell_data = json.loads(
                                                    spell_response.read())
                                                formatted_data = format_spell_data(
                                                    spell_data)
                                                return [types.TextContent(type="text", text=formatted_data)]
                                    return [types.TextContent(type="text", text=f"No spells found matching '{arguments.get('name', '')}'.")]
                        except Exception as search_e:
                            return [types.TextContent(type="text", text=f"Error searching for spell: {str(search_e)}")]
                    return [types.TextContent(type="text", text=f"Error accessing spell information: {str(e)}")]
                except Exception as e:
                    return [types.TextContent(type="text", text=f"Error: {str(e)}")]

            elif name == "get_class":
                class_name = arguments.get("name", "").lower()
                if not class_name:
                    return [types.TextContent(type="text", text="Please provide a class name.")]

                try:
                    with urllib.request.urlopen(f"{API_BASE_URL}/classes/{class_name}") as response:
                        if response.status == 200:
                            class_data = json.loads(response.read())
                            formatted_data = format_class_data(class_data)
                            return [types.TextContent(type="text", text=formatted_data)]
                        else:
                            return [types.TextContent(type="text", text=f"Class '{arguments.get('name', '')}' not found.")]
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        return [types.TextContent(type="text", text=f"Class '{arguments.get('name', '')}' not found.")]
                    return [types.TextContent(type="text", text=f"Error accessing class information: {str(e)}")]
                except Exception as e:
                    return [types.TextContent(type="text", text=f"Error: {str(e)}")]

            elif name == "search_api":
                endpoint = arguments.get("endpoint", "")
                query = arguments.get("query", "")

                if not endpoint or not query:
                    return [types.TextContent(type="text", text="Please provide both an endpoint and a query.")]

                valid_endpoints = ["monsters", "spells", "classes",
                                   "races", "equipment", "magic-items", "features"]
                if endpoint not in valid_endpoints:
                    return [types.TextContent(type="text", text=f"Error: Invalid endpoint. Valid options are: {', '.join(valid_endpoints)}")]

                try:
                    search_url = f"{API_BASE_URL}/{endpoint}?name={urllib.parse.quote(query)}"
                    print(
                        f"Searching API with URL: {search_url}", file=sys.stderr)

                    with urllib.request.urlopen(search_url) as response:
                        if response.status == 200:
                            results = json.loads(response.read())
                            if results.get("count", 0) == 0:
                                return [types.TextContent(type="text", text=f"No results found for '{query}' in {endpoint}.")]

                            results_text = f"Found {results['count']} results for '{query}' in '{endpoint}':\n\n"
                            for result in results.get("results", []):
                                results_text += f"- {result.get('name')}\n"

                            return [types.TextContent(type="text", text=results_text)]
                except urllib.error.HTTPError as e:
                    return [types.TextContent(type="text", text=f"Error searching the D&D API: {str(e)}")]
                except Exception as e:
                    return [types.TextContent(type="text", text=f"Error: {str(e)}")]

            else:
                return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
        except Exception as e:
            print(f"Error in call_tool: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    # Helper functions for formatting data

    def format_monster_data(data):
        """Format monster data into a readable string."""
        try:
            result = f"# {data.get('name', 'Unknown Monster')}\n\n"

            # Basic information
            result += f"**Type:** {data.get('size', '')} {data.get('type', '')}"
            if data.get('subtype'):
                result += f" ({data.get('subtype')})"
            result += f", {data.get('alignment', '')}\n"

            result += f"**Armor Class:** {data.get('armor_class', 0)}"
            if isinstance(data.get('armor_class'), list):
                ac_items = data.get('armor_class', [])
                if ac_items and len(ac_items) > 0:
                    ac_value = ac_items[0].get('value', 0)
                    ac_type = ac_items[0].get('type', '')
                    result += f" ({ac_value}"
                    if ac_type:
                        result += f", {ac_type}"
                    result += ")"
            result += "\n"

            result += f"**Hit Points:** {data.get('hit_points', 0)} ({data.get('hit_dice', '')})\n"
            result += f"**Speed:** {', '.join([f'{k} {v} ft.' for k,
                                              v in data.get('speed', {}).items()])}\n\n"

            # Ability scores
            result += "| STR | DEX | CON | INT | WIS | CHA |\n"
            result += "|-----|-----|-----|-----|-----|-----|\n"
            result += f"| {data.get('strength', 0)} ({format_ability_modifier(data.get('strength', 0))}) "
            result += f"| {data.get('dexterity', 0)} ({format_ability_modifier(data.get('dexterity', 0))}) "
            result += f"| {data.get('constitution', 0)} ({format_ability_modifier(data.get('constitution', 0))}) "
            result += f"| {data.get('intelligence', 0)} ({format_ability_modifier(data.get('intelligence', 0))}) "
            result += f"| {data.get('wisdom', 0)} ({format_ability_modifier(data.get('wisdom', 0))}) "
            result += f"| {data.get('charisma', 0)} ({format_ability_modifier(data.get('charisma', 0))}) |\n\n"

            # Saving throws
            if data.get('proficiencies'):
                saving_throws = [p for p in data.get(
                    'proficiencies', []) if 'saving-throw' in p.get('proficiency', {}).get('index', '')]
                if saving_throws:
                    saves = [
                        f"{p.get('proficiency', {}).get('name', '').replace('Saving Throw: ', '')}: +{p.get('value', 0)}" for p in saving_throws]
                    result += f"**Saving Throws:** {', '.join(saves)}\n"

            # Skills
            if data.get('proficiencies'):
                skills = [p for p in data.get('proficiencies', []) if 'skill' in p.get(
                    'proficiency', {}).get('index', '')]
                if skills:
                    skill_list = [
                        f"{p.get('proficiency', {}).get('name', '').replace('Skill: ', '')}: +{p.get('value', 0)}" for p in skills]
                    result += f"**Skills:** {', '.join(skill_list)}\n"

            # Damage vulnerabilities, resistances, immunities
            if data.get('damage_vulnerabilities'):
                result += f"**Damage Vulnerabilities:** {', '.join(data.get('damage_vulnerabilities', []))}\n"

            if data.get('damage_resistances'):
                result += f"**Damage Resistances:** {', '.join(data.get('damage_resistances', []))}\n"

            if data.get('damage_immunities'):
                result += f"**Damage Immunities:** {', '.join(data.get('damage_immunities', []))}\n"

            if data.get('condition_immunities'):
                conditions = [c.get('name', '')
                              for c in data.get('condition_immunities', [])]
                if conditions:
                    result += f"**Condition Immunities:** {', '.join(conditions)}\n"

            # Senses and languages
            if data.get('senses'):
                senses = [f"{k}: {v}" for k,
                          v in data.get('senses', {}).items()]
                result += f"**Senses:** {', '.join(senses)}\n"

            if data.get('languages'):
                result += f"**Languages:** {data.get('languages', '')}\n"

            result += f"**Challenge:** {data.get('challenge_rating', '0')} ({calculate_xp(data.get('challenge_rating', 0))} XP)\n\n"

            # Special abilities
            if data.get('special_abilities'):
                result += "## Special Abilities\n\n"
                for ability in data.get('special_abilities', []):
                    result += f"**{ability.get('name', '')}:** {ability.get('desc', '')}\n\n"

            # Actions
            if data.get('actions'):
                result += "## Actions\n\n"
                for action in data.get('actions', []):
                    result += f"**{action.get('name', '')}:** {action.get('desc', '')}\n\n"

            # Legendary actions
            if data.get('legendary_actions'):
                result += "## Legendary Actions\n\n"
                if data.get('legendary_desc'):
                    result += f"{data.get('legendary_desc', '')}\n\n"
                for action in data.get('legendary_actions', []):
                    result += f"**{action.get('name', '')}:** {action.get('desc', '')}\n\n"

            return result
        except Exception as e:
            print(f"Error formatting monster data: {e}", file=sys.stderr)
            return f"Error formatting monster data: {str(e)}"

    def format_ability_modifier(score):
        """Calculate and format ability score modifier."""
        modifier = (score - 10) // 2
        if modifier >= 0:
            return f"+{modifier}"
        return str(modifier)

    def calculate_xp(cr):
        """Calculate XP from Challenge Rating."""
        xp_by_cr = {
            0: 0, 0.125: 25, 0.25: 50, 0.5: 100, 1: 200, 2: 450, 3: 700, 4: 1100, 5: 1800,
            6: 2300, 7: 2900, 8: 3900, 9: 5000, 10: 5900, 11: 7200, 12: 8400, 13: 10000,
            14: 11500, 15: 13000, 16: 15000, 17: 18000, 18: 20000, 19: 22000, 20: 25000,
            21: 33000, 22: 41000, 23: 50000, 24: 62000, 25: 75000, 26: 90000, 27: 105000,
            28: 120000, 29: 135000, 30: 155000
        }

        try:
            cr_value = float(cr)
            return xp_by_cr.get(cr_value, 0)
        except (ValueError, TypeError):
            return 0

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
