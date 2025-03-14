#!/usr/bin/env python3
"""
Test script for the search enhancement integration.

This script tests the integration of the query enhancement module
with the search_all_categories function.
"""

import sys
import json
import requests
from cache import APICache
from src.query_enhancement import (
    enhance_query,
    expand_query_with_synonyms,
    tokenize_dnd_query,
    fuzzy_match,
    prioritize_categories,
    get_top_categories
)


def test_query_enhancement():
    """Test the query enhancement module directly."""
    print("\n=== Testing Query Enhancement Module ===")

    # Test queries that should benefit from enhancement
    test_queries = [
        "What is the AC of a dragon?",
        "How does the firball spell work?",
        "What are the stats for a rouge?",
        "How much damage does 2d6+3 do?",
        "What is the DC for a STR save?",
        "Can I use my dex for intimidation checks?"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")

        try:
            # Enhance the query
            enhanced_query, enhancements = enhance_query(query)

            # Print the enhanced query
            print(f"Enhanced query: {enhanced_query}")

            # Print query enhancements
            if enhancements["synonyms_added"]:
                print("Synonyms added:")
                for original, expanded in enhancements["synonyms_added"]:
                    print(f"  - {original} → {expanded}")

            if enhancements["special_terms"]:
                print(
                    f"Special terms: {', '.join(enhancements['special_terms'])}")

            if enhancements["fuzzy_matches"]:
                print("Fuzzy matches:")
                for original, correction in enhancements["fuzzy_matches"]:
                    print(f"  - {original} → {correction}")

            # Print top categories
            top_categories = get_top_categories(enhanced_query, 3)
            print(f"Top categories: {', '.join(top_categories)}")

        except Exception as e:
            print(f"Error: {e}")

    print("\n✅ Query enhancement test completed!")


def test_api_search():
    """Test searching the D&D 5e API with enhanced queries."""
    print("\n=== Testing API Search with Enhanced Queries ===")

    # Base URL for the D&D 5e API
    BASE_URL = "https://www.dnd5eapi.co/api"

    # Test queries that should benefit from enhancement
    test_queries = [
        "AC",
        "firball",
        "rouge",
        "2d6+3",
        "STR save",
        "dex"
    ]

    for query in test_queries:
        print(f"\nOriginal query: {query}")

        try:
            # Enhance the query
            enhanced_query, enhancements = enhance_query(query)
            print(f"Enhanced query: {enhanced_query}")

            # Get top categories
            top_categories = get_top_categories(enhanced_query, 3)
            print(f"Top categories: {', '.join(top_categories)}")

            # Search the API with the original query
            original_results = {}
            for category in top_categories:
                try:
                    response = requests.get(
                        f"{BASE_URL}/{category}?name={query}", timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        original_results[category] = data.get("count", 0)
                except Exception:
                    pass

            # Search the API with the enhanced query
            enhanced_results = {}
            for category in top_categories:
                try:
                    response = requests.get(
                        f"{BASE_URL}/{category}?name={enhanced_query}", timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        enhanced_results[category] = data.get("count", 0)
                except Exception:
                    pass

            # Print results
            print("Original query results:")
            for category, count in original_results.items():
                print(f"  - {category}: {count} results")

            print("Enhanced query results:")
            for category, count in enhanced_results.items():
                print(f"  - {category}: {count} results")

            # Calculate improvement
            original_total = sum(original_results.values())
            enhanced_total = sum(enhanced_results.values())

            if original_total > 0:
                improvement = (
                    (enhanced_total - original_total) / original_total) * 100
                print(f"Improvement: {improvement:.1f}%")
            else:
                print("No results for original query")

        except Exception as e:
            print(f"Error: {e}")

    print("\n✅ API search test completed!")


if __name__ == "__main__":
    print("Testing query enhancement integration...")

    test_query_enhancement()
    test_api_search()
