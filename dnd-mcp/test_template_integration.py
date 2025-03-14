#!/usr/bin/env python3
"""
Test script for template integration with tools.

This script tests the integration of our template system with the tools.
"""

import sys
import json
from src.templates import TEMPLATES_ENABLED
from src.templates.config import FORMATTING_OPTIONS
from src.attribution import source_tracker, attribution_manager, SourceAttribution, ConfidenceLevel


def test_search_formatting():
    """Test search formatting with templates."""
    print("\n=== Testing Search Formatting ===")

    # Create a mock search response
    mock_response = {
        "query": "fireball",
        "results": {
            "spells": {
                "items": [
                    {"name": "Fireball", "desc": "A bright streak flashes from your pointing finger to a point you choose within range and then blossoms with a low roar into an explosion of flame."},
                    {"name": "Delayed Blast Fireball", "desc": "A beam of yellow light flashes from your pointing finger, then condenses to linger at a chosen point within range as a glowing bead for the duration."}
                ],
                "count": 2
            },
            "magic-items": {
                "items": [
                    {"name": "Wand of Fireballs", "desc": "This wand has 7 charges. While holding it, you can use an action to expend 1 or more of its charges to cast the fireball spell."}
                ],
                "count": 1
            }
        },
        "total_count": 3
    }

    # Create attributions
    spell_attr_id = attribution_manager.add_attribution(
        attribution=SourceAttribution(
            source="D&D 5e API",
            api_endpoint="/api/spells",
            confidence=ConfidenceLevel.HIGH,
            relevance_score=95.0,
            tool_used="search_all_categories"
        )
    )

    item_attr_id = attribution_manager.add_attribution(
        attribution=SourceAttribution(
            source="D&D 5e API",
            api_endpoint="/api/magic-items",
            confidence=ConfidenceLevel.MEDIUM,
            relevance_score=80.0,
            tool_used="search_all_categories"
        )
    )

    # Create attribution map
    attribution_map = {
        "query": spell_attr_id,
        "results.spells": spell_attr_id,
        "results.magic-items": item_attr_id,
        "total_count": spell_attr_id
    }

    # Test with templates enabled
    print(f"Templates enabled: {TEMPLATES_ENABLED}")
    print(f"Formatting options: {FORMATTING_OPTIONS}")

    # Format the response using our template system if enabled
    if TEMPLATES_ENABLED:
        from src.templates import format_search_results
        formatted_content = format_search_results(
            mock_response, include_attribution=False)
        mock_response["content"] = formatted_content
        print("\nFormatted content:")
        print(formatted_content[:500] +
              "..." if len(formatted_content) > 500 else formatted_content)

    # Prepare the final response with all attributions for MCP
    mcp_response = source_tracker.prepare_mcp_response(
        mock_response, attribution_map)

    print("\nMCP response:")
    if "content" in mcp_response:
        print(mcp_response["content"][:500] + "..." if len(
            mcp_response["content"]) > 500 else mcp_response["content"])
    else:
        print("No content in MCP response")


def test_verify_formatting():
    """Test verify formatting with templates."""
    print("\n=== Testing Verify Formatting ===")

    # Create a mock verify response
    mock_response = {
        "statement": "Fireball is a 3rd-level evocation spell that deals 8d6 fire damage.",
        "search_terms": ["fireball", "evocation", "spell", "damage"],
        "results": {
            "spells": [
                {
                    "name": "Fireball",
                    "details": {
                        "name": "Fireball",
                        "level": 3,
                        "school": {"name": "Evocation"},
                        "desc": ["A bright streak flashes from your pointing finger to a point you choose within range and then blossoms with a low roar into an explosion of flame. Each creature in a 20-foot-radius sphere centered on that point must make a Dexterity saving throw. A target takes 8d6 fire damage on a failed save, or half as much damage on a successful one."]
                    }
                }
            ]
        },
        "found_matches": True
    }

    # Create attributions
    verify_attr_id = attribution_manager.add_attribution(
        attribution=SourceAttribution(
            source="D&D 5e API",
            api_endpoint="/api/spells/fireball",
            confidence=ConfidenceLevel.HIGH,
            relevance_score=95.0,
            tool_used="verify_with_api"
        )
    )

    # Create attribution map
    attribution_map = {
        "statement": verify_attr_id,
        "search_terms": verify_attr_id,
        "results.spells": verify_attr_id,
        "found_matches": verify_attr_id
    }

    # Format the verification result using our template system if enabled
    if TEMPLATES_ENABLED:
        from src.templates import format_dnd_data

        formatted_content = f"# Verification of D&D Statement\n\n"
        formatted_content += f"**Statement:** {mock_response['statement']}\n\n"

        if mock_response["found_matches"]:
            formatted_content += "## Verification Results\n\n"
            formatted_content += f"Found information related to {len(mock_response['search_terms'])} search terms: "
            formatted_content += f"*{', '.join(mock_response['search_terms'])}*\n\n"

            # Format each category's results
            for category_name, items in mock_response["results"].items():
                formatted_content += f"### {category_name.replace('_', ' ').title()}\n\n"

                for item in items:
                    # Format the item details using our template system
                    item_details = item.get("details", {})
                    item_type = category_name[:-
                                              1] if category_name.endswith('s') else category_name

                    formatted_content += f"**{item.get('name', 'Unknown')}**\n\n"

                    # Add a brief formatted excerpt
                    if item_details:
                        # Get a brief formatted version (first 200 chars)
                        formatted_item = format_dnd_data(
                            item_details, item_type)
                        brief_format = formatted_item.split("\n\n")[0]
                        if len(brief_format) > 200:
                            brief_format = brief_format[:197] + "..."

                        formatted_content += f"{brief_format}\n\n"

        mock_response["content"] = formatted_content
        print("\nFormatted content:")
        print(formatted_content[:500] +
              "..." if len(formatted_content) > 500 else formatted_content)

    # Prepare the final response with all attributions for MCP
    mcp_response = source_tracker.prepare_mcp_response(
        mock_response, attribution_map)

    print("\nMCP response:")
    if "content" in mcp_response:
        print(mcp_response["content"][:500] + "..." if len(
            mcp_response["content"]) > 500 else mcp_response["content"])
    else:
        print("No content in MCP response")


if __name__ == "__main__":
    print("Testing template integration with tools...")

    test_search_formatting()
    test_verify_formatting()

    print("\n✅ Template integration tests completed!")
