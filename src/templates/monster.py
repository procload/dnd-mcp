"""
Monster template module for D&D Knowledge Navigator.

This module contains templates for formatting monster data in markdown.
"""

from src.templates.config import is_template_enabled, get_formatting_option


def format_ability_modifier(score):
    """Format ability score modifier."""
    modifier = (score - 10) // 2
    if modifier >= 0:
        return f"+{modifier}"
    return str(modifier)


def format_monster_stat_block(data):
    """
    Format monster data into a D&D-style stat block using markdown.

    Args:
        data: Monster data dictionary from the D&D 5e API

    Returns:
        Formatted markdown string
    """
    # Check if templates are enabled
    if not is_template_enabled("monster"):
        return format_monster_plain(data)

    use_tables = get_formatting_option("use_tables", True)
    use_emojis = get_formatting_option("use_emojis", False)

    try:
        monster_name = data.get('name', 'Unknown Monster')
        monster_emoji = "🐲 " if use_emojis else ""
        result = f"# {monster_emoji}{monster_name}\n\n"

        # Basic information
        result += f"**Type:** {data.get('size', '')} {data.get('type', '')}"
        if data.get('subtype'):
            result += f" ({data.get('subtype')})"
        result += f", {data.get('alignment', '')}\n"

        # Armor Class
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

        # Hit Points and Speed
        result += f"**Hit Points:** {data.get('hit_points', 0)} ({data.get('hit_dice', '')})\n"
        result += f"**Speed:** {', '.join([f'{k} {v} ft.' for k,
                                          v in data.get('speed', {}).items()])}\n\n"

        # Ability scores
        if use_tables:
            result += "| STR | DEX | CON | INT | WIS | CHA |\n"
            result += "|-----|-----|-----|-----|-----|-----|\n"
            result += f"| {data.get('strength', 0)} ({format_ability_modifier(data.get('strength', 0))}) "
            result += f"| {data.get('dexterity', 0)} ({format_ability_modifier(data.get('dexterity', 0))}) "
            result += f"| {data.get('constitution', 0)} ({format_ability_modifier(data.get('constitution', 0))}) "
            result += f"| {data.get('intelligence', 0)} ({format_ability_modifier(data.get('intelligence', 0))}) "
            result += f"| {data.get('wisdom', 0)} ({format_ability_modifier(data.get('wisdom', 0))}) "
            result += f"| {data.get('charisma', 0)} ({format_ability_modifier(data.get('charisma', 0))}) |\n\n"
        else:
            result += "**Abilities:**\n"
            result += f"STR: {data.get('strength', 0)} ({format_ability_modifier(data.get('strength', 0))}), "
            result += f"DEX: {data.get('dexterity', 0)} ({format_ability_modifier(data.get('dexterity', 0))}), "
            result += f"CON: {data.get('constitution', 0)} ({format_ability_modifier(data.get('constitution', 0))}), "
            result += f"INT: {data.get('intelligence', 0)} ({format_ability_modifier(data.get('intelligence', 0))}), "
            result += f"WIS: {data.get('wisdom', 0)} ({format_ability_modifier(data.get('wisdom', 0))}), "
            result += f"CHA: {data.get('charisma', 0)} ({format_ability_modifier(data.get('charisma', 0))})\n\n"

        # Saving throws
        if data.get('proficiencies'):
            saving_throws = [p for p in data.get('proficiencies', [])
                             if 'saving-throw' in p.get('proficiency', {}).get('index', '')]
            if saving_throws:
                saves = [f"{p.get('proficiency', {}).get('name', '').replace('Saving Throw: ', '')}: +{p.get('value', 0)}"
                         for p in saving_throws]
                result += f"**Saving Throws:** {', '.join(saves)}\n"

        # Skills
        skills = [p for p in data.get('proficiencies', [])
                  if 'skill' in p.get('proficiency', {}).get('index', '')]
        if skills:
            skill_list = [f"{p.get('proficiency', {}).get('name', '').replace('Skill: ', '')}: +{p.get('value', 0)}"
                          for p in skills]
            result += f"**Skills:** {', '.join(skill_list)}\n"

        # Senses, Languages, Challenge
        if data.get('senses'):
            senses = [f"{k.replace('_', ' ').title()}: {v}" for k, v in data.get(
                'senses', {}).items()]
            result += f"**Senses:** {', '.join(senses)}\n"

        if data.get('languages'):
            result += f"**Languages:** {data.get('languages', '')}\n"

        result += f"**Challenge:** {data.get('challenge_rating', 0)} "
        xp = calculate_xp(data.get('challenge_rating', 0))
        if xp:
            result += f"({xp} XP)\n\n"
        else:
            result += "\n\n"

        # Special abilities
        if data.get('special_abilities'):
            special_emoji = "✨ " if use_emojis else ""
            result += f"## {special_emoji}Special Abilities\n\n"
            for ability in data.get('special_abilities', []):
                result += f"**{ability.get('name', '')}:** {ability.get('desc', '')}\n\n"

        # Actions
        if data.get('actions'):
            action_emoji = "⚔️ " if use_emojis else ""
            result += f"## {action_emoji}Actions\n\n"
            for action in data.get('actions', []):
                result += f"**{action.get('name', '')}:** {action.get('desc', '')}\n\n"

        # Legendary actions
        if data.get('legendary_actions'):
            legendary_emoji = "👑 " if use_emojis else ""
            result += f"## {legendary_emoji}Legendary Actions\n\n"
            if data.get('legendary_desc'):
                result += f"{data.get('legendary_desc', '')}\n\n"
            for action in data.get('legendary_actions', []):
                result += f"**{action.get('name', '')}:** {action.get('desc', '')}\n\n"

        return result
    except Exception as e:
        # Fallback to plain formatting if there's an error
        print(f"Error formatting monster stat block: {e}", file=sys.stderr)
        return format_monster_plain(data)


def format_monster_plain(data):
    """
    Format monster data into a simple plain text format.

    Args:
        data: Monster data dictionary from the D&D 5e API

    Returns:
        Formatted plain text string
    """
    try:
        result = f"{data.get('name', 'Unknown Monster')}\n\n"
        result += f"Type: {data.get('size', '')} {data.get('type', '')}"
        if data.get('subtype'):
            result += f" ({data.get('subtype')})"
        result += f", {data.get('alignment', '')}\n"
        result += f"AC: {data.get('armor_class', 0)}, "
        result += f"HP: {data.get('hit_points', 0)} ({data.get('hit_dice', '')})\n"
        result += f"Speed: {', '.join([f'{k} {v} ft.' for k,
                                      v in data.get('speed', {}).items()])}\n\n"

        # Basic stats
        result += f"STR: {data.get('strength', 0)}, "
        result += f"DEX: {data.get('dexterity', 0)}, "
        result += f"CON: {data.get('constitution', 0)}, "
        result += f"INT: {data.get('intelligence', 0)}, "
        result += f"WIS: {data.get('wisdom', 0)}, "
        result += f"CHA: {data.get('charisma', 0)}\n\n"

        # Challenge
        result += f"Challenge: {data.get('challenge_rating', 0)}\n\n"

        # Special abilities (summarized)
        if data.get('special_abilities'):
            result += "Special Abilities: "
            abilities = [ability.get('name', '')
                         for ability in data.get('special_abilities', [])]
            result += f"{', '.join(abilities)}\n\n"

        # Actions (summarized)
        if data.get('actions'):
            result += "Actions: "
            actions = [action.get('name', '')
                       for action in data.get('actions', [])]
            result += f"{', '.join(actions)}\n\n"

        return result
    except Exception as e:
        # Ultra-fallback for any errors
        print(f"Error in plain monster formatting: {e}", file=sys.stderr)
        return str(data)


def calculate_xp(cr):
    """Calculate XP from challenge rating."""
    xp_by_cr = {
        0: 0, 0.125: 25, 0.25: 50, 0.5: 100, 1: 200, 2: 450, 3: 700, 4: 1100, 5: 1800,
        6: 2300, 7: 2900, 8: 3900, 9: 5000, 10: 5900, 11: 7200, 12: 8400, 13: 10000,
        14: 11500, 15: 13000, 16: 15000, 17: 18000, 18: 20000, 19: 22000, 20: 25000,
        21: 33000, 22: 41000, 23: 50000, 24: 62000, 25: 75000, 26: 90000, 27: 105000,
        28: 120000, 29: 135000, 30: 155000
    }
    return xp_by_cr.get(cr, None)
