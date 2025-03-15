"""
Main formatter module for D&D Knowledge Navigator.

This module provides a unified interface for formatting D&D data using templates.
"""

import sys
from src.templates.config import TEMPLATES_ENABLED
from src.templates.monster import format_monster_stat_block, format_monster_plain
from src.templates.spell import format_spell_card, format_spell_plain
from src.templates.equipment import format_equipment_card, format_equipment_plain


def format_dnd_data(data, data_type=None):
    """
    Format D&D data using the appropriate template.

    Args:
        data: The data to format
        data_type: The type of data (monster, spell, equipment, etc.)
                  If None, will attempt to determine from the data

    Returns:
        Formatted string
    """
    if not TEMPLATES_ENABLED:
        return format_plain(data, data_type)

    # Determine data type if not provided
    if data_type is None:
        data_type = determine_data_type(data)

    try:
        if data_type == 'monster':
            return format_monster_stat_block(data)
        elif data_type == 'spell':
            return format_spell_card(data)
        elif data_type == 'equipment':
            return format_equipment_card(data)
        else:
            # Default to plain formatting for unknown types
            return format_plain(data, data_type)
    except Exception as e:
        print(f"Error in format_dnd_data: {e}", file=sys.stderr)
        return format_plain(data, data_type)


def format_plain(data, data_type=None):
    """
    Format D&D data in plain text.

    Args:
        data: The data to format
        data_type: The type of data

    Returns:
        Formatted string
    """
    # Determine data type if not provided
    if data_type is None:
        data_type = determine_data_type(data)

    try:
        if data_type == 'monster':
            return format_monster_plain(data)
        elif data_type == 'spell':
            return format_spell_plain(data)
        elif data_type == 'equipment':
            return format_equipment_plain(data)
        else:
            # Ultra-fallback for unknown types
            return str(data)
    except Exception as e:
        print(f"Error in format_plain: {e}", file=sys.stderr)
        return str(data)


def determine_data_type(data):
    """
    Determine the type of D&D data.

    Args:
        data: The data to analyze

    Returns:
        String indicating the data type
    """
    # Check for monster-specific fields
    if 'hit_dice' in data or 'challenge_rating' in data:
        return 'monster'

    # Check for spell-specific fields
    if 'level' in data and ('components' in data or 'school' in data):
        return 'spell'

    # Check for equipment-specific fields
    if 'equipment_category' in data or 'gear_category' in data or 'weapon_category' in data:
        return 'equipment'

    # Check for class-specific fields
    if 'class_levels' in data or 'subclasses' in data:
        return 'class'

    # Default to unknown
    return 'unknown'


def format_search_results(results, include_attribution=True):
    """
    Format search results with appropriate templates.

    Args:
        results: Search results dictionary
        include_attribution: Whether to include attribution section

    Returns:
        Formatted string
    """
    formatted = ""

    # Format the query
    if 'query' in results:
        formatted += f"# Search Results for \"{results.get('query')}\"\n\n"

    # Format categories
    for category, data in results.get('results', {}).items():
        if not data.get('items'):
            continue

        category_name = category.replace('_', ' ').title()
        formatted += f"## {category_name}\n\n"

        for item in data.get('items', []):
            formatted += f"- **{item.get('name')}**"

            # Add brief description if available
            if 'desc' in item and item['desc']:
                desc = item['desc']
                if isinstance(desc, list) and len(desc) > 0:
                    desc = desc[0]
                # Truncate long descriptions
                if len(desc) > 100:
                    desc = desc[:97] + "..."
                formatted += f": {desc}"

            formatted += "\n"

        formatted += "\n"

    # Add total count
    if 'total_count' in results:
        formatted += f"*Found {results.get('total_count')} results in total.*\n\n"

    # Add attribution if included in results and requested
    if include_attribution and 'formatted_attribution' in results:
        formatted += results.get('formatted_attribution', '')

    return formatted
