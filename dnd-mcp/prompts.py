#!/usr/bin/env python3
import sys
from mcp.types import PromptMessage as UserMessage, PromptMessage as AssistantMessage
from mcp.types import TextContent


def register_prompts(app):
    """Register simple prompts using FastMCP's syntax."""
    print("Registering simple FastMCP prompts...", file=sys.stderr)

    @app.prompt()
    def character_concept(class_name: str, race: str, background: str = None) -> str:
        """Generate a D&D character concept"""
        prompt_text = f"Create a concept for a D&D {race} {class_name} character"
        if background:
            prompt_text += f" with a {background} background"
        prompt_text += "."

        prompt_text += "\n\nPlease create a compelling character concept that includes:\n1. A brief backstory\n2. Personality traits\n3. Goals and motivations\n4. A unique quirk or characteristic"

        return prompt_text

    @app.prompt()
    def adventure_hook(setting: str, level_range: str, theme: str = None) -> str:
        """Generate a D&D adventure hook"""
        prompt_text = f"Create a D&D adventure hook set in a {setting} for character levels {level_range}"
        if theme:
            prompt_text += f" with a {theme} theme"
        prompt_text += "."

        prompt_text += "\n\nInclude:\n1. A compelling hook to draw players in\n2. Key NPCs involved\n3. Potential challenges and encounters\n4. Possible rewards"

        return prompt_text

    @app.prompt()
    def spell_selection(class_name: str, level: str, focus: str = None) -> str:
        """Get spell recommendations for your character"""
        prompt_text = f"Recommend spells for a level {level} {class_name}"
        if focus:
            prompt_text += f" focusing on {focus} spells"
        prompt_text += "."

        prompt_text += "\n\nPlease provide:\n1. Recommended cantrips\n2. Recommended spells by level\n3. Spell combinations that work well together\n4. Situational spells that could be useful"

        return prompt_text

    @app.prompt()
    def encounter_builder(party_level: str, party_size: str, difficulty: str, environment: str = None) -> list:
        """Build a balanced combat encounter"""
        prompt_text = f"Build a {difficulty} combat encounter for {party_size} players at level {party_level}"
        if environment:
            prompt_text += f" in a {environment} environment"
        prompt_text += "."

        prompt_text += "\n\nPlease design an encounter that includes:"
        prompt_text += "\n1. A balanced mix of monsters"
        prompt_text += "\n2. Interesting terrain features and environmental elements"
        prompt_text += "\n3. Tactical considerations and monster strategies"
        prompt_text += "\n4. Appropriate treasure and rewards"
        prompt_text += "\n5. Potential for both combat and non-combat resolution"

        # Return as a list of messages for more structured conversation
        return [
            UserMessage(role="user", content=TextContent(
                type="text", text=prompt_text)),
            AssistantMessage(role="assistant", content=TextContent(
                type="text", text="I'll design a balanced encounter for you. Let me know if you have any specific themes or enemies in mind!"))
        ]

    @app.prompt()
    def magic_item_finder(character_level: str, character_class: str, rarity: str = None) -> str:
        """Find appropriate magic items for your character"""
        prompt_text = f"Recommend magic items for a level {character_level} {character_class}"
        if rarity:
            prompt_text += f" of {rarity} rarity"
        prompt_text += "."

        prompt_text += "\n\nPlease provide:"
        prompt_text += "\n1. Recommendations for appropriate magic items"
        prompt_text += "\n2. How these items would benefit this character class"
        prompt_text += "\n3. Creative ways to incorporate these items into a character's story"
        prompt_text += "\n4. Alternative items that might not be in the standard rules"

        return prompt_text

    print("Simple FastMCP prompts registered successfully", file=sys.stderr)
