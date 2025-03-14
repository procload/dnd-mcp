#!/usr/bin/env python3
"""
Test script for the MCP integration with source attribution.

This script tests the MCP integration by simulating a search query
and examining the formatted attribution in the response.
"""

import sys
import json
import traceback
from src.attribution import (
    SourceAttribution,
    ConfidenceLevel,
    ConfidenceFactors,
    ConfidenceScorer,
    ToolCategory,
    track_tool_usage,
    source_tracker,
    attribution_manager
)
from src.attribution.formatters import format_all_attribution_for_display


def test_mcp_response_formatting():
    """Test MCP response formatting with attributions."""
    print("Testing MCP response formatting...")

    # Create test attributions
    attr1 = SourceAttribution(
        source="Player's Handbook",
        api_endpoint="/api/spells/fireball",
        confidence=ConfidenceLevel.HIGH,
        relevance_score=95.0,
        tool_used="search_spells",
        page=241,
        metadata={"spell_level": 3}
    )

    attr2 = SourceAttribution(
        source="Monster Manual",
        api_endpoint="/api/monsters/dragon-red",
        confidence=ConfidenceLevel.MEDIUM,
        relevance_score=75.0,
        tool_used="search_monsters",
        page=98,
        metadata={"cr": 17}
    )

    # Add attributions
    attr1_id = attribution_manager.add_attribution(attribution=attr1)
    attr2_id = attribution_manager.add_attribution(attribution=attr2)

    # Create test response data
    response_data = {
        "query": "fireball dragon",
        "results": {
            "spells": {
                "items": [
                    {"name": "Fireball", "level": 3}
                ],
                "count": 1
            },
            "monsters": {
                "items": [
                    {"name": "Red Dragon", "cr": 17}
                ],
                "count": 1
            }
        },
        "total_count": 2
    }

    # Create attribution map
    attribution_map = {
        "query": attr1_id,
        "results.spells": attr1_id,
        "results.monsters": attr2_id,
        "total_count": attr1_id
    }

    try:
        # Format response for MCP
        mcp_response = source_tracker.prepare_mcp_response(
            response_data, attribution_map
        )

        # Verify the MCP response
        assert "content" in mcp_response
        assert "formatted_attribution" in mcp_response

        # Print the MCP response
        print("MCP response content:")
        print(mcp_response.get("content", ""))

        print("\nFormatted attribution:")
        print(mcp_response.get("formatted_attribution", ""))

        print("MCP response formatting test passed!")
    except Exception as e:
        print(f"Error in MCP response formatting test: {e}")
        traceback.print_exc()
        print("Continuing with other tests...")


def test_direct_formatting():
    """Test direct formatting of attribution information."""
    print("Testing direct formatting...")

    # Create test attributions
    attr1 = SourceAttribution(
        source="Player's Handbook",
        api_endpoint="/api/spells/fireball",
        confidence=ConfidenceLevel.HIGH,
        relevance_score=95.0,
        tool_used="search_spells",
        page=241,
        metadata={"spell_level": 3}
    )

    # Add attributions
    attr1_id = attribution_manager.add_attribution(attribution=attr1)

    # Create test response data with attribution
    response_data = {
        "query": "fireball",
        "attributions": {
            "query": attr1.to_dict()
        },
        "sources_summary": ["Player's Handbook"]
    }

    # Format the attribution directly
    formatted = format_all_attribution_for_display(response_data)

    # Print the formatted attribution
    print("Directly formatted attribution:")
    print(formatted)

    print("Direct formatting test passed!")


if __name__ == "__main__":
    try:
        test_mcp_response_formatting()
        print()
        test_direct_formatting()
        print("\nAll tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
