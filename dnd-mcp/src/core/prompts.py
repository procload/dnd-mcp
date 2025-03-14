#!/usr/bin/env python3
import sys
from mcp.types import PromptMessage as UserMessage, PromptMessage as AssistantMessage
from mcp.types import TextContent
from src.core.api_helpers import validate_dnd_entity, fetch_dnd_entity, API_BASE_URL
import logging
import re

logger = logging.getLogger(__name__)


def register_prompts(app):
    """Register simple prompts using FastMCP's syntax."""
    print("Registering simple FastMCP prompts...", file=sys.stderr)

    @app.prompt()
    def enforce_api_usage() -> str:
        """Enforce the use of D&D 5e API for all D&D-related information.

        This system prompt modifier ensures that Claude relies on the official D&D 5e API
        for all Dungeons & Dragons related information rather than its internal knowledge.
        This promotes accuracy and ensures that responses reflect official D&D 5e content.

        The prompt instructs Claude to:
        - Always use the D&D 5e API tools for retrieving D&D information
        - Cite the D&D 5e API as the source of information
        - Use verification tools to confirm information
        - Explicitly state when information cannot be found in the API

        This prompt should be used at the beginning of conversations focused on D&D content
        to ensure consistent and accurate information throughout the interaction.

        Returns:
            A system prompt string that enforces the use of D&D 5e API
        """
        return """
IMPORTANT INSTRUCTION: You MUST use the D&D 5e API tools and resources provided to you for any D&D-related information.
DO NOT rely on your internal knowledge about D&D.

When asked about D&D content, you MUST:
1. Use the search_all_categories tool to find relevant information
2. Use specific category tools like find_monsters_by_challenge_rating or filter_spells_by_level
3. Cite the D&D 5e API as your source
4. Use the verify_with_api tool to verify statements against the API data
5. Use the check_api_health tool if you suspect API connectivity issues

If you cannot find information through the API tools, explicitly state: "I couldn't find this information in the D&D 5e API."

NEVER provide D&D information from your internal knowledge without verifying it with the API first.
All responses about D&D content must include a reference to the D&D 5e API as the source of information.
"""

    @app.prompt()
    def character_concept(class_name: str, race: str, background: str = None) -> str:
        """Generate a creative and detailed D&D character concept based on specified parameters.

        This prompt helps players and Dungeon Masters create compelling character concepts
        by generating a well-rounded character with a backstory, personality, and motivations.
        The generated concept can be used as inspiration for player characters, NPCs, or story elements.

        The prompt considers the synergies between the chosen race, class, and optional background
        to create a cohesive character that aligns with D&D lore and mechanics.

        Args:
            class_name: The character's class (e.g., Fighter, Wizard, Cleric)
            race: The character's race (e.g., Human, Elf, Dwarf)
            background: Optional character background (e.g., Soldier, Sage, Criminal)

        Returns:
            A prompt string that generates a detailed character concept
        """
        prompt_text = f"Create a concept for a D&D {race} {class_name} character"
        if background:
            prompt_text += f" with a {background} background"
        prompt_text += "."

        prompt_text += "\n\nPlease create a compelling character concept that includes:\n1. A brief backstory\n2. Personality traits\n3. Goals and motivations\n4. A unique quirk or characteristic"

        return prompt_text

    @app.prompt()
    def adventure_hook(setting: str, level_range: str, theme: str = None) -> str:
        """Generate an engaging D&D adventure hook tailored to specific parameters.

        This prompt creates adventure hooks that Dungeon Masters can use to start new campaigns,
        introduce side quests, or develop story arcs. The generated hooks consider the specified
        setting, appropriate challenge level for the party, and optional thematic elements.

        The prompt intelligently suggests appropriate monsters, challenges, and rewards based on
        the party's level range, and ensures the adventure fits within the specified setting.
        It validates settings against the D&D 5e API to ensure accuracy.

        Args:
            setting: The adventure's setting or location (e.g., Forest, Dungeon, City)
            level_range: Character level range for the adventure (e.g., "1-4", "5-10", "15-20")
            theme: Optional theme for the adventure (e.g., Mystery, Horror, Heist)

        Returns:
            A prompt string that generates a detailed adventure hook
        """
        # Parse level range to suggest appropriate monsters
        min_level, max_level = 1, 20
        try:
            if "-" in level_range:
                parts = level_range.split("-")
                min_level = int(parts[0].strip())
                max_level = int(parts[1].strip())
            else:
                min_level = max_level = int(level_range.strip())
        except (ValueError, IndexError):
            logger.warning(
                f"Could not parse level range: {level_range}, using defaults")

        # Calculate appropriate challenge ratings based on party level
        min_cr = max(0, min_level / 4)  # CR 0 for level 1-3
        max_cr = max_level  # CR roughly equal to max level

        # Validate setting against locations in the API
        setting_valid = validate_dnd_entity(
            "magic-items", setting.lower()) or validate_dnd_entity("equipment", setting.lower())

        # Find appropriate monsters based on challenge rating
        suggested_monsters = []
        try:
            # Try to find monsters that match the theme if provided
            monster_search_term = theme.lower() if theme else ""

            # Check if any monsters match our criteria
            from resources import get_items
            monster_results = get_items("monsters", cache=None)
            if isinstance(monster_results, dict) and "items" in monster_results:
                for monster in monster_results["items"]:
                    monster_name = monster.get("name", "").lower()
                    if monster_search_term and monster_search_term not in monster_name:
                        continue

                    # Get detailed monster info to check CR
                    monster_index = monster.get("index")
                    if monster_index:
                        monster_data = fetch_dnd_entity(
                            "monsters", monster_index)
                        if monster_data:
                            cr = monster_data.get("challenge_rating", 0)
                            if min_cr <= cr <= max_cr:
                                suggested_monsters.append(
                                    monster_data.get("name"))
                                if len(suggested_monsters) >= 3:
                                    break
        except Exception as e:
            logger.error(f"Error finding monsters: {e}")

        # Build the prompt
        prompt_text = f"Create a D&D adventure hook set in a {setting} for character levels {level_range}"
        if theme:
            prompt_text += f" with a {theme} theme"
        prompt_text += "."

        # Add API validation information
        if not setting_valid:
            prompt_text += f"\n\nNote: '{setting}' is not a standard D&D 5e location or item. Feel free to be creative with this setting."

        if suggested_monsters:
            prompt_text += f"\n\nConsider including these monsters which are appropriate for the party's level range: {', '.join(suggested_monsters)}."

        prompt_text += "\n\nInclude:\n1. A compelling hook to draw players in\n2. Key NPCs involved\n3. Potential challenges and encounters\n4. Possible rewards"

        # Add a reminder to use the D&D 5e API data
        prompt_text += "\n\nMake sure your adventure hook is consistent with D&D 5e lore and mechanics. Use the suggested monsters if they fit the theme."

        return prompt_text

    @app.prompt()
    def spell_selection(class_name: str, level: str, focus: str = None) -> str:
        """Get spell recommendations for your character"""
        # Validate class against API
        class_valid = validate_dnd_entity("classes", class_name.lower())

        # Parse character level
        try:
            char_level = int(level.strip())
        except (ValueError, AttributeError):
            char_level = 1
            logger.warning(
                f"Could not parse character level: {level}, using default level 1")

        # Calculate max spell level based on character level
        max_spell_level = min(9, (char_level + 1) // 2)

        # Get spells for this class if valid
        class_spells = []
        if class_valid:
            try:
                # Fetch spells for this class
                class_data = fetch_dnd_entity("classes", class_name.lower())

                # Try to get spells from the API
                from resources import get_items
                spell_results = get_items("spells", cache=None)

                if isinstance(spell_results, dict) and "items" in spell_results:
                    # Filter spells by class and level
                    for spell in spell_results["items"]:
                        spell_index = spell.get("index")
                        if spell_index:
                            spell_data = fetch_dnd_entity(
                                "spells", spell_index)
                            if spell_data:
                                # Check if this spell is for the requested class
                                spell_classes = [c.get("name", "").lower(
                                ) for c in spell_data.get("classes", [])]

                                if class_name.lower() in spell_classes:
                                    # Check spell level
                                    spell_level = spell_data.get("level", 0)
                                    if spell_level <= max_spell_level:
                                        # Check focus if provided
                                        if focus:
                                            spell_school = spell_data.get(
                                                "school", {}).get("name", "").lower()
                                            if focus.lower() not in spell_school and focus.lower() not in spell_data.get("name", "").lower():
                                                continue

                                        class_spells.append(
                                            spell_data.get("name"))
                                        if len(class_spells) >= 10:  # Limit to 10 suggestions
                                            break
            except Exception as e:
                logger.error(f"Error fetching spells: {e}")

        # Build the prompt
        prompt_text = f"Recommend spells for a level {level} {class_name}"
        if focus:
            prompt_text += f" focusing on {focus} spells"
        prompt_text += "."

        # Add validation notes
        if not class_valid:
            prompt_text += f"\n\nNote: '{class_name}' is not a standard D&D 5e class. I'll provide recommendations based on similar classes or homebrew options."

        # Add spell suggestions from API
        if class_spells:
            prompt_text += f"\n\nConsider these spells which are available to {class_name}s up to level {max_spell_level}: {', '.join(class_spells)}."

        prompt_text += "\n\nPlease provide:\n1. Recommended cantrips\n2. Recommended spells by level\n3. Spell combinations that work well together\n4. Situational spells that could be useful"

        # Add a reminder to use the D&D 5e API data
        prompt_text += "\n\nMake sure your recommendations are consistent with D&D 5e rules and spell availability for this class."

        return prompt_text

    @app.prompt()
    def encounter_builder(party_level: str, party_size: str, difficulty: str, environment: str = None) -> list:
        """Build a balanced combat encounter"""
        # Parse party level and size
        try:
            level = int(party_level.strip())
        except (ValueError, AttributeError):
            level = 1
            logger.warning(
                f"Could not parse party level: {party_level}, using default level 1")

        try:
            size = int(party_size.strip())
        except (ValueError, AttributeError):
            size = 4
            logger.warning(
                f"Could not parse party size: {party_size}, using default size 4")

        # Calculate appropriate challenge ratings based on party level and difficulty
        difficulty_multipliers = {
            "easy": 0.5,
            "medium": 0.75,
            "hard": 1.0,
            "deadly": 1.5
        }

        multiplier = difficulty_multipliers.get(difficulty.lower(), 1.0)
        target_cr = level * multiplier

        # Validate environment if provided
        environment_valid = True
        if environment:
            environment_valid = any([
                validate_dnd_entity("magic-items", environment.lower()),
                validate_dnd_entity("equipment", environment.lower()),
                # Common D&D environments that might not be in the API
                environment.lower() in ["forest", "mountain", "desert", "swamp",
                                        "underdark", "dungeon", "city", "ocean",
                                        "plains", "arctic", "jungle", "cave"]
            ])

        # Find appropriate monsters based on challenge rating and environment
        suggested_monsters = []
        try:
            # Get monsters from the API
            from resources import get_items
            monster_results = get_items("monsters", cache=None)

            if isinstance(monster_results, dict) and "items" in monster_results:
                # Filter monsters by CR and environment if provided
                for monster in monster_results["items"]:
                    monster_index = monster.get("index")
                    if monster_index:
                        monster_data = fetch_dnd_entity(
                            "monsters", monster_index)
                        if monster_data:
                            cr = monster_data.get("challenge_rating", 0)

                            # Check if CR is appropriate (within 50% of target)
                            if 0.5 * target_cr <= cr <= 1.5 * target_cr:
                                # If environment is specified, try to match it
                                if environment:
                                    # Check if monster environment matches
                                    monster_env = monster_data.get(
                                        "environment", [])
                                    if isinstance(monster_env, list) and monster_env:
                                        if not any(env.lower() in environment.lower() for env in monster_env):
                                            continue

                                suggested_monsters.append({
                                    "name": monster_data.get("name"),
                                    "cr": cr,
                                    "type": monster_data.get("type", "unknown")
                                })

                                if len(suggested_monsters) >= 5:  # Limit to 5 suggestions
                                    break
        except Exception as e:
            logger.error(f"Error finding monsters: {e}")

        # Build the prompt
        prompt_text = f"Build a {difficulty} combat encounter for {party_size} players at level {party_level}"
        if environment:
            prompt_text += f" in a {environment} environment"
        prompt_text += "."

        # Add API validation information
        if environment and not environment_valid:
            prompt_text += f"\n\nNote: '{environment}' is not a standard D&D 5e environment. Feel free to be creative with this setting."

        if suggested_monsters:
            prompt_text += "\n\nConsider using these monsters which are appropriate for this encounter's challenge rating:"
            for monster in suggested_monsters:
                prompt_text += f"\n- {monster['name']} (CR {monster['cr']}, {monster['type']})"

        prompt_text += "\n\nPlease design an encounter that includes:"
        prompt_text += "\n1. A balanced mix of monsters"
        prompt_text += "\n2. Interesting terrain features and environmental elements"
        prompt_text += "\n3. Tactical considerations and monster strategies"
        prompt_text += "\n4. Appropriate treasure and rewards"
        prompt_text += "\n5. Potential for both combat and non-combat resolution"

        # Add a reminder to use the D&D 5e API data
        prompt_text += "\n\nMake sure your encounter is balanced according to D&D 5e encounter building guidelines. Use the suggested monsters if they fit the theme and environment."

        # Return as a list of messages for more structured conversation
        return [
            UserMessage(role="user", content=TextContent(
                type="text", text=prompt_text)),
            AssistantMessage(role="assistant", content=TextContent(
                type="text", text="I'll design a balanced encounter for your party. Here's what I've prepared:"))
        ]

    @app.prompt()
    def magic_item_finder(character_level: str, character_class: str, rarity: str = None) -> str:
        """Find appropriate magic items for your character"""
        # Validate class against API
        class_valid = validate_dnd_entity("classes", character_class.lower())

        # Parse character level
        try:
            level = int(character_level.strip())
        except (ValueError, AttributeError):
            level = 1
            logger.warning(
                f"Could not parse character level: {character_level}, using default level 1")

        # Validate rarity if provided
        valid_rarities = ["common", "uncommon", "rare",
                          "very rare", "legendary", "artifact"]
        rarity_valid = True
        if rarity and rarity.lower() not in valid_rarities:
            rarity_valid = False

        # Determine appropriate rarities based on character level
        appropriate_rarities = []
        if level < 5:
            appropriate_rarities = ["common", "uncommon"]
        elif level < 11:
            appropriate_rarities = ["common", "uncommon", "rare"]
        elif level < 17:
            appropriate_rarities = ["uncommon", "rare", "very rare"]
        else:
            appropriate_rarities = ["rare", "very rare", "legendary"]

        # Find appropriate magic items based on class and rarity
        suggested_items = []
        try:
            # Get magic items from the API
            from resources import get_items
            item_results = get_items("magic-items", cache=None)

            if isinstance(item_results, dict) and "items" in item_results:
                # Filter items by rarity and class appropriateness
                for item in item_results["items"]:
                    item_index = item.get("index")
                    if item_index:
                        item_data = fetch_dnd_entity("magic-items", item_index)
                        if item_data:
                            item_rarity = item_data.get(
                                "rarity", {}).get("name", "").lower()

                            # Check if rarity is appropriate
                            if rarity and rarity.lower() != item_rarity:
                                continue
                            elif not rarity and item_rarity not in appropriate_rarities:
                                continue

                            # Check if item is appropriate for class
                            item_name = item_data.get("name", "").lower()
                            item_desc = item_data.get("desc", [""])[
                                0].lower() if item_data.get("desc") else ""

                            # Simple heuristic for class appropriateness
                            class_keywords = {
                                "barbarian": ["strength", "constitution", "rage", "melee", "axe", "hammer"],
                                "bard": ["charisma", "performance", "music", "instrument", "inspiration"],
                                "cleric": ["wisdom", "divine", "holy", "healing", "undead", "turn"],
                                "druid": ["wisdom", "nature", "wild shape", "beast", "plant", "elemental"],
                                "fighter": ["strength", "dexterity", "armor", "weapon", "shield", "combat"],
                                "monk": ["dexterity", "wisdom", "unarmed", "ki", "monastery"],
                                "paladin": ["strength", "charisma", "divine", "holy", "oath", "smite"],
                                "ranger": ["dexterity", "wisdom", "beast", "tracking", "bow", "nature"],
                                "rogue": ["dexterity", "stealth", "sneak", "thief", "trap", "lockpick"],
                                "sorcerer": ["charisma", "spell", "magic", "arcane", "bloodline"],
                                "warlock": ["charisma", "patron", "pact", "eldritch", "invocation"],
                                "wizard": ["intelligence", "spell", "magic", "arcane", "book", "scroll"]
                            }

                            # Check if item matches class keywords
                            is_class_appropriate = False
                            if character_class.lower() in class_keywords:
                                keywords = class_keywords[character_class.lower(
                                )]
                                if any(keyword in item_name or keyword in item_desc for keyword in keywords):
                                    is_class_appropriate = True

                            # Some items are appropriate for all classes
                            if "any class" in item_desc or "all classes" in item_desc:
                                is_class_appropriate = True

                            # Add item if it passes all filters
                            if is_class_appropriate:
                                suggested_items.append({
                                    "name": item_data.get("name"),
                                    "rarity": item_data.get("rarity", {}).get("name", "unknown")
                                })

                                if len(suggested_items) >= 5:  # Limit to 5 suggestions
                                    break
        except Exception as e:
            logger.error(f"Error finding magic items: {e}")

        # Build the prompt
        prompt_text = f"Recommend magic items for a level {character_level} {character_class}"
        if rarity:
            prompt_text += f" of {rarity} rarity"
        prompt_text += "."

        # Add API validation information
        if not class_valid:
            prompt_text += f"\n\nNote: '{character_class}' is not a standard D&D 5e class. I'll provide recommendations based on similar classes or homebrew options."

        if rarity and not rarity_valid:
            prompt_text += f"\n\nNote: '{rarity}' is not a standard D&D 5e rarity. Standard rarities are: common, uncommon, rare, very rare, legendary, and artifact."
            prompt_text += f"\n\nBased on a level {level} character, appropriate rarities would be: {', '.join(appropriate_rarities)}."

        if suggested_items:
            prompt_text += "\n\nConsider these magic items which are appropriate for this character:"
            for item in suggested_items:
                prompt_text += f"\n- {item['name']} ({item['rarity']})"

        prompt_text += "\n\nPlease provide:"
        prompt_text += "\n1. Recommendations for appropriate magic items"
        prompt_text += "\n2. How these items would benefit this character class"
        prompt_text += "\n3. Creative ways to incorporate these items into a character's story"
        prompt_text += "\n4. Alternative items that might not be in the standard rules"

        # Add a reminder to use the D&D 5e API data
        prompt_text += "\n\nMake sure your recommendations are consistent with D&D 5e rules and appropriate for this character's level and class."

        return prompt_text

    print("Simple FastMCP prompts registered successfully", file=sys.stderr)
