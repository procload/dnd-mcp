#!/usr/bin/env python3
"""
Test script to verify the D&D Knowledge Navigator package structure.
This script imports and uses various components from the package to ensure
everything is properly accessible.
"""

from src.templates import formatter, spell
from src.query_enhancement import synonyms, tokenizer
from src.attribution import core as attribution_core
from src.core import api_helpers
from src import __version__
import sys
import os

# Add the current directory to the path so we can import our package
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Test importing from the package


def test_imports():
    """Test that all imports are working correctly."""
    print(f"D&D Knowledge Navigator version: {__version__}")
    print(f"Attribution module loaded: {attribution_core.__name__}")
    print(
        f"Query enhancement modules loaded: {synonyms.__name__}, {tokenizer.__name__}")
    print(f"Template modules loaded: {formatter.__name__}, {spell.__name__}")

    # Test some basic functionality
    print("\nTesting basic functionality:")

    # Test attribution
    attribution_manager = attribution_core.AttributionManager()

    # Create a source attribution object
    source_attr = attribution_core.SourceAttribution(
        source="Player's Handbook",
        api_endpoint="/api/spells/fireball",
        confidence=attribution_core.ConfidenceLevel.HIGH,
        relevance_score=95.0,
        tool_used="spell_search"
    )

    # Add the attribution to the manager
    attribution_id = attribution_manager.add_attribution(
        attribution=source_attr)
    print(f"Attribution ID created: {attribution_id}")

    # Test synonym expansion
    test_query = "wizard spell"
    expanded_query, expanded_terms = synonyms.expand_query_with_synonyms(
        test_query)
    print(f"Synonym expansion: '{test_query}' -> '{expanded_query}'")
    if expanded_terms:
        print(f"Expanded terms: {expanded_terms}")

    print("\nAll tests completed successfully!")


if __name__ == "__main__":
    test_imports()
