"""
Equipment template module for D&D Knowledge Navigator.

This module contains templates for formatting equipment data in markdown.
"""

import sys
from src.templates.config import is_template_enabled, get_template_setting, get_formatting_option


def format_equipment_card(data):
    """
    Format equipment data into a D&D-style equipment card using markdown.

    Args:
        data: Equipment data dictionary from the D&D 5e API

    Returns:
        Formatted markdown string
    """
    # Check if templates are enabled
    if not is_template_enabled("equipment"):
        return format_equipment_plain(data)

    use_emojis = get_formatting_option("use_emojis", False)
    show_cost_details = get_template_setting(
        "equipment", "show_cost_details", True)

    try:
        item_name = data.get('name', 'Unknown Item')

        # Choose emoji based on equipment category
        item_emoji = ""
        if use_emojis:
            category = data.get('equipment_category', {}
                                ).get('name', '').lower()
            if 'weapon' in category:
                item_emoji = "⚔️ "
            elif 'armor' in category:
                item_emoji = "🛡️ "
            elif 'potion' in category:
                item_emoji = "🧪 "
            elif 'ring' in category:
                item_emoji = "💍 "
            elif 'wand' in category or 'staff' in category:
                item_emoji = "🪄 "
            elif 'tool' in category:
                item_emoji = "🔧 "
            elif 'mount' in category or 'vehicle' in category:
                item_emoji = "🐎 "
            else:
                item_emoji = "📦 "

        result = f"# {item_emoji}{item_name}\n\n"

        # Category and subcategory
        category = data.get('equipment_category', {}).get('name', '')
        result += f"*{category}*"

        if data.get('gear_category'):
            result += f" (*{data.get('gear_category', {}).get('name', '')}*)"
        elif data.get('weapon_category'):
            result += f" (*{data.get('weapon_category')}*)"
        elif data.get('armor_category'):
            result += f" (*{data.get('armor_category')}*)"
        elif data.get('tool_category'):
            result += f" (*{data.get('tool_category')}*)"
        elif data.get('vehicle_category'):
            result += f" (*{data.get('vehicle_category')}*)"

        result += "\n\n"

        # Cost
        if data.get('cost') and show_cost_details:
            quantity = data.get('cost', {}).get('quantity', 0)
            unit = data.get('cost', {}).get('unit', '')
            result += f"**Cost:** {quantity} {unit}\n"

        # Weight
        if data.get('weight'):
            result += f"**Weight:** {data.get('weight')} lb.\n"

        # Armor specific properties
        if data.get('armor_class'):
            ac_base = data.get('armor_class', {}).get('base', 0)
            dex_bonus = data.get('armor_class', {}).get('dex_bonus', False)
            max_bonus = data.get('armor_class', {}).get('max_bonus', None)

            result += f"**Armor Class:** {ac_base}"
            if dex_bonus:
                if max_bonus is not None:
                    result += f" + DEX (max {max_bonus})"
                else:
                    result += " + DEX"
            result += "\n"

            if data.get('str_minimum'):
                result += f"**Strength Required:** {data.get('str_minimum')}\n"

            if data.get('stealth_disadvantage'):
                result += "**Stealth:** Disadvantage\n"

        # Weapon specific properties
        if data.get('damage'):
            damage_dice = data.get('damage', {}).get('damage_dice', '')
            damage_type = data.get('damage', {}).get(
                'damage_type', {}).get('name', '')
            result += f"**Damage:** {damage_dice} {damage_type}\n"

        if data.get('range'):
            normal_range = data.get('range', {}).get('normal', 0)
            long_range = data.get('range', {}).get('long', 0)
            if long_range > 0:
                result += f"**Range:** {normal_range}/{long_range} ft.\n"
            else:
                result += f"**Range:** {normal_range} ft.\n"

        if data.get('properties'):
            properties = [p.get('name', '')
                          for p in data.get('properties', [])]
            result += f"**Properties:** {', '.join(properties)}\n"

        # Description
        result += "\n"
        if data.get('desc'):
            for paragraph in data.get('desc', []):
                result += f"{paragraph}\n\n"

        # Special rules for specific items
        if data.get('special'):
            result += f"**Special:** {data.get('special')}\n\n"

        # Contents for packs
        if data.get('contents'):
            result += "**Contents:**\n\n"
            for item in data.get('contents', []):
                item_name = item.get('item', {}).get('name', 'Unknown item')
                quantity = item.get('quantity', 1)
                result += f"* {item_name} (×{quantity})\n"
            result += "\n"

        return result
    except Exception as e:
        # Fallback to plain formatting if there's an error
        print(f"Error formatting equipment card: {e}", file=sys.stderr)
        return format_equipment_plain(data)


def format_equipment_plain(data):
    """
    Format equipment data into a simple plain text format.

    Args:
        data: Equipment data dictionary from the D&D 5e API

    Returns:
        Formatted plain text string
    """
    try:
        result = f"{data.get('name', 'Unknown Item')}\n\n"

        # Category
        category = data.get('equipment_category', {}).get('name', '')
        result += f"Type: {category}\n"

        # Cost and weight
        if data.get('cost'):
            quantity = data.get('cost', {}).get('quantity', 0)
            unit = data.get('cost', {}).get('unit', '')
            result += f"Cost: {quantity} {unit}\n"

        if data.get('weight'):
            result += f"Weight: {data.get('weight')} lb.\n"

        # Basic properties (simplified)
        if data.get('armor_class'):
            ac_base = data.get('armor_class', {}).get('base', 0)
            result += f"AC: {ac_base}\n"

        if data.get('damage'):
            damage_dice = data.get('damage', {}).get('damage_dice', '')
            damage_type = data.get('damage', {}).get(
                'damage_type', {}).get('name', '')
            result += f"Damage: {damage_dice} {damage_type}\n"

        # Description (simplified)
        if data.get('desc'):
            result += "\nDescription: "
            result += " ".join(data.get('desc', []))[:200]
            if len(" ".join(data.get('desc', []))) > 200:
                result += "..."
            result += "\n"

        return result
    except Exception as e:
        # Ultra-fallback for any errors
        print(f"Error in plain equipment formatting: {e}", file=sys.stderr)
        return str(data)
