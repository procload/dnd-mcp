#!/usr/bin/env python3
import sys
import json
import urllib.request
import urllib.error

# D&D API endpoint
API_BASE_URL = "https://www.dnd5eapi.co/api"


def validate_dnd_entity(endpoint: str, name: str) -> bool:
    """Check if an entity exists in the D&D API."""
    if not name:
        return False

    try:
        name = name.lower().replace(' ', '-')
        url = f"{API_BASE_URL}/{endpoint}/{name}"
        print(f"Validating entity: {url}", file=sys.stderr)

        with urllib.request.urlopen(url) as response:
            return response.status == 200
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Entity not found: {endpoint}/{name}", file=sys.stderr)
            return False
        print(f"HTTP error validating entity: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error validating entity: {e}", file=sys.stderr)
        return False


def fetch_dnd_entity(endpoint: str, name: str) -> dict:
    """Fetch entity details from the D&D API."""
    if not name:
        return {}

    try:
        name = name.lower().replace(' ', '-')
        url = f"{API_BASE_URL}/{endpoint}/{name}"
        print(f"Fetching entity: {url}", file=sys.stderr)

        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                return json.loads(response.read())
            return {}
    except urllib.error.HTTPError as e:
        print(f"HTTP error fetching entity: {e}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"Error fetching entity: {e}", file=sys.stderr)
        return {}


def get_primary_ability(class_name: str) -> str:
    """Return the primary ability for a class."""
    mapping = {
        "barbarian": "Strength",
        "bard": "Charisma",
        "cleric": "Wisdom",
        "druid": "Wisdom",
        "fighter": "Strength or Dexterity",
        "monk": "Dexterity & Wisdom",
        "paladin": "Strength & Charisma",
        "ranger": "Dexterity & Wisdom",
        "rogue": "Dexterity",
        "sorcerer": "Charisma",
        "warlock": "Charisma",
        "wizard": "Intelligence"
    }
    return mapping.get(class_name.lower(), "Unknown")


def get_asi_text(race_data: dict) -> str:
    """Extract ability score increases from race data."""
    if not race_data or "ability_bonuses" not in race_data:
        return "Unknown"

    bonuses = race_data.get("ability_bonuses", [])
    if not bonuses:
        return "None"

    asi_text = []
    for bonus in bonuses:
        ability_name = bonus.get("ability_score", {}).get("name", "Unknown")
        bonus_value = bonus.get("bonus", 0)
        if ability_name and bonus_value:
            asi_text.append(f"{ability_name} +{bonus_value}")

    return ", ".join(asi_text) if asi_text else "None"
