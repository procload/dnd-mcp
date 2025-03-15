#!/usr/bin/env python3
"""
Test script for the query enhancement module.

This script tests the various components of the query enhancement module,
including synonym expansion, special term tokenization, fuzzy matching,
and category prioritization.
"""

import sys
from src.query_enhancement import (
    enhance_query,
    expand_query_with_synonyms,
    tokenize_dnd_query,
    fuzzy_match,
    prioritize_categories,
    get_top_categories
)


def test_synonym_expansion():
    """Test the synonym expansion functionality."""
    print("\n=== Testing Synonym Expansion ===")

    test_queries = [
        "What is the AC of a dragon?",
        "How many HP does a goblin have?",
        "What are the stats for a fighter?",
        "How does the fireball spell work?",
        "What is the DC for disarming a trap?",
        "Can I use my STR for intimidation?"
    ]

    for query in test_queries:
        expanded_query, synonyms_added = expand_query_with_synonyms(query)
        print(f"\nOriginal: {query}")
        print(f"Expanded: {expanded_query}")
        if synonyms_added:
            print("Synonyms added:")
            for original, expanded in synonyms_added:
                print(f"  - {original} → {expanded}")
        else:
            print("No synonyms added.")


def test_special_term_tokenization():
    """Test the special term tokenization functionality."""
    print("\n=== Testing Special Term Tokenization ===")

    test_queries = [
        "What is the AC of a dragon?",
        "How much damage does 2d6+3 do?",
        "What is the DC for a STR save?",
        "How does the PHB describe multiclassing?",
        "What's the CR of an adult red dragon?",
        "How do I calculate my DEX modifier?"
    ]

    for query in test_queries:
        tokens, special_terms = tokenize_dnd_query(query)
        print(f"\nQuery: {query}")
        print(f"Tokens: {tokens}")
        if special_terms:
            print(f"Special terms: {special_terms}")
        else:
            print("No special terms found.")


def test_fuzzy_matching():
    """Test the fuzzy matching functionality."""
    print("\n=== Testing Fuzzy Matching ===")

    test_queries = [
        "What is the armour class of a dragon?",
        "How does the firball spell work?",
        "What are the abilities of a rouge?",
        "How much damage does a wizzard do?",
        "What is the challange rating of a tarrasque?",
        "How do I calculate my dexterity modifer?"
    ]

    for query in test_queries:
        tokens = query.split()
        corrections = fuzzy_match(tokens)
        print(f"\nQuery: {query}")
        if corrections:
            print("Suggested corrections:")
            for original, correction in corrections:
                print(f"  - {original} → {correction}")
        else:
            print("No corrections suggested.")


def test_category_prioritization():
    """Test the category prioritization functionality."""
    print("\n=== Testing Category Prioritization ===")

    test_queries = [
        "What is the fireball spell?",
        "Tell me about dragons",
        "How do barbarians rage?",
        "What equipment does a fighter start with?",
        "What are the properties of a vorpal sword?",
        "How does the charmed condition work?",
        "What feats are good for a wizard?",
        "What is the acolyte background?",
        "What are the rules for multiclassing?",
        "What races get darkvision?"
    ]

    for query in test_queries:
        scores = prioritize_categories(query)
        top_categories = get_top_categories(query, 3)

        print(f"\nQuery: {query}")
        print("Category scores:")
        for category, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            if score > 0:
                print(f"  - {category}: {score:.2f}")

        print(f"Top categories: {', '.join(top_categories)}")


def test_full_enhancement():
    """Test the full query enhancement pipeline."""
    print("\n=== Testing Full Query Enhancement ===")

    test_queries = [
        "What is the AC of a dragon?",
        "How does the firball spell work?",
        "What are the stats for a rouge?",
        "How much damage does 2d6+3 do?",
        "What is the DC for a STR save?",
        "Can I use my dex for intimidation checks?"
    ]

    for query in test_queries:
        enhanced_query, enhancements = enhance_query(query)

        print(f"\nOriginal query: {query}")
        print(f"Enhanced query: {enhanced_query}")

        if enhancements["synonyms_added"]:
            print("Synonyms added:")
            for original, expanded in enhancements["synonyms_added"]:
                print(f"  - {original} → {expanded}")

        if enhancements["special_terms"]:
            print(f"Special terms: {', '.join(enhancements['special_terms'])}")

        if enhancements["fuzzy_matches"]:
            print("Suggested corrections:")
            for original, correction in enhancements["fuzzy_matches"]:
                print(f"  - {original} → {correction}")

        if enhancements["category_priorities"]:
            top_categories = get_top_categories(enhanced_query, 3)
            print(f"Top categories: {', '.join(top_categories)}")


if __name__ == "__main__":
    print("Testing query enhancement module...")

    test_synonym_expansion()
    test_special_term_tokenization()
    test_fuzzy_matching()
    test_category_prioritization()
    test_full_enhancement()

    print("\n✅ Query enhancement tests completed!")
