#!/usr/bin/env python3
"""
Test script for the template system.

This script tests the template system by formatting sample data
and displaying the results.
"""

import sys
import json
import requests
from src.templates import (
    TEMPLATES_ENABLED,
    format_dnd_data,
    format_search_results
)
from src.templates.config import FORMATTING_OPTIONS

# Base URL for the D&D 5e API
BASE_URL = "https://www.dnd5eapi.co/api"


def fetch_sample_data():
    """Fetch sample data from the D&D 5e API."""
    samples = {}

    # Fetch a monster
    try:
        response = requests.get(f"{BASE_URL}/monsters/adult-red-dragon")
        if response.status_code == 200:
            samples['monster'] = response.json()
            print("✅ Fetched monster data")
        else:
            print(f"❌ Failed to fetch monster data: {response.status_code}")
    except Exception as e:
        print(f"❌ Error fetching monster data: {e}")

    # Fetch a spell
    try:
        response = requests.get(f"{BASE_URL}/spells/fireball")
        if response.status_code == 200:
            samples['spell'] = response.json()
            print("✅ Fetched spell data")
        else:
            print(f"❌ Failed to fetch spell data: {response.status_code}")
    except Exception as e:
        print(f"❌ Error fetching spell data: {e}")

    # Fetch equipment
    try:
        response = requests.get(f"{BASE_URL}/equipment/plate-armor")
        if response.status_code == 200:
            samples['equipment'] = response.json()
            print("✅ Fetched equipment data")
        else:
            print(f"❌ Failed to fetch equipment data: {response.status_code}")
    except Exception as e:
        print(f"❌ Error fetching equipment data: {e}")

    return samples


def test_templates(samples):
    """Test the template system with sample data."""
    print("\n=== Testing Templates ===")
    print(f"Templates enabled: {TEMPLATES_ENABLED}")
    print(f"Formatting options: {FORMATTING_OPTIONS}")

    # Test monster template
    if 'monster' in samples:
        print("\n--- Monster Template ---")
        formatted = format_dnd_data(samples['monster'], 'monster')
        print(formatted[:500] + "...\n")

    # Test spell template
    if 'spell' in samples:
        print("\n--- Spell Template ---")
        formatted = format_dnd_data(samples['spell'], 'spell')
        print(formatted[:500] + "...\n")

    # Test equipment template
    if 'equipment' in samples:
        print("\n--- Equipment Template ---")
        formatted = format_dnd_data(samples['equipment'], 'equipment')
        print(formatted[:500] + "...\n")

    # Test search results formatting
    print("\n--- Search Results Template ---")
    mock_results = {
        "query": "dragon",
        "results": {
            "monsters": {
                "items": [
                    {"name": "Adult Red Dragon",
                        "desc": "A massive fire-breathing dragon with crimson scales."},
                    {"name": "Young Black Dragon",
                        "desc": "A sleek acid-spitting dragon with ebony scales."}
                ]
            },
            "spells": {
                "items": [
                    {"name": "Dragon's Breath",
                        "desc": "You imbue a creature with the power to exhale destructive energy."}
                ]
            }
        },
        "total_count": 3,
        "formatted_attribution": "\n\n---\n\n**Source Information:**\n\n* **Source:** D&D 5e API\n* **Confidence:** High\n"
    }
    formatted = format_search_results(mock_results)
    print(formatted)


def test_template_toggle():
    """Test toggling templates on and off."""
    if 'monster' not in samples:
        return

    print("\n=== Testing Template Toggle ===")

    # Save original setting
    original = TEMPLATES_ENABLED

    # Import the module to modify
    import src.templates.config as config

    # Test with templates enabled
    config.TEMPLATES_ENABLED = True
    print("\n--- Templates Enabled ---")
    formatted = format_dnd_data(samples['monster'], 'monster')
    print(formatted[:200] + "...\n")

    # Test with templates disabled
    config.TEMPLATES_ENABLED = False
    print("\n--- Templates Disabled ---")
    formatted = format_dnd_data(samples['monster'], 'monster')
    print(formatted[:200] + "...\n")

    # Restore original setting
    config.TEMPLATES_ENABLED = original


if __name__ == "__main__":
    print("Fetching sample data from D&D 5e API...")
    samples = fetch_sample_data()

    if not samples:
        print("❌ No sample data available. Exiting.")
        sys.exit(1)

    test_templates(samples)
    test_template_toggle()

    print("\n✅ Template tests completed!")
