#!/usr/bin/env python3
import sys


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
