#!/usr/bin/env python3
import sys
import requests
import json
import logging
from typing import List, Dict, Any, Optional
from cache import APICache
from datetime import datetime

logger = logging.getLogger(__name__)

# Base URL for the D&D 5e API
BASE_URL = "https://www.dnd5eapi.co/api"

# Request timeout in seconds
REQUEST_TIMEOUT = 10

# Category descriptions for better resource discovery
CATEGORY_DESCRIPTIONS = {
    "ability-scores": "The six abilities that describe a character's physical and mental characteristics",
    "alignments": "The moral and ethical attitudes and behaviors of creatures",
    "backgrounds": "Character backgrounds and their features",
    "classes": "Character classes with features, proficiencies, and subclasses",
    "conditions": "Status conditions that affect creatures",
    "damage-types": "Types of damage that can be dealt",
    "equipment": "Items, weapons, armor, and gear for adventuring",
    "equipment-categories": "Categories of equipment",
    "feats": "Special abilities and features",
    "features": "Class and racial features",
    "languages": "Languages spoken throughout the multiverse",
    "magic-items": "Magical equipment with special properties",
    "magic-schools": "Schools of magic specialization",
    "monsters": "Creatures and foes",
    "proficiencies": "Skills and tools characters can be proficient with",
    "races": "Character races and their traits",
    "rule-sections": "Sections of the game rules",
    "rules": "Game rules",
    "skills": "Character skills tied to ability scores",
    "spells": "Magic spells with effects, components, and descriptions",
    "subclasses": "Specializations within character classes",
    "subraces": "Variants of character races",
    "traits": "Racial traits",
    "weapon-properties": "Special properties of weapons"
}


def register_resources(app, cache: APICache):
    """Register D&D API resources with the FastMCP app.

    Args:
        app: The FastMCP app instance
        cache: The shared API cache
    """
    print("Registering D&D API resources...", file=sys.stderr)

    def prefetch_category_items(category: str) -> None:
        """Prefetch and cache all items in a category.

        Args:
            category: The D&D API category to prefetch
        """
        logger.info(f"Prefetching items for category: {category}")

        # First get the list of items
        cache_key = f"dnd_items_{category}"
        category_data = cache.get(cache_key)

        if not category_data:
            try:
                logger.debug(f"Fetching item list for category: {category}")
                response = requests.get(
                    f"{BASE_URL}/{category}", timeout=REQUEST_TIMEOUT)
                if response.status_code != 200:
                    logger.error(
                        f"Failed to fetch items for {category}: {response.status_code}")
                    return

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

                category_data = {
                    "category": category,
                    "items": items,
                    "count": len(items)
                }

                # Cache the result
                cache.set(cache_key, category_data)

            except Exception as e:
                logger.exception(
                    f"Error prefetching items for {category}: {e}")
                return

        # Now prefetch each individual item
        for item in category_data["items"]:
            item_cache_key = f"dnd_item_{category}_{item['index']}"
            if not cache.get(item_cache_key):
                try:
                    logger.debug(
                        f"Prefetching item details: {category}/{item['index']}")
                    response = requests.get(
                        f"{BASE_URL}/{category}/{item['index']}", timeout=REQUEST_TIMEOUT)
                    if response.status_code == 200:
                        data = response.json()
                        cache.set(item_cache_key, data)
                except Exception as e:
                    logger.exception(
                        f"Error prefetching item {category}/{item['index']}: {e}")

    # Start prefetching common categories in the background
    import threading
    for category in ["spells", "equipment", "monsters", "classes", "races"]:
        threading.Thread(target=prefetch_category_items,
                         args=(category,), daemon=True).start()

    @app.resource("resource://dnd/categories")
    def get_categories() -> Dict[str, Any]:
        """List all available D&D 5e API categories for browsing the official content.

        This resource provides a comprehensive list of all categories available in the D&D 5e API,
        such as spells, monsters, equipment, classes, races, and more. Each category entry includes
        a name, description, and endpoint URL.

        This is typically the first resource to access when exploring the D&D 5e API, as it provides
        an overview of all available content categories and their endpoints.

        The data is cached to improve performance on subsequent requests.

        Returns:
            A dictionary containing all available D&D 5e API categories with descriptions
            and endpoints, with source attribution to the D&D 5e API.
        """
        logger.debug("Fetching D&D API categories")

        # Check cache first
        cached_data = cache.get("dnd_categories")
        if cached_data:
            return cached_data

        # Fetch from API if not in cache
        try:
            response = requests.get(f"{BASE_URL}/", timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                logger.error(
                    f"Failed to fetch categories: {response.status_code}")
                return {"error": f"API request failed with status {response.status_code}"}

            data = response.json()

            # Transform to resource format with descriptions
            categories = []
            for key in data.keys():
                description = CATEGORY_DESCRIPTIONS.get(
                    key, f"Collection of D&D 5e {key}")
                categories.append({
                    "name": key,
                    "description": description,
                    "uri": f"resource://dnd/items/{key}"
                })

            result = {
                "categories": categories,
                "count": len(categories)
            }

            # Cache the result
            cache.set("dnd_categories", result)
            return result

        except Exception as e:
            logger.exception(f"Error fetching categories: {e}")
            return {"error": f"Failed to fetch categories: {str(e)}"}

    @app.resource("resource://dnd/items/{category}")
    def get_items(category: str) -> Dict[str, Any]:
        """Retrieve a list of all items available in a specific D&D 5e API category.

        This resource provides access to all items within a specified category, such as all spells,
        all monsters, all equipment, etc. The response includes basic information about each item
        (name and index) that can be used to retrieve detailed information via the item details resource.

        Common categories include:
        - spells: All spells in the D&D 5e ruleset
        - monsters: All monsters and creatures
        - equipment: All standard equipment items
        - magic-items: All magical items and artifacts
        - classes: All character classes
        - races: All playable races

        The data is cached to improve performance on subsequent requests.

        Args:
            category: The D&D API category to retrieve items from (e.g., 'spells', 'monsters', 'equipment')

        Returns:
            A dictionary containing all items in the specified category with basic information,
            with source attribution to the D&D 5e API.
        """
        logger.debug(f"Fetching items for category: {category}")

        # Check cache first
        cache_key = f"dnd_items_{category}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        # Fetch from API if not in cache
        try:
            response = requests.get(
                f"{BASE_URL}/{category}", timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                logger.error(
                    f"Failed to fetch items for {category}: {response.status_code}")
                return {"error": f"Category '{category}' not found or API request failed"}

            data = response.json()

            # Transform to resource format
            items = []
            for item in data.get("results", []):
                item_uri = f"resource://dnd/item/{category}/{item['index']}"
                items.append({
                    "name": item["name"],
                    "index": item["index"],
                    "uri": item_uri,
                })

            result = {
                "category": category,
                "count": len(items),
                "items": items,
                "source": "D&D 5e API (www.dnd5eapi.co)",
            }

            # Cache the result
            cache.set(cache_key, result)
            return result

        except Exception as e:
            logger.exception(f"Error fetching items for {category}: {e}")
            return {"error": f"Failed to fetch items for {category}: {str(e)}"}

    @app.resource("resource://dnd/item/{category}/{index}")
    def get_item(category: str, index: str) -> Dict[str, Any]:
        """Retrieve detailed information about a specific D&D 5e item by its category and index.

        This resource provides comprehensive details about a specific D&D item, including all of its
        properties, descriptions, mechanics, and related information. The response structure varies
        based on the category, as different types of items have different properties:

        - Spells: Includes level, casting time, range, components, duration, description, etc.
        - Monsters: Includes challenge rating, hit points, armor class, abilities, actions, etc.
        - Equipment: Includes cost, weight, properties, damage (for weapons), etc.
        - Classes: Includes proficiencies, spellcasting abilities, class features, etc.
        - Races: Includes ability bonuses, traits, languages, etc.

        The data is cached to improve performance on subsequent requests.

        Args:
            category: The D&D API category the item belongs to (e.g., 'spells', 'monsters', 'equipment')
            index: The unique identifier for the specific item (e.g., 'fireball', 'adult-red-dragon')

        Returns:
            A dictionary containing detailed information about the requested item,
            with source attribution to the D&D 5e API.
        """
        logger.debug(f"Fetching item details: {category}/{index}")

        # Check cache first
        cache_key = f"dnd_item_{category}_{index}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        # Fetch from API if not in cache
        try:
            response = requests.get(
                f"{BASE_URL}/{category}/{index}", timeout=REQUEST_TIMEOUT)

            # Handle redirects (common in the D&D API)
            if response.status_code == 301 and 'Location' in response.headers:
                redirect_url = response.headers['Location']
                logger.debug(f"Following redirect to: {redirect_url}")
                response = requests.get(redirect_url, timeout=REQUEST_TIMEOUT)

            if response.status_code != 200:
                logger.error(
                    f"Failed to fetch item {category}/{index}: {response.status_code}")
                return {"error": f"Item '{index}' not found in category '{category}' or API request failed"}

            # Add source attribution to the API response
            data = response.json()
            data["source"] = "D&D 5e API (www.dnd5eapi.co)"

            # Cache the result
            cache.set(cache_key, data)
            return data

        except Exception as e:
            logger.exception(f"Error fetching item {category}/{index}: {e}")
            return {"error": f"Failed to fetch item {category}/{index}: {str(e)}"}

    @app.resource("resource://dnd/search/{category}/{query}")
    def search_category(category: str, query: str) -> Dict[str, Any]:
        """Search for D&D 5e items within a specific category that match the provided query.

        This resource allows for targeted searching within a specific category of D&D content,
        such as finding spells that match a name pattern, monsters with specific terms in their
        name, or equipment items with particular keywords.

        The search is performed on item names and indexes, with partial matching supported.
        Results are returned in order of relevance, with exact matches prioritized.

        For broader searches across all categories, use the search_all_categories tool instead.

        Examples:
        - search/spells/fire - finds all spells with "fire" in their name
        - search/monsters/dragon - finds all monsters with "dragon" in their name
        - search/equipment/sword - finds all equipment items with "sword" in their name

        Args:
            category: The D&D API category to search within (e.g., 'spells', 'monsters', 'equipment')
            query: The search term to look for in item names (minimum 2 characters)

        Returns:
            A dictionary containing items from the specified category that match the search query,
            with source attribution to the D&D 5e API.
        """
        logger.debug(f"Searching in {category} for: {query}")

        # Get all items in the category
        all_items = get_items(category)

        # Handle error cases
        if "error" in all_items:
            return all_items

        # Filter items by search term
        matching_items = []
        for item in all_items.get("items", []):
            if query.lower() in item["name"].lower():
                matching_items.append(item)

        result = {
            "category": category,
            "query": query,
            "count": len(matching_items),
            "items": matching_items,
            "source": "D&D 5e API (www.dnd5eapi.co)",
        }

        return result

    @app.resource("resource://dnd/api_status")
    def check_api_status() -> Dict[str, Any]:
        """Check the current status and health of the D&D 5e API connection.

        This resource provides diagnostic information about the D&D 5e API, including:
        - Whether the API is currently available and responding
        - The response time of the API
        - The HTTP status code returned by the API
        - A list of available endpoints/categories
        - Any error messages if the API is not functioning correctly

        This is useful for troubleshooting when other D&D resources or tools are not working
        as expected, or when you want to verify the API's availability before making requests.

        No parameters are required for this resource.

        Returns:
            A dictionary containing comprehensive API status information, including availability,
            response time, available endpoints, and any error messages if applicable.
        """
        logger.debug("Checking D&D 5e API status")

        try:
            start_time = datetime.now()
            response = requests.get(BASE_URL, timeout=REQUEST_TIMEOUT)
            response_time = (datetime.now() - start_time).total_seconds()

            if response.status_code == 200:
                data = response.json()
                available_endpoints = list(data.keys())

                return {
                    "status": "online",
                    "response_time_seconds": response_time,
                    "available_endpoints": available_endpoints,
                    "base_url": BASE_URL,
                    "source": "D&D 5e API Status Check"
                }
            else:
                return {
                    "status": "error",
                    "response_code": response.status_code,
                    "response_time_seconds": response_time,
                    "message": f"API returned non-200 status code: {response.status_code}",
                    "source": "D&D 5e API Status Check"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to connect to D&D 5e API: {str(e)}",
                "source": "D&D 5e API Status Check"
            }

    print("D&D API resources registered successfully", file=sys.stderr)
