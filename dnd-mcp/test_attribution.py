#!/usr/bin/env python3
"""
Test script for the source attribution system.

This script tests the source attribution functionality by simulating
a search query and examining the attribution information in the response.
"""

import sys
import json
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


def test_basic_attribution():
    """Test basic attribution functionality."""
    print("Testing basic attribution...")

    # Create a test attribution
    attr = SourceAttribution(
        source="Test Source",
        api_endpoint="/api/test",
        confidence=ConfidenceLevel.HIGH,
        relevance_score=95.0,
        tool_used="test_function",
        page=42,
        metadata={"test_key": "test_value"}
    )

    # Add the attribution
    attr_id = attribution_manager.add_attribution(attribution=attr)

    # Get the attribution back
    retrieved_attr = attribution_manager.get_attribution(attr_id)

    # Verify the attribution
    assert retrieved_attr.source == "Test Source"
    assert retrieved_attr.api_endpoint == "/api/test"
    assert retrieved_attr.confidence == ConfidenceLevel.HIGH
    assert retrieved_attr.relevance_score == 95.0
    assert retrieved_attr.tool_used == "test_function"
    assert retrieved_attr.page == 42
    assert retrieved_attr.metadata["test_key"] == "test_value"

    print("Basic attribution test passed!")


def test_confidence_scoring():
    """Test confidence scoring functionality."""
    print("Testing confidence scoring...")

    # Create test factors
    factors = {
        ConfidenceFactors.DIRECT_API_MATCH: 0.8,
        ConfidenceFactors.OFFICIAL_SOURCE: 1.0,
        ConfidenceFactors.MULTIPLE_SOURCES: 0.5
    }

    # Calculate confidence
    score, level = ConfidenceScorer.calculate_confidence(factors)

    # Verify the confidence
    assert score > 0
    assert level in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM,
                     ConfidenceLevel.LOW, ConfidenceLevel.UNCERTAIN]

    # Get explanation
    explanation = ConfidenceScorer.explain_confidence(factors, score, level)
    assert "Confidence:" in explanation

    print(
        f"Confidence scoring test passed! Score: {score:.1f}%, Level: {level.value}")
    print(f"Explanation:\n{explanation}")


def test_response_formatting():
    """Test response formatting with attributions."""
    print("Testing response formatting...")

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

    # Format response with attributions
    formatted_response = source_tracker.prepare_response_with_sources(
        response_data, attribution_map
    )

    # Verify the formatted response
    assert "attributions" in formatted_response
    assert "sources_summary" in formatted_response
    assert "Player's Handbook" in formatted_response["sources_summary"]
    assert "Monster Manual" in formatted_response["sources_summary"]

    # Print the formatted response
    print("Formatted response:")
    print(json.dumps(formatted_response, indent=2))

    print("Response formatting test passed!")


if __name__ == "__main__":
    try:
        test_basic_attribution()
        print()
        test_confidence_scoring()
        print()
        test_response_formatting()
        print("\nAll tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
