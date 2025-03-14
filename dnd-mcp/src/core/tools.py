#!/usr/bin/env python3
import sys
import json
import traceback
import urllib.request
import urllib.error
import urllib.parse
import mcp.types as types
from src.core.api_helpers import API_BASE_URL
from src.core.formatters import format_monster_data, format_spell_data, format_class_data
import requests
import logging
from typing import List, Dict, Any, Optional
from src.core.cache import APICache
import src.core.formatters as formatters
import src.core.resources as resources
import time
# Import our new source attribution system
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
# Import our new template system
from src.templates import (
    format_dnd_data,
    format_search_results,
    TEMPLATES_ENABLED
)
# Import our query enhancement module
from src.query_enhancement import (
    enhance_query,
    expand_query_with_synonyms,
    tokenize_dnd_query,
    fuzzy_match,
    prioritize_categories,
    get_top_categories
)

logger = logging.getLogger(__name__)

# Base URL for the D&D 5e API
BASE_URL = "https://www.dnd5eapi.co/api"
# Request timeout in seconds
REQUEST_TIMEOUT = 10


def register_tools(app, cache: APICache):
    """Register D&D API tools with the FastMCP app.

    Args:
        app: The FastMCP app instance
        cache: The shared API cache
    """
    print("Registering D&D API tools...", file=sys.stderr)

    @app.tool()
    def search_equipment_by_cost(max_cost: float, cost_unit: str = "gp") -> Dict[str, Any]:
        """Search for D&D equipment items that cost less than or equal to a specified maximum price.

        This tool helps find affordable equipment options for character creation or in-game purchases.
        Results include item details such as name, cost, weight, and category.

        Args:
            max_cost: Maximum cost value (e.g., 10 for items costing 10 or less of the specified currency)
            cost_unit: Currency unit (gp=gold pieces, sp=silver pieces, cp=copper pieces)

        Returns:
            A dictionary containing equipment items within the specified cost range, with source attribution
            to the D&D 5e API.
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
        """Find D&D spells within a specific level range and optionally from a particular magic school.

        This tool is useful for spellcasters looking for spells they can cast at their current level,
        or for finding appropriate spells for NPCs, scrolls, or other magical items. Results include
        spell names, levels, schools, and basic casting information.

        Args:
            min_level: Minimum spell level (0-9, where 0 represents cantrips)
            max_level: Maximum spell level (0-9, where 9 represents 9th-level spells)
            school: Magic school filter (abjuration, conjuration, divination, enchantment, 
                   evocation, illusion, necromancy, transmutation)

        Returns:
            A dictionary containing spells that match the specified criteria, with source attribution
            to the D&D 5e API.
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
        """Find D&D monsters within a specific challenge rating (CR) range for encounter building.

        This tool helps Dungeon Masters find appropriate monsters for encounters based on party level
        and desired difficulty. Results include monster names, challenge ratings, types, and basic stats.

        Challenge ratings indicate a monster's relative threat level:
        - CR 0-4: Low-level threats suitable for parties of levels 1-4
        - CR 5-10: Mid-level threats suitable for parties of levels 5-10
        - CR 11-16: High-level threats suitable for parties of levels 11-16
        - CR 17+: Epic threats suitable for parties of levels 17+

        Args:
            min_cr: Minimum challenge rating (0 to 30, can use fractions like 0.25, 0.5)
            max_cr: Maximum challenge rating (0 to 30)

        Returns:
            A dictionary containing monsters within the specified CR range, with source attribution
            to the D&D 5e API.
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
    @track_tool_usage(ToolCategory.SEARCH)
    def search_all_categories(query: str) -> Dict[str, Any]:
        """Search across all D&D 5e API categories for any D&D content matching the query.

        This is the primary search tool for finding D&D content. It searches across all available
        categories including spells, monsters, equipment, classes, races, magic items, and more.
        Results are ranked by relevance and include a "top results" section showing the best matches
        across all categories.

        The search is intelligent and considers:
        - Exact name matches
        - Partial name matches
        - Matches in descriptions
        - Content relevance to the query
        - D&D-specific synonyms and abbreviations
        - Special D&D terms and notation
        - Common misspellings of D&D terms

        For more specific searches, consider using category-specific tools like filter_spells_by_level
        or find_monsters_by_challenge_rating.

        Args:
            query: Search term (minimum 3 characters) to find across all D&D content

        Returns:
            A comprehensive dictionary containing matching items across all categories, organized by
            category with a "top_results" section highlighting the best matches, and source attribution
            to the D&D 5e API.
        """
        logger.debug(f"Searching all categories for: {query}")

        # Clear previous tool usages for this request
        source_tracker.tool_tracker.clear()

        if not query or len(query.strip()) < 3:
            error_response = {
                "error": "Search query must be at least 3 characters long",
                "message": "Please provide a more specific search term",
            }

            # Add attribution for the error message
            error_attr_id = attribution_manager.add_attribution(
                attribution=SourceAttribution(
                    source="D&D 5e API",
                    api_endpoint="N/A",
                    confidence=ConfidenceLevel.HIGH,
                    relevance_score=100.0,
                    tool_used="search_all_categories"
                )
            )

            # Prepare response with attribution for MCP
            return source_tracker.prepare_mcp_response(
                error_response,
                {"error": error_attr_id, "message": error_attr_id}
            )

        # Get available categories
        categories_response = requests.get(
            f"{BASE_URL}", timeout=REQUEST_TIMEOUT)
        if categories_response.status_code != 200:
            error_response = {
                "error": "Failed to fetch categories",
                "message": "API request failed, please try again",
            }

            # Add attribution for the error message
            error_attr_id = attribution_manager.add_attribution(
                attribution=SourceAttribution(
                    source="D&D 5e API",
                    api_endpoint=f"{BASE_URL}",
                    confidence=ConfidenceLevel.HIGH,
                    relevance_score=100.0,
                    tool_used="search_all_categories"
                )
            )

            # Prepare response with attribution for MCP
            return source_tracker.prepare_mcp_response(
                error_response,
                {"error": error_attr_id, "message": error_attr_id}
            )

        categories = list(categories_response.json().keys())

        # Enhance the query using our query enhancement module
        enhanced_query, enhancements = enhance_query(query)

        # Add attribution for the query enhancement
        enhancement_attr_id = attribution_manager.add_attribution(
            attribution=SourceAttribution(
                source="D&D Knowledge Navigator",
                api_endpoint="query_enhancement",
                confidence=ConfidenceLevel.HIGH,
                relevance_score=90.0,
                tool_used="search_all_categories",
                metadata={
                    "original_query": query,
                    "enhanced_query": enhanced_query,
                    "synonyms_added": [f"{orig} → {exp}" for orig, exp in enhancements["synonyms_added"]],
                    "special_terms": enhancements["special_terms"],
                    "fuzzy_matches": [f"{orig} → {corr}" for orig, corr in enhancements["fuzzy_matches"]]
                }
            )
        )

        # Use the enhanced query for tokenization
        query_tokens = [token.lower()
                        for token in enhanced_query.split() if len(token) > 2]

        # Use category prioritization from our module
        category_priorities = enhancements["category_priorities"]

        # Convert normalized scores (0-1) to priority multipliers (1-10)
        for category in category_priorities:
            if category in categories:
                category_priorities[category] = 1 + \
                    (category_priorities[category] * 9)
            else:
                category_priorities[category] = 1

        # Search each category
        results = {}
        total_count = 0
        all_matches = []
        attribution_map = {}

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

                # Also check for exact match with enhanced query
                if enhanced_query.lower() != query.lower() and (
                        enhanced_query.lower() == item_name or enhanced_query.lower() == item_index):
                    score += 90

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
                    score += 25

                # Search in description if available
                if item_details and isinstance(item_details, dict):
                    description = ""

                    # Extract description based on item type
                    if "desc" in item_details:
                        if isinstance(item_details["desc"], list):
                            description = " ".join(item_details["desc"])
                        else:
                            description = str(item_details["desc"])
                    elif "description" in item_details:
                        description = str(item_details["description"])

                    description = description.lower()

                    # Score based on description matches
                    for token in query_tokens:
                        if token in description:
                            score += 10

                    # Bonus for multiple token matches in description
                    matching_tokens = sum(
                        1 for token in query_tokens if token in description)
                    if matching_tokens > 1:
                        score += matching_tokens * 5

                # Apply category priority multiplier
                score *= category_priorities.get(category, 1)

                # Add to results if score is above threshold
                if score > 0:
                    # Create attribution for this item
                    confidence_level = ConfidenceLevel.HIGH if score > 70 else (
                        ConfidenceLevel.MEDIUM if score > 40 else ConfidenceLevel.LOW
                    )

                    item_attr_id = attribution_manager.add_attribution(
                        attribution=SourceAttribution(
                            source="D&D 5e API",
                            api_endpoint=f"{BASE_URL}/{category}/{item['index']}",
                            confidence=confidence_level,
                            relevance_score=min(score, 100),
                            tool_used="search_all_categories",
                            metadata={
                                "category": category,
                                "score": score
                            }
                        )
                    )

                    item_with_score = item.copy()
                    item_with_score["score"] = score
                    item_with_score["attribution_id"] = item_attr_id
                    matching_items.append(item_with_score)

                    # Add to all matches for cross-category top results
                    all_matches.append({
                        "category": category,
                        "item": item_with_score
                    })

            # Sort matching items by score
            matching_items.sort(key=lambda x: x["score"], reverse=True)

            # Add to results if there are matches
            if matching_items:
                # Create attribution for this category's results
                category_attr_id = attribution_manager.add_attribution(
                    attribution=SourceAttribution(
                        source="D&D 5e API",
                        api_endpoint=f"{BASE_URL}/{category}",
                        confidence=ConfidenceLevel.HIGH,
                        relevance_score=85.0,
                        tool_used="search_all_categories",
                        metadata={
                            "item_count": len(matching_items)
                        }
                    )
                )

                results[category] = {
                    "items": matching_items,
                    "count": len(matching_items),
                }
                attribution_map[f"results.{category}"] = category_attr_id
                total_count += len(matching_items)

        # Sort all matches by score for top results across categories
        all_matches.sort(key=lambda x: x["item"]["score"], reverse=True)
        # Get top 10 results across all categories
        top_results = all_matches[:10]

        # Create attribution for the overall search results
        search_attr_id = attribution_manager.add_attribution(
            attribution=SourceAttribution(
                source="D&D 5e API",
                api_endpoint=f"{BASE_URL}",
                confidence=ConfidenceLevel.HIGH,
                relevance_score=90.0,
                tool_used="search_all_categories",
                metadata={
                    "query": query,
                    "enhanced_query": enhanced_query,
                    "total_results": total_count
                }
            )
        )

        # Create the response data
        response_data = {
            "query": query,
            "enhanced_query": enhanced_query,
            "query_enhancements": {
                "synonyms_added": [f"{orig} → {exp}" for orig, exp in enhancements["synonyms_added"]],
                "special_terms": enhancements["special_terms"],
                "fuzzy_matches": [f"{orig} → {corr}" for orig, corr in enhancements["fuzzy_matches"]]
            },
            "results": results,
            "total_count": total_count,
            "top_results": [
                {
                    "category": match["category"],
                    "name": match["item"]["name"],
                    "index": match["item"]["index"],
                    "score": match["item"]["score"],
                }
                for match in top_results
            ],
        }

        # Add attributions for top results
        for i, match in enumerate(top_results):
            attribution_map[f"top_results.{i}"] = match["item"]["attribution_id"]

        # Add attribution for the overall response
        attribution_map["query"] = search_attr_id
        attribution_map["enhanced_query"] = enhancement_attr_id
        attribution_map["query_enhancements"] = enhancement_attr_id
        attribution_map["total_count"] = search_attr_id

        # Format the response using our template system if enabled
        if TEMPLATES_ENABLED:
            formatted_content = format_search_results(
                response_data, include_attribution=False)
            response_data["content"] = formatted_content

        # Prepare the final response with all attributions
        return source_tracker.prepare_mcp_response(response_data, attribution_map)

    @app.tool()
    @track_tool_usage(ToolCategory.SEARCH)
    def verify_with_api(statement: str, category: str = None) -> Dict[str, Any]:
        """Verify the accuracy of a D&D statement by checking it against the official D&D 5e API data.

        This tool analyzes a statement about D&D 5e rules, creatures, spells, or other game elements
        and verifies its accuracy by searching the official D&D 5e API. It extracts key terms from
        the statement and searches for relevant information.

        The verification process:
        1. Extracts key terms from the statement
        2. Searches the D&D 5e API for these terms
        3. Analyzes the search results to verify the statement
        4. Returns the verification results with confidence levels
        5. Includes source attribution for all information

        Args:
            statement: The D&D statement to verify (e.g., "Fireball is a 3rd-level evocation spell")
            category: Optional category to focus the search (e.g., "spells", "monsters", "classes")

        Returns:
            A dictionary containing verification results, relevant D&D information, and source attribution.
        """
        logger.debug(f"Verifying statement: {statement}")

        # Clear previous tool usages for this request
        source_tracker.tool_tracker.clear()

        # Extract key terms from the statement
        # Filter out common words and keep only meaningful terms
        common_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "with", "by", "about", "against", "between", "into", "through", "during",
            "before", "after", "above", "below", "from", "up", "down", "of", "off",
            "over", "under", "again", "further", "then", "once", "here", "there",
            "when", "where", "why", "how", "all", "any", "both", "each", "few",
            "more", "most", "other", "some", "such", "no", "nor", "not", "only",
            "own", "same", "so", "than", "too", "very", "s", "t", "can", "will",
            "just", "don", "should", "now", "d&d", "dnd", "dungeons", "dragons",
            "dungeon", "dragon", "player", "character", "dm", "game", "roll", "dice",
            "rules", "rule", "edition", "5e", "fifth"
        }

        # Use our query enhancement module to extract key terms
        enhanced_statement, enhancements = enhance_query(statement)

        # Get special terms and synonyms from the enhancements
        special_terms = enhancements["special_terms"]

        # Extract search terms from the statement
        words = statement.lower().split()
        search_terms = [word.strip('.,?!;:()"\'') for word in words
                        if word.strip('.,?!;:()"\'') not in common_words
                        and len(word.strip('.,?!;:()"\'-')) > 2]

        # Add special terms to search terms if they're not already included
        for term in special_terms:
            term_lower = term.lower()
            if term_lower not in search_terms:
                search_terms.append(term_lower)

        # Add expanded terms from synonyms
        for original, expanded in enhancements["synonyms_added"]:
            if expanded.lower() not in search_terms:
                search_terms.append(expanded.lower())

        # Add corrections from fuzzy matches
        for original, correction in enhancements["fuzzy_matches"]:
            if correction.lower() not in search_terms:
                search_terms.append(correction.lower())

        # Remove duplicates while preserving order
        unique_search_terms = []
        for term in search_terms:
            if term not in unique_search_terms:
                unique_search_terms.append(term)
        search_terms = unique_search_terms

        # Create attribution for the statement analysis
        statement_attr_id = attribution_manager.add_attribution(
            attribution=SourceAttribution(
                source="D&D Knowledge Navigator",
                api_endpoint="statement_analysis",
                confidence=ConfidenceLevel.HIGH,
                relevance_score=100.0,
                tool_used="verify_with_api",
                metadata={
                    "statement": statement,
                    "search_terms": search_terms,
                    "enhanced_statement": enhanced_statement
                }
            )
        )

        # Initialize results
        results = {}
        found_matches = False
        attribution_map = {
            "statement": statement_attr_id,
            "search_terms": statement_attr_id
        }

        if category:
            # Search in specific category
            category_data = _get_category_items(category, cache)
            if "error" not in category_data:
                matching_items = []
                for item in category_data.get("items", []):
                    item_name = item["name"].lower()
                    if any(term in item_name for term in search_terms):
                        item_details = _get_item_details(
                            category, item["index"], cache)
                        if "error" not in item_details:
                            # Create attribution for this item
                            item_attr_id = attribution_manager.add_attribution(
                                attribution=SourceAttribution(
                                    source="D&D 5e API",
                                    api_endpoint=f"{BASE_URL}/{category}/{item['index']}",
                                    confidence=ConfidenceLevel.HIGH,
                                    relevance_score=90.0,
                                    tool_used="verify_with_api",
                                    metadata={
                                        "category": category,
                                        "statement": statement
                                    }
                                )
                            )

                            matching_items.append({
                                "name": item["name"],
                                "details": item_details,
                                "attribution_id": item_attr_id
                            })

                if matching_items:
                    results[category] = matching_items
                    found_matches = True
                    attribution_map[f"results.{category}"] = statement_attr_id
        else:
            # Use category prioritization from our module to focus the search
            category_priorities = enhancements["category_priorities"]
            top_categories = get_top_categories(enhanced_statement, 5)

            # Search across prioritized categories
            search_query = " ".join(search_terms)

            # First, try the top categories
            for category_name in top_categories:
                category_data = _get_category_items(category_name, cache)
                if "error" not in category_data:
                    matching_items = []
                    for item in category_data.get("items", []):
                        item_name = item["name"].lower()
                        if any(term in item_name for term in search_terms):
                            item_details = _get_item_details(
                                category_name, item["index"], cache)
                            if "error" not in item_details:
                                # Create attribution for this item
                                item_attr_id = attribution_manager.add_attribution(
                                    attribution=SourceAttribution(
                                        source="D&D 5e API",
                                        api_endpoint=f"{BASE_URL}/{category_name}/{item['index']}",
                                        confidence=ConfidenceLevel.MEDIUM,
                                        relevance_score=category_priorities.get(
                                            category_name, 0.5) * 100,
                                        tool_used="verify_with_api",
                                        metadata={
                                            "category": category_name,
                                            "statement": statement
                                        }
                                    )
                                )

                                matching_items.append({
                                    "name": item["name"],
                                    "details": item_details,
                                    "attribution_id": item_attr_id
                                })

                    if matching_items:
                        results[category_name] = matching_items
                        found_matches = True
                        attribution_map[f"results.{category_name}"] = statement_attr_id

            # If no matches found in top categories, fall back to search_all_categories
            if not found_matches:
                all_results = search_all_categories(search_query)

                if all_results.get("total_count", 0) > 0:
                    for category_name, category_data in all_results.get("results", {}).items():
                        matching_items = []
                        for item in category_data.get("items", []):
                            item_details = _get_item_details(
                                category_name, item["index"], cache)
                            if "error" not in item_details:
                                # Create attribution for this item
                                item_attr_id = attribution_manager.add_attribution(
                                    attribution=SourceAttribution(
                                        source="D&D 5e API",
                                        api_endpoint=f"{BASE_URL}/{category_name}/{item['index']}",
                                        confidence=ConfidenceLevel.MEDIUM,
                                        relevance_score=item.get(
                                            "score", 50.0),
                                        tool_used="verify_with_api",
                                        metadata={
                                            "category": category_name,
                                            "statement": statement
                                        }
                                    )
                                )

                                matching_items.append({
                                    "name": item["name"],
                                    "details": item_details,
                                    "attribution_id": item_attr_id
                                })

                        if matching_items:
                            results[category_name] = matching_items
                            found_matches = True
                            attribution_map[f"results.{category_name}"] = statement_attr_id

        # Create attribution for the overall verification result
        verification_attr_id = attribution_manager.add_attribution(
            attribution=SourceAttribution(
                source="D&D 5e API",
                api_endpoint=f"{BASE_URL}",
                confidence=ConfidenceLevel.HIGH if found_matches else ConfidenceLevel.LOW,
                relevance_score=85.0 if found_matches else 30.0,
                tool_used="verify_with_api",
                metadata={
                    "statement": statement,
                    "found_matches": found_matches,
                    "categories_checked": list(results.keys()) if results else []
                }
            )
        )

        # Create the response data
        response_data = {
            "statement": statement,
            "enhanced_statement": enhanced_statement,
            "search_terms": search_terms,
            "results": results,
            "found_matches": found_matches,
            "query_enhancements": {
                "synonyms_added": [f"{orig} → {exp}" for orig, exp in enhancements["synonyms_added"]],
                "special_terms": enhancements["special_terms"],
                "fuzzy_matches": [f"{orig} → {corr}" for orig, corr in enhancements["fuzzy_matches"]]
            }
        }

        # Add attribution for the overall response
        attribution_map["found_matches"] = verification_attr_id
        attribution_map["enhanced_statement"] = statement_attr_id
        attribution_map["query_enhancements"] = statement_attr_id

        # Format the response using our template system if enabled
        if TEMPLATES_ENABLED:
            formatted_content = f"# Verification of D&D Statement\n\n"
            formatted_content += f"**Statement:** {statement}\n\n"

            if found_matches:
                formatted_content += "## Verification Results\n\n"
                formatted_content += f"Found information related to {len(search_terms)} search terms: "
                formatted_content += f"*{', '.join(search_terms)}*\n\n"

                # Format each category's results
                for category_name, items in results.items():
                    formatted_content += f"### {category_name.replace('_', ' ').title()}\n\n"

                    for item in items:
                        # Format the item details using our template system
                        item_details = item.get("details", {})
                        item_type = category_name[:-1] if category_name.endswith(
                            's') else category_name

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
            else:
                formatted_content += "## No Matching Information Found\n\n"
                formatted_content += "Could not find specific information to verify this statement in the D&D 5e API.\n\n"
                formatted_content += f"Search terms used: *{', '.join(search_terms)}*\n\n"

            response_data["content"] = formatted_content

        # Prepare the final response with all attributions
        return source_tracker.prepare_mcp_response(response_data, attribution_map)

    @app.tool()
    @track_tool_usage(ToolCategory.CONTEXT)
    def check_api_health() -> Dict[str, Any]:
        """Check the health and status of the D&D 5e API.

        This tool verifies that the D&D 5e API is operational and provides information
        about available endpoints and resources. It's useful for diagnosing issues or
        understanding what data is available.

        The health check includes:
        1. Verifying the base API endpoint is accessible
        2. Checking key endpoints (spells, monsters, classes)
        3. Reporting on available categories and their status
        4. Providing counts of available resources

        Returns:
            A dictionary containing API status information, available endpoints,
            resource counts, and source attribution to the D&D 5e API.
        """
        logger.debug("Checking API health")

        # Clear previous tool usages for this request
        source_tracker.tool_tracker.clear()

        # Check base API endpoint
        try:
            base_response = requests.get(
                f"{BASE_URL}", timeout=REQUEST_TIMEOUT)
            base_status = base_response.status_code == 200
            base_data = base_response.json() if base_status else {}
        except Exception as e:
            logger.error(f"Error checking base API: {e}")
            base_status = False
            base_data = {}

        # Create attribution for the base API check
        base_attr_id = attribution_manager.add_attribution(
            attribution=SourceAttribution(
                source="D&D 5e API",
                api_endpoint=f"{BASE_URL}",
                confidence=ConfidenceLevel.HIGH,
                relevance_score=100.0,
                tool_used="check_api_health",
                metadata={
                    "status": base_status
                }
            )
        )

        if not base_status:
            error_response = {
                "status": "error",
                "message": "D&D 5e API is not responding",
                "details": "The base API endpoint could not be reached. Please try again later."
            }

            # Prepare response with attribution for MCP
            return source_tracker.prepare_mcp_response(
                error_response,
                {"status": base_attr_id, "message": base_attr_id,
                    "details": base_attr_id}
            )

        # Check key endpoints
        endpoints_status = {}
        endpoints_attr_ids = {}

        key_endpoints = ["spells", "monsters", "classes"]
        for endpoint in key_endpoints:
            try:
                endpoint_response = requests.get(
                    f"{BASE_URL}/{endpoint}", timeout=REQUEST_TIMEOUT)
                endpoint_status = endpoint_response.status_code == 200
                endpoint_data = endpoint_response.json() if endpoint_status else {}
                count = endpoint_data.get("count", 0) if endpoint_status else 0
                endpoints_status[endpoint] = {
                    "status": endpoint_status,
                    "count": count
                }

                # Create attribution for this endpoint check
                endpoint_attr_id = attribution_manager.add_attribution(
                    attribution=SourceAttribution(
                        source="D&D 5e API",
                        api_endpoint=f"{BASE_URL}/{endpoint}",
                        confidence=ConfidenceLevel.HIGH,
                        relevance_score=90.0,
                        tool_used="check_api_health",
                        metadata={
                            "status": endpoint_status,
                            "count": count
                        }
                    )
                )
                endpoints_attr_ids[endpoint] = endpoint_attr_id

            except Exception as e:
                logger.error(f"Error checking {endpoint} endpoint: {e}")
                endpoints_status[endpoint] = {
                    "status": False,
                    "error": str(e)
                }

                # Create attribution for this endpoint error
                endpoint_attr_id = attribution_manager.add_attribution(
                    attribution=SourceAttribution(
                        source="D&D 5e API",
                        api_endpoint=f"{BASE_URL}/{endpoint}",
                        confidence=ConfidenceLevel.LOW,
                        relevance_score=50.0,
                        tool_used="check_api_health",
                        metadata={
                            "status": False,
                            "error": str(e)
                        }
                    )
                )
                endpoints_attr_ids[endpoint] = endpoint_attr_id

        # Create the health check result
        health_check = {
            "status": "healthy" if base_status and all(endpoint["status"] for endpoint in endpoints_status.values()) else "degraded",
            "base_api": {
                "status": "online" if base_status else "offline",
                "available_categories": list(base_data.keys()) if base_status else []
            },
            "key_endpoints": endpoints_status,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }

        # Create attribution for the overall health check
        health_attr_id = attribution_manager.add_attribution(
            attribution=SourceAttribution(
                source="D&D 5e API",
                api_endpoint=f"{BASE_URL}",
                confidence=ConfidenceLevel.HIGH,
                relevance_score=95.0,
                tool_used="check_api_health",
                metadata={
                    "status": health_check["status"],
                    "timestamp": health_check["timestamp"]
                }
            )
        )

        # Create attribution map
        attribution_map = {
            "status": health_attr_id,
            "base_api": base_attr_id,
            "timestamp": health_attr_id
        }

        # Add attributions for key endpoints
        for endpoint in key_endpoints:
            attribution_map[f"key_endpoints.{endpoint}"] = endpoints_attr_ids[endpoint]

        # Format the health check result using our template system if enabled
        if TEMPLATES_ENABLED:
            formatted_content = f"# D&D 5e API Health Check\n\n"
            formatted_content += f"**Status:** {health_check['status'].upper()}\n"
            formatted_content += f"**Timestamp:** {health_check['timestamp']}\n\n"

            formatted_content += "## Base API\n\n"
            formatted_content += f"**Status:** {health_check['base_api']['status']}\n"

            if health_check['base_api']['available_categories']:
                formatted_content += f"**Available Categories:** {len(health_check['base_api']['available_categories'])}\n\n"
                formatted_content += "Categories:\n"
                for category in sorted(health_check['base_api']['available_categories']):
                    formatted_content += f"- {category}\n"
            else:
                formatted_content += "No categories available.\n"

            formatted_content += "\n## Key Endpoints\n\n"

            for endpoint, status in health_check['key_endpoints'].items():
                formatted_content += f"### {endpoint.title()}\n\n"
                formatted_content += f"**Status:** {status['status']}\n"

                if 'count' in status:
                    formatted_content += f"**Available Items:** {status['count']}\n"

                if 'error' in status:
                    formatted_content += f"**Error:** {status['error']}\n"

                formatted_content += "\n"

            health_check["content"] = formatted_content

        # Prepare the final response with all attributions
        return source_tracker.prepare_mcp_response(health_check, attribution_map)

    @app.tool()
    def generate_treasure_hoard(challenge_rating: float, is_final_treasure: bool = False, treasure_type: str = "hoard") -> Dict[str, Any]:
        """Generate D&D 5e treasure based on challenge rating and context.

        This tool creates appropriate treasure for encounters or dungeons following the
        Dungeon Master's Guide treasure tables. It uses official D&D 5e API data for
        equipment and magic items to ensure accuracy.

        The treasure is balanced according to the challenge rating provided, with higher
        CR values resulting in more valuable treasure. Final treasure (such as at the end
        of a dungeon) can be made more significant by setting is_final_treasure to True.

        Args:
            challenge_rating: The challenge rating to base treasure on (0.25 to 30)
            is_final_treasure: Whether this is a climactic treasure (increases value)
            treasure_type: Type of treasure to generate ("individual" or "hoard")

        Returns:
            A dictionary containing generated treasure including coins, equipment items, and magic items
            with source attribution to the D&D 5e API.
        """
        logger.debug(
            f"Generating {treasure_type} treasure for CR {challenge_rating}, final: {is_final_treasure}")

        # Validate inputs
        if challenge_rating < 0 or challenge_rating > 30:
            return {
                "error": "Challenge rating must be between 0 and 30",
                "message": "Please provide a valid challenge rating",
                "source": "D&D 5e API"
            }

        if treasure_type not in ["individual", "hoard"]:
            return {
                "error": "Invalid treasure type",
                "message": "Treasure type must be 'individual' or 'hoard'",
                "source": "D&D 5e API"
            }

        # Determine treasure table based on CR
        if challenge_rating <= 4:
            cr_tier = "0-4"
        elif challenge_rating <= 10:
            cr_tier = "5-10"
        elif challenge_rating <= 16:
            cr_tier = "11-16"
        else:
            cr_tier = "17+"

        # Generate coins based on DMG tables
        coins = _generate_coins_from_dmg(cr_tier, treasure_type)

        # Get equipment from API
        equipment_items = _get_equipment_for_treasure(
            cr_tier, treasure_type, cache)

        # Get magic items from API for hoards
        magic_items = []
        if treasure_type == "hoard":
            magic_items = _get_magic_items_for_treasure(
                cr_tier, is_final_treasure, cache)

        # Apply final treasure bonus if applicable
        if is_final_treasure:
            coins = _apply_final_treasure_bonus(coins)

        # Calculate total value
        total_value = _calculate_total_value(
            coins, equipment_items, magic_items)

        return {
            "challenge_rating": challenge_rating,
            "treasure_type": treasure_type,
            "cr_tier": cr_tier,
            "is_final_treasure": is_final_treasure,
            "coins": coins,
            "equipment_items": equipment_items,
            "magic_items": magic_items,
            "total_value_gp": total_value,
            "source": "D&D 5e API"
        }

    def _generate_coins_from_dmg(cr_tier: str, treasure_type: str) -> Dict[str, int]:
        """Generate coins based on DMG treasure tables."""
        import random

        coins = {"cp": 0, "sp": 0, "gp": 0, "pp": 0}

        # DMG Individual Treasure Tables (p.136)
        if treasure_type == "individual":
            if cr_tier == "0-4":
                roll = random.randint(1, 100)
                if roll <= 30:
                    coins["cp"] = random.randint(5, 30)
                elif roll <= 60:
                    coins["sp"] = random.randint(4, 24)
                elif roll <= 70:
                    coins["ep"] = random.randint(3, 18)
                elif roll <= 95:
                    coins["gp"] = random.randint(3, 18)
                else:
                    coins["pp"] = random.randint(1, 6)

            elif cr_tier == "5-10":
                roll = random.randint(1, 100)
                if roll <= 30:
                    coins["cp"] = random.randint(4, 24) * 100
                    coins["sp"] = random.randint(6, 36) * 10
                elif roll <= 60:
                    coins["sp"] = random.randint(2, 12) * 100
                    coins["gp"] = random.randint(2, 12) * 10
                elif roll <= 70:
                    coins["ep"] = random.randint(2, 12) * 10
                    coins["gp"] = random.randint(2, 12) * 10
                elif roll <= 95:
                    coins["gp"] = random.randint(4, 24) * 10
                else:
                    coins["gp"] = random.randint(2, 12) * 10
                    coins["pp"] = random.randint(3, 18)

            elif cr_tier == "11-16":
                roll = random.randint(1, 100)
                if roll <= 20:
                    coins["sp"] = random.randint(4, 24) * 100
                    coins["gp"] = random.randint(1, 6) * 100
                elif roll <= 35:
                    coins["ep"] = random.randint(1, 6) * 100
                    coins["gp"] = random.randint(1, 6) * 100
                elif roll <= 75:
                    coins["gp"] = random.randint(2, 12) * 100
                    coins["pp"] = random.randint(1, 6) * 10
                else:
                    coins["gp"] = random.randint(2, 12) * 100
                    coins["pp"] = random.randint(2, 12) * 10

            else:  # cr_tier == "17+"
                roll = random.randint(1, 100)
                if roll <= 15:
                    coins["ep"] = random.randint(2, 12) * 1000
                    coins["gp"] = random.randint(8, 48) * 100
                elif roll <= 55:
                    coins["gp"] = random.randint(1, 6) * 1000
                    coins["pp"] = random.randint(1, 6) * 100
                else:
                    coins["gp"] = random.randint(1, 6) * 1000
                    coins["pp"] = random.randint(2, 12) * 100

        # DMG Treasure Hoard Tables (p.137-139)
        else:  # treasure_type == "hoard"
            if cr_tier == "0-4":
                coins["cp"] = random.randint(6, 36) * 100
                coins["sp"] = random.randint(3, 18) * 100
                coins["gp"] = random.randint(2, 12) * 10

            elif cr_tier == "5-10":
                coins["cp"] = random.randint(2, 12) * 100
                coins["sp"] = random.randint(2, 12) * 1000
                coins["gp"] = random.randint(6, 36) * 100
                coins["pp"] = random.randint(3, 18) * 10

            elif cr_tier == "11-16":
                coins["gp"] = random.randint(4, 24) * 1000
                coins["pp"] = random.randint(5, 30) * 100

            else:  # cr_tier == "17+"
                coins["gp"] = random.randint(12, 72) * 1000
                coins["pp"] = random.randint(8, 48) * 1000

        return coins

    def _get_equipment_for_treasure(cr_tier: str, treasure_type: str, cache: APICache) -> List[Dict[str, Any]]:
        """Get equipment items from the D&D 5e API based on CR tier."""
        import random

        # Get all equipment from API
        equipment_list = _get_category_items("equipment", cache)
        if "error" in equipment_list:
            return []

        # Number of items to include
        num_items = 0
        if treasure_type == "individual":
            num_items = random.randint(0, 2)
        else:  # hoard
            if cr_tier == "0-4":
                num_items = random.randint(2, 5)
            elif cr_tier == "5-10":
                num_items = random.randint(2, 6)
            elif cr_tier == "11-16":
                num_items = random.randint(1, 4)
            else:  # 17+
                num_items = random.randint(1, 3)

        # Value ranges by CR tier (in gp)
        value_ranges = {
            "0-4": (1, 50),
            "5-10": (10, 250),
            "11-16": (50, 750),
            "17+": (100, 2500)
        }

        min_value, max_value = value_ranges[cr_tier]

        # Filter equipment by value
        valuable_items = []
        for item in equipment_list.get("items", []):
            item_index = item["index"]
            item_details = _get_item_details("equipment", item_index, cache)

            if "error" in item_details or not isinstance(item_details, dict):
                continue

            # Check if item has cost
            if "cost" in item_details:
                cost = item_details["cost"]
                value_in_gp = _convert_currency(
                    cost["quantity"], cost["unit"], "gp")

                # Check if value is in appropriate range
                if min_value <= value_in_gp <= max_value:
                    valuable_items.append({
                        "name": item_details["name"],
                        "value": f"{cost['quantity']} {cost['unit']}",
                        "value_in_gp": value_in_gp,
                        "description": _get_description(item_details),
                        "uri": f"resource://dnd/item/equipment/{item_index}"
                    })

        # Select random items
        selected_items = []
        if valuable_items:
            # Ensure we don't try to select more items than are available
            num_items = min(num_items, len(valuable_items))
            selected_items = random.sample(valuable_items, num_items)

        return selected_items

    def _get_magic_items_for_treasure(cr_tier: str, is_final_treasure: bool, cache: APICache) -> List[Dict[str, Any]]:
        """Get magic items from the D&D 5e API based on CR tier."""
        import random

        # Get all magic items from API
        magic_items_list = _get_category_items("magic-items", cache)
        if "error" in magic_items_list:
            return []

        # Number of magic items by CR tier
        num_items_range = {
            "0-4": (0, 2),
            "5-10": (1, 3),
            "11-16": (1, 4),
            "17+": (2, 6)
        }

        min_items, max_items = num_items_range[cr_tier]
        if is_final_treasure:
            max_items += 1

        num_items = random.randint(min_items, max_items)

        # Rarity weights by CR tier
        rarity_weights = {
            # Common, Uncommon, Rare, Very Rare, Legendary
            "0-4": [70, 25, 5, 0, 0],
            "5-10": [20, 50, 25, 5, 0],
            "11-16": [5, 25, 45, 20, 5],
            "17+": [0, 10, 30, 40, 20]
        }

        # Group items by rarity
        items_by_rarity = {
            "Common": [],
            "Uncommon": [],
            "Rare": [],
            "Very Rare": [],
            "Legendary": []
        }

        # Categorize all magic items by rarity
        for item in magic_items_list.get("items", []):
            item_index = item["index"]
            item_details = _get_item_details("magic-items", item_index, cache)

            if "error" in item_details or not isinstance(item_details, dict):
                continue

            rarity = item_details.get("rarity", {}).get("name", "Unknown")
            if rarity in items_by_rarity:
                items_by_rarity[rarity].append(item_details)

        # Select magic items based on appropriate rarity for the tier
        selected_items = []
        for _ in range(num_items):
            # Choose rarity based on tier weights
            weights = rarity_weights[cr_tier]
            rarity_roll = random.randint(1, 100)

            chosen_rarity = "Common"  # Default
            if rarity_roll <= weights[0]:
                chosen_rarity = "Common"
            elif rarity_roll <= weights[0] + weights[1]:
                chosen_rarity = "Uncommon"
            elif rarity_roll <= weights[0] + weights[1] + weights[2]:
                chosen_rarity = "Rare"
            elif rarity_roll <= weights[0] + weights[1] + weights[2] + weights[3]:
                chosen_rarity = "Very Rare"
            else:
                chosen_rarity = "Legendary"

            # If no items of chosen rarity, pick next lower rarity
            available_rarities = [r for r in ["Common", "Uncommon", "Rare", "Very Rare", "Legendary"]
                                  if items_by_rarity[r]]
            if not items_by_rarity[chosen_rarity] and available_rarities:
                # Find closest available rarity
                if chosen_rarity == "Legendary" and "Very Rare" in available_rarities:
                    chosen_rarity = "Very Rare"
                elif chosen_rarity == "Very Rare" and "Rare" in available_rarities:
                    chosen_rarity = "Rare"
                elif chosen_rarity == "Rare" and "Uncommon" in available_rarities:
                    chosen_rarity = "Uncommon"
                elif chosen_rarity == "Uncommon" and "Common" in available_rarities:
                    chosen_rarity = "Common"
                else:
                    chosen_rarity = available_rarities[0]

            # Select a random item of the chosen rarity
            if items_by_rarity[chosen_rarity]:
                item_details = random.choice(items_by_rarity[chosen_rarity])

                # Extract better description
                description = _get_magic_item_description(item_details)

                selected_items.append({
                    "name": item_details.get("name", "Unknown Magic Item"),
                    "rarity": chosen_rarity,
                    "description": description,
                    "uri": f"resource://dnd/item/magic-items/{item_details.get('index', '')}"
                })

        return selected_items

    def _get_magic_item_description(item_details: Dict[str, Any]) -> str:
        """Extract a useful description from magic item details."""
        description = ""

        # Try to get the item type
        item_type = ""
        if "equipment_category" in item_details:
            item_type = item_details["equipment_category"].get("name", "")

        # Get the rarity and attunement info
        rarity = item_details.get("rarity", {}).get("name", "")
        requires_attunement = item_details.get("requires_attunement", False)
        attunement_text = ", requires attunement" if requires_attunement else ""

        # Start with basic info
        description = f"{item_type}, {rarity.lower()}{attunement_text}"

        # Add a snippet of the actual description if available
        if "desc" in item_details:
            if isinstance(item_details["desc"], list) and item_details["desc"]:
                first_para = item_details["desc"][0]
                if len(first_para) > 100:
                    description += f": {first_para[:100]}..."
                else:
                    description += f": {first_para}"
            elif isinstance(item_details["desc"], str):
                if len(item_details["desc"]) > 100:
                    description += f": {item_details['desc'][:100]}..."
                else:
                    description += f": {item_details['desc']}"

        return description

    # Helper functions
    def _get_category_items(category: str, cache: APICache) -> Dict[str, Any]:
        """Get all items in a category, using cache if available."""
        cache_key = f"dnd_items_{category}"
        cached_data = cache.get(cache_key)

        if cached_data:
            # Add source attribution if not already present
            if isinstance(cached_data, dict) and "source" not in cached_data:
                cached_data["source"] = "D&D 5e API"
            return cached_data

        try:
            response = requests.get(f"{BASE_URL}/{category}")
            if response.status_code != 200:
                return {
                    "error": f"Category '{category}' not found or API request failed",
                    "status_code": response.status_code,
                    "message": "Please use only valid D&D 5e API categories",
                    "source": "D&D 5e API"
                }

            data = response.json()

            # Transform to resource format
            items = []
            for item in data.get("results", []):
                items.append({
                    "name": item["name"],
                    "index": item["index"],
                    "description": f"Details about {item['name']}",
                    "uri": f"resource://dnd/item/{category}/{item['index']}",
                    "source": "D&D 5e API"
                })

            result = {
                "category": category,
                "items": items,
                "count": len(items),
                "source": "D&D 5e API"
            }

            # Cache the result
            cache.set(cache_key, result)
            return result

        except Exception as e:
            logger.exception(f"Error fetching category {category}: {e}")
            return {
                "error": f"Failed to fetch category items: {str(e)}",
                "message": "API request failed, please try again with valid parameters",
                "source": "D&D 5e API"
            }

    def _get_item_details(category: str, index: str, cache: APICache) -> Dict[str, Any]:
        """Get detailed information about a specific item, using cache if available."""
        cache_key = f"dnd_item_{category}_{index}"
        cached_data = cache.get(cache_key)

        if cached_data:
            # Add source attribution if not already present
            if isinstance(cached_data, dict) and "source" not in cached_data:
                cached_data["source"] = "D&D 5e API"
            return cached_data

        try:
            response = requests.get(f"{BASE_URL}/{category}/{index}")
            if response.status_code != 200:
                return {
                    "error": f"Item '{index}' not found in category '{category}' or API request failed",
                    "status_code": response.status_code,
                    "message": "Please use only valid D&D 5e API endpoints and parameters",
                    "source": "D&D 5e API"
                }

            data = response.json()

            # Add source attribution
            data["source"] = "D&D 5e API"

            # Cache the result
            cache.set(cache_key, data)
            return data

        except Exception as e:
            logger.exception(f"Error fetching item {category}/{index}: {e}")
            return {
                "error": f"Failed to fetch item details: {str(e)}",
                "message": "API request failed, please try again with valid parameters",
                "source": "D&D 5e API"
            }

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
        # Handle string description
        if isinstance(desc, str):
            return desc[:100] + "..." if len(desc) > 100 else desc

        return "No description available"

    def _apply_final_treasure_bonus(coins: Dict[str, int]) -> Dict[str, int]:
        """Apply bonus to coins for final treasure."""
        import random

        # Bonus multiplier between 1.5 and 2.5
        multiplier = 1.5 + (random.random() * 1.0)

        # Apply multiplier to each coin type
        for coin_type in coins:
            coins[coin_type] = int(coins[coin_type] * multiplier)

        return coins

    def _calculate_total_value(coins: Dict[str, int], items: List[Dict[str, Any]],
                               magic_items: List[Dict[str, Any]]) -> float:
        """Calculate the total value of the treasure in gold pieces."""
        total_value = 0.0

        # Add coin values
        coin_values = {
            "cp": 0.01,
            "sp": 0.1,
            "gp": 1.0,
            "pp": 10.0
        }

        for coin_type, amount in coins.items():
            total_value += amount * coin_values.get(coin_type, 0)

        # Add item values
        for item in items:
            total_value += item.get("value_in_gp", 0)

        # Magic items are harder to value, use rarity as a guide
        rarity_values = {
            "Common": 50,
            "Uncommon": 500,
            "Rare": 5000,
            "Very Rare": 50000,
            "Legendary": 200000,
            "Unknown": 100
        }

        for item in magic_items:
            rarity = item.get("rarity", "Unknown")
            total_value += rarity_values.get(rarity, 100)

        return round(total_value, 2)

    print("D&D API tools registered successfully", file=sys.stderr)
