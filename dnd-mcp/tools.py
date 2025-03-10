#!/usr/bin/env python3
import sys
import json
import traceback
import urllib.request
import urllib.error
import urllib.parse
import mcp.types as types
from api_helpers import API_BASE_URL
from formatters import format_monster_data, format_spell_data, format_class_data
import requests
import logging
from typing import List, Dict, Any, Optional
from cache import APICache
import formatters
import resources

logger = logging.getLogger(__name__)

# Base URL for the D&D 5e API
BASE_URL = "https://www.dnd5eapi.co/api"


def register_tools(app, cache: APICache):
    """Register D&D API tools with the FastMCP app.

    Args:
        app: The FastMCP app instance
        cache: The shared API cache
    """
    print("Registering D&D API tools...", file=sys.stderr)

    @app.tool()
    def search_equipment_by_cost(max_cost: float, cost_unit: str = "gp") -> Dict[str, Any]:
        """Search equipment by maximum cost.

        Args:
            max_cost: Maximum cost value
            cost_unit: Cost unit (gp, sp, cp)

        Returns:
            Equipment items within the cost range
        """
        logger.debug(f"Searching equipment by cost: {max_cost} {cost_unit}")

        # Get equipment list (from cache if available)
        equipment_list = _get_category_items("equipment", cache)
        if "error" in equipment_list:
            return equipment_list

        # Filter equipment by cost
        results = []
        for item in equipment_list.get("items", []):
            # Get detailed item info (from cache if available)
            item_index = item["index"]
            item_details = _get_item_details("equipment", item_index, cache)
            if "error" in item_details:
                continue

            # Check if item has cost and is within budget
            if "cost" in item_details:
                cost = item_details["cost"]
                # Convert cost to requested unit for comparison
                converted_cost = _convert_currency(
                    cost["quantity"], cost["unit"], cost_unit)
                if converted_cost <= max_cost:
                    results.append({
                        "name": item_details["name"],
                        "cost": f"{cost['quantity']} {cost['unit']}",
                        "description": _get_description(item_details),
                        "category": item_details.get("equipment_category", {}).get("name", "Unknown"),
                        "uri": f"resource://dnd/item/equipment/{item_index}"
                    })

        return {
            "query": f"Equipment costing {max_cost} {cost_unit} or less",
            "items": results,
            "count": len(results)
        }

    @app.tool()
    def filter_spells_by_level(min_level: int = 0, max_level: int = 9, school: str = None) -> Dict[str, Any]:
        """Filter spells by level range and optionally by school.

        Args:
            min_level: Minimum spell level (0-9)
            max_level: Maximum spell level (0-9)
            school: Magic school (optional)

        Returns:
            Spells within the level range and school
        """
        logger.debug(
            f"Filtering spells by level: {min_level}-{max_level}, school: {school}")

        # Validate input
        if min_level < 0 or max_level > 9 or min_level > max_level:
            return {"error": "Invalid level range. Must be between 0 and 9."}

        # Get spells list (from cache if available)
        spells_list = _get_category_items("spells", cache)
        if "error" in spells_list:
            return spells_list

        # Filter spells by level and school
        results = []
        for item in spells_list.get("items", []):
            # Get detailed spell info (from cache if available)
            item_index = item["index"]
            spell_details = _get_item_details("spells", item_index, cache)
            if "error" in spell_details:
                continue

            # Check if spell level is within range
            spell_level = spell_details.get("level", 0)
            if min_level <= spell_level <= max_level:
                # Check school if specified
                if school:
                    spell_school = spell_details.get(
                        "school", {}).get("name", "").lower()
                    if school.lower() not in spell_school:
                        continue

                results.append({
                    "name": spell_details["name"],
                    "level": spell_level,
                    "school": spell_details.get("school", {}).get("name", "Unknown"),
                    "casting_time": spell_details.get("casting_time", "Unknown"),
                    "description": _get_description(spell_details),
                    "uri": f"resource://dnd/item/spells/{item_index}"
                })

        # Sort results by level and name
        results.sort(key=lambda x: (x["level"], x["name"]))

        return {
            "query": f"Spells of level {min_level}-{max_level}" + (f" in school {school}" if school else ""),
            "items": results,
            "count": len(results)
        }

    @app.tool()
    def find_monsters_by_challenge_rating(min_cr: float = 0, max_cr: float = 30) -> Dict[str, Any]:
        """Find monsters within a challenge rating range.

        Args:
            min_cr: Minimum challenge rating
            max_cr: Maximum challenge rating

        Returns:
            Monsters within the CR range
        """
        logger.debug(f"Finding monsters by CR: {min_cr}-{max_cr}")

        # Get monsters list (from cache if available)
        monsters_list = _get_category_items("monsters", cache)
        if "error" in monsters_list:
            return monsters_list

        # Filter monsters by CR
        results = []
        for item in monsters_list.get("items", []):
            # Get detailed monster info (from cache if available)
            item_index = item["index"]
            monster_details = _get_item_details("monsters", item_index, cache)
            if "error" in monster_details:
                continue

            # Check if monster CR is within range
            monster_cr = float(monster_details.get("challenge_rating", 0))
            if min_cr <= monster_cr <= max_cr:
                results.append({
                    "name": monster_details["name"],
                    "challenge_rating": monster_cr,
                    "type": monster_details.get("type", "Unknown"),
                    "size": monster_details.get("size", "Unknown"),
                    "alignment": monster_details.get("alignment", "Unknown"),
                    "hit_points": monster_details.get("hit_points", 0),
                    "armor_class": monster_details.get("armor_class", [{"value": 0}])[0].get("value", 0),
                    "uri": f"resource://dnd/item/monsters/{item_index}"
                })

        # Sort results by CR and name
        results.sort(key=lambda x: (x["challenge_rating"], x["name"]))

        return {
            "query": f"Monsters with CR {min_cr}-{max_cr}",
            "items": results,
            "count": len(results)
        }

    @app.tool()
    def get_class_starting_equipment(class_name: str) -> Dict[str, Any]:
        """Get starting equipment for a character class.

        Args:
            class_name: Name of the character class

        Returns:
            Starting equipment for the class
        """
        logger.debug(f"Getting starting equipment for class: {class_name}")

        # Normalize class name
        class_name = class_name.lower()

        # Get class details (from cache if available)
        class_details = _get_item_details("classes", class_name, cache)
        if "error" in class_details:
            return {"error": f"Class '{class_name}' not found"}

        # Extract starting equipment
        starting_equipment = []
        for item in class_details.get("starting_equipment", []):
            equipment = item.get("equipment", {})
            quantity = item.get("quantity", 1)
            starting_equipment.append({
                "name": equipment.get("name", "Unknown"),
                "quantity": quantity
            })

        # Extract starting equipment options
        equipment_options = []
        for option_set in class_details.get("starting_equipment_options", []):
            desc = option_set.get("desc", "Choose one option")
            choices = []

            for option in option_set.get("from", {}).get("options", []):
                if "item" in option:
                    item = option.get("item", {})
                    choices.append({
                        "name": item.get("name", "Unknown"),
                        "quantity": option.get("quantity", 1)
                    })

            equipment_options.append({
                "description": desc,
                "choices": choices
            })

        return {
            "class": class_details.get("name", class_name),
            "starting_equipment": starting_equipment,
            "equipment_options": equipment_options
        }

    @app.tool()
    def search_all_categories(query: str) -> Dict[str, Any]:
        """Search across all D&D categories for a term.

        Args:
            query: Search term

        Returns:
            Matching items across categories
        """
        logger.debug(f"Searching all categories for: {query}")

        # Get categories (from cache if available)
        categories_data = cache.get("dnd_categories")
        if not categories_data:
            try:
                response = requests.get(f"{BASE_URL}/")
                if response.status_code != 200:
                    return {"error": f"Failed to fetch categories: {response.status_code}"}

                data = response.json()
                categories = list(data.keys())

            except Exception as e:
                logger.exception(f"Error fetching categories: {e}")
                return {"error": f"Failed to fetch categories: {str(e)}"}
        else:
            categories = [cat["name"]
                          for cat in categories_data.get("categories", [])]

        # Prepare search query
        query_tokens = query.lower().split()

        # Define category priorities for certain query types
        category_priorities = {}

        # Check for magic item related queries
        magic_item_keywords = ["magic", "magical", "item",
                               "items", "wand", "staff", "rod", "wondrous"]
        if any(keyword in query_tokens for keyword in magic_item_keywords):
            category_priorities["magic-items"] = 10
            category_priorities["equipment"] = 5

        # Check for spell related queries
        spell_keywords = ["spell", "spells", "cast", "casting",
                          "caster", "magic", "wizard", "sorcerer", "warlock", "cleric"]
        if any(keyword in query_tokens for keyword in spell_keywords):
            category_priorities["spells"] = 10
            category_priorities["classes"] = 5

        # Check for monster related queries
        monster_keywords = ["monster", "creature", "beast",
                            "dragon", "undead", "fiend", "demon", "devil"]
        if any(keyword in query_tokens for keyword in monster_keywords):
            category_priorities["monsters"] = 10

        # Search each category
        results = {}
        total_count = 0
        all_matches = []

        for category in categories:
            # Skip rule-related categories for efficiency
            if category in ["rule-sections", "rules"]:
                continue

            # Get category items (from cache if available)
            category_data = _get_category_items(category, cache)
            if "error" in category_data:
                continue

            # Search for matching items with relevance scoring
            matching_items = []

            for item in category_data.get("items", []):
                item_name = item["name"].lower()
                item_index = item.get("index", "").lower()

                # Get item details for more comprehensive search
                item_details = None
                if any(token in item_name or token in item_index for token in query_tokens):
                    # Only fetch details if there's a potential match to avoid unnecessary API calls
                    item_details = _get_item_details(
                        category, item["index"], cache)

                # Calculate relevance score
                score = 0

                # Exact match in name or index
                if query.lower() == item_name or query.lower() == item_index:
                    score += 100

                # Partial matches in name or index
                for token in query_tokens:
                    if token in item_name:
                        score += 20
                    if token in item_index:
                        score += 15

                # Check if name contains all tokens
                if all(token in item_name for token in query_tokens):
                    score += 50

                # Check if name starts with any token
                if any(item_name.startswith(token) for token in query_tokens):
                    score += 10

                # Search in description and other fields if we have details
                if item_details and isinstance(item_details, dict) and not item_details.get("error"):
                    # Search in description
                    desc = ""
                    if isinstance(item_details.get("desc"), list):
                        desc = " ".join(item_details.get("desc", [])).lower()
                    elif isinstance(item_details.get("desc"), str):
                        desc = item_details.get("desc", "").lower()

                    for token in query_tokens:
                        if token in desc:
                            score += 5

                    # Search in other relevant fields based on category
                    if category == "magic-items" or category == "equipment":
                        # Check equipment category
                        eq_category = item_details.get(
                            "equipment_category", {}).get("name", "").lower()
                        for token in query_tokens:
                            if token in eq_category:
                                score += 10

                        # Check rarity for magic items
                        rarity = item_details.get(
                            "rarity", {}).get("name", "").lower()
                        for token in query_tokens:
                            if token in rarity:
                                score += 10

                    elif category == "spells":
                        # Check spell school
                        school = item_details.get(
                            "school", {}).get("name", "").lower()
                        for token in query_tokens:
                            if token in school:
                                score += 10

                        # Check classes that can use this spell
                        classes = [c.get("name", "").lower()
                                   for c in item_details.get("classes", [])]
                        for token in query_tokens:
                            if any(token in c for c in classes):
                                score += 15

                # Apply category priority boost
                if category in category_priorities:
                    score += category_priorities[category]

                # Add to matches if score is above threshold
                if score > 0:
                    matching_items.append({
                        **item,
                        "score": score
                    })

            # Sort by relevance score
            matching_items.sort(key=lambda x: x["score"], reverse=True)

            if matching_items:
                # Add category to results
                results[category] = {
                    # Limit to 5 items per category
                    "items": matching_items[:5],
                    "count": len(matching_items)
                }
                total_count += len(matching_items)

                # Add to all matches for cross-category sorting
                for item in matching_items:
                    all_matches.append({
                        "category": category,
                        "item": item
                    })

        # Sort all matches by score for top overall results
        all_matches.sort(key=lambda x: x["item"]["score"], reverse=True)
        top_results = all_matches[:5] if all_matches else []

        return {
            "query": query,
            "results": results,
            "total_count": total_count,
            "top_results": [
                {
                    "category": match["category"],
                    "name": match["item"]["name"],
                    "index": match["item"]["index"],
                    "score": match["item"]["score"]
                } for match in top_results
            ]
        }

    @app.tool("compare_knowledge")
    def compare_knowledge(category: str, index: str) -> Dict[str, Any]:
        """Compare D&D 5e API data with Claude's internal knowledge.

        This tool fetches data from the D&D 5e API and also provides Claude's internal knowledge
        about the same entity, allowing you to compare the two sources.

        Args:
            category: The D&D API category (e.g., 'spells', 'equipment', 'monsters')
            index: The specific item's index identifier

        Returns:
            A dictionary containing both the API data and Claude's internal knowledge
        """
        logger.debug(f"Comparing knowledge for {category}/{index}")

        # Get data from the D&D 5e API using the helper function
        api_data = _get_item_details(category, index, cache)

        # Add source attribution
        if "error" not in api_data:
            api_data["source"] = "D&D 5e API (www.dnd5eapi.co)"

        # Create a placeholder for Claude's internal knowledge
        # This will be filled in by Claude during response generation
        claude_knowledge = {
            "note": "This section will be filled with Claude's internal knowledge during response generation",
            "source": "Claude's training data (no API call)"
        }

        return {
            "api_data": api_data,
            "claude_knowledge": claude_knowledge,
            "comparison_note": "Compare these two sources to see differences between API data and Claude's knowledge"
        }

    # Helper functions
    def _get_category_items(category: str, cache: APICache) -> Dict[str, Any]:
        """Get all items in a category, using cache if available."""
        cache_key = f"dnd_items_{category}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        try:
            response = requests.get(f"{BASE_URL}/{category}")
            if response.status_code != 200:
                return {"error": f"Category '{category}' not found or API request failed"}

            data = response.json()

            # Transform to resource format
            items = []
            for item in data.get("results", []):
                items.append({
                    "name": item["name"],
                    "index": item["index"],
                    "description": f"Details about {item['name']}",
                    "uri": f"resource://dnd/item/{category}/{item['index']}"
                })

            result = {
                "category": category,
                "items": items,
                "count": len(items)
            }

            # Cache the result
            cache.set(cache_key, result)
            return result

        except Exception as e:
            logger.exception(f"Error fetching items for {category}: {e}")
            return {"error": f"Failed to fetch items: {str(e)}"}

    def _get_item_details(category: str, index: str, cache: APICache) -> Dict[str, Any]:
        """Get detailed information about a specific item, using cache if available."""
        cache_key = f"dnd_item_{category}_{index}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        try:
            response = requests.get(f"{BASE_URL}/{category}/{index}")
            if response.status_code != 200:
                return {"error": f"Item '{index}' not found in category '{category}' or API request failed"}

            data = response.json()

            # Cache the result
            cache.set(cache_key, data)
            return data

        except Exception as e:
            logger.exception(f"Error fetching item {category}/{index}: {e}")
            return {"error": f"Failed to fetch item details: {str(e)}"}

    def _convert_currency(amount: float, from_unit: str, to_unit: str) -> float:
        """Convert currency between different units (gp, sp, cp)."""
        # Conversion rates
        rates = {
            "cp": 0.01,  # 1 cp = 0.01 gp
            "sp": 0.1,   # 1 sp = 0.1 gp
            "gp": 1.0,   # 1 gp = 1 gp
            "pp": 10.0   # 1 pp = 10 gp
        }

        # Convert to gp first
        gp_value = amount * rates.get(from_unit.lower(), 1.0)

        # Convert from gp to target unit
        target_rate = rates.get(to_unit.lower(), 1.0)
        if target_rate == 0:
            return 0

        return gp_value / target_rate

    def _get_description(item: Dict[str, Any]) -> str:
        """Extract description from an item, handling different formats."""
        desc = item.get("desc", "")

        # Handle list of descriptions
        if isinstance(desc, list):
            if desc:
                return desc[0][:100] + "..." if len(desc[0]) > 100 else desc[0]
            return "No description available"

        # Handle string description
        if isinstance(desc, str):
            return desc[:100] + "..." if len(desc) > 100 else desc

        return "No description available"

    print("D&D API tools registered successfully", file=sys.stderr)
