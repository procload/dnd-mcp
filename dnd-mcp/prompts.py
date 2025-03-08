#!/usr/bin/env python3
import sys
import json
import traceback
import urllib.request
import mcp.types as types
from api_helpers import validate_dnd_entity, fetch_dnd_entity, get_primary_ability, get_asi_text, API_BASE_URL


def register_prompts(app):
    """Register prompt handlers with the app."""
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
