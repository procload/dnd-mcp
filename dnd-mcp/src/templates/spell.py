"""
Spell template module for D&D Knowledge Navigator.

This module contains templates for formatting spell data in markdown.
"""

import sys
from src.templates.config import is_template_enabled, get_template_setting, get_formatting_option


def format_spell_card(data):
    """
    Format spell data into a D&D-style spell card using markdown.

    Args:
        data: Spell data dictionary from the D&D 5e API

    Returns:
        Formatted markdown string
    """
    # Check if templates are enabled
    if not is_template_enabled("spell"):
        return format_spell_plain(data)

    use_emojis = get_formatting_option("use_emojis", False)
    show_components_detail = get_template_setting(
        "spell", "show_components_detail", True)

    try:
        spell_name = data.get('name', 'Unknown Spell')
        spell_emoji = "✨ " if use_emojis else ""
        result = f"# {spell_emoji}{spell_name}\n\n"

        # Basic information
        level_text = "Cantrip" if data.get(
            'level') == 0 else f"{data.get('level', 0)}-level"
        school = data.get('school', {}).get('name', '')
        result += f"*{level_text} {school.lower()}*\n\n"

        # Casting time, range, components
        result += f"**Casting Time:** {data.get('casting_time', '')}\n"
        result += f"**Range:** {data.get('range', '')}\n"

        # Components
        components = data.get('components', [])
        component_str = ", ".join(components)

        if show_components_detail and 'material' in components and data.get('material'):
            component_str += f" ({data.get('material', '')})"

        result += f"**Components:** {component_str}\n"

        # Duration and concentration
        duration = data.get('duration', '')
        if data.get('concentration', False):
            duration = f"Concentration, {duration}"
        result += f"**Duration:** {duration}\n\n"

        # Description
        if data.get('desc'):
            for paragraph in data.get('desc', []):
                result += f"{paragraph}\n\n"

        # Higher levels
        if data.get('higher_level'):
            higher_level_emoji = "🔼 " if use_emojis else ""
            result += f"**{higher_level_emoji}At Higher Levels:** "
            for paragraph in data.get('higher_level', []):
                result += f"{paragraph}\n\n"

        # Classes
        if data.get('classes'):
            class_names = [c.get('name', '') for c in data.get('classes', [])]
            result += f"**Classes:** {', '.join(class_names)}\n\n"

        return result
    except Exception as e:
        # Fallback to plain formatting if there's an error
        print(f"Error formatting spell card: {e}", file=sys.stderr)
        return format_spell_plain(data)


def format_spell_plain(data):
    """
    Format spell data into a simple plain text format.

    Args:
        data: Spell data dictionary from the D&D 5e API

    Returns:
        Formatted plain text string
    """
    try:
        result = f"{data.get('name', 'Unknown Spell')}\n\n"

        level_text = "Cantrip" if data.get(
            'level') == 0 else f"Level {data.get('level', 0)}"
        school = data.get('school', {}).get('name', '')
        result += f"{level_text} {school}\n"

        result += f"Casting Time: {data.get('casting_time', '')}\n"
        result += f"Range: {data.get('range', '')}\n"
        result += f"Components: {', '.join(data.get('components', []))}\n"

        duration = data.get('duration', '')
        if data.get('concentration', False):
            duration = f"Concentration, {duration}"
        result += f"Duration: {duration}\n\n"

        # Description (simplified)
        if data.get('desc'):
            result += "Description: "
            result += " ".join(data.get('desc', []))[:200]
            if len(" ".join(data.get('desc', []))) > 200:
                result += "..."
            result += "\n\n"

        # Classes
        if data.get('classes'):
            class_names = [c.get('name', '') for c in data.get('classes', [])]
            result += f"Classes: {', '.join(class_names)}\n"

        return result
    except Exception as e:
        # Ultra-fallback for any errors
        print(f"Error in plain spell formatting: {e}", file=sys.stderr)
        return str(data)
