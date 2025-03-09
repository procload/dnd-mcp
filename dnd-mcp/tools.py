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


def register_tools(app):
    """Register tool handlers with the app using the decorator pattern."""
    print("Defining tools with decorators...", file=sys.stderr)

    # Define the query_monster function
    async def query_monster_handler(name: str) -> str:
        """Get information about a D&D monster.

        Args:
            name: The name of the monster (e.g., goblin, dragon)
        """
        print(f"Searching for monster: {name}", file=sys.stderr)
        try:
            monster_name = name.lower()
            if not monster_name:
                return "Please provide a monster name."

            # Special monsters dictionary
            special_monsters = {
                "beholder": "beholder-zombie",  # Beholder is actually "beholder-zombie" in the API
                "dragon": "adult-black-dragon",  # Default dragon if just "dragon" is specified
                "devil": "horned-devil",        # Default devil
                "demon": "balor",               # Default demon
                "giant": "stone-giant",         # Default giant
                "lich": "lich",                 # Lich is actually in the API
                "vampire": "vampire",           # Vampire is in the API
                "zombie": "zombie"              # Zombie is in the API
            }

            # Check if we have a special case
            if monster_name in special_monsters:
                print(
                    f"Special monster case: {monster_name} -> {special_monsters[monster_name]}", file=sys.stderr)
                monster_index = special_monsters[monster_name]
            else:
                monster_index = monster_name.replace(" ", "-")

            # First try direct access by index (for exact matches)
            try:
                # Try direct access first
                direct_url = f"{API_BASE_URL}/monsters/{monster_index}"
                print(f"Trying direct access: {direct_url}", file=sys.stderr)

                with urllib.request.urlopen(direct_url) as response:
                    if response.status == 200:
                        print(
                            f"Direct access successful for {monster_index}", file=sys.stderr)
                        monster_data = json.loads(response.read())
                        formatted_data = format_monster_data(monster_data)
                        return formatted_data
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    print(
                        f"Monster not found by direct index: {monster_index} (404)", file=sys.stderr)
                    # Continue to search
                else:
                    print(f"HTTP error: {e}", file=sys.stderr)
                    return f"Error accessing the D&D API: {str(e)}"
            except Exception as e:
                print(f"Error in direct access: {e}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                # Continue to search

            # If direct access fails, try searching by name
            try:
                # Use the monster list endpoint with name filtering
                search_url = f"{API_BASE_URL}/monsters?name={urllib.parse.quote(monster_name)}"
                print(
                    f"Searching monsters with URL: {search_url}", file=sys.stderr)

                with urllib.request.urlopen(search_url) as response:
                    if response.status == 200:
                        search_results = json.loads(response.read())
                        print(
                            f"Search results count: {search_results.get('count', 0)}", file=sys.stderr)

                        if search_results.get("count", 0) == 0:
                            # Try a more general search by removing hyphens and using partial matching
                            general_name = monster_name.replace(
                                "-", " ").split()[0]  # Get first word
                            if general_name != monster_name:
                                print(
                                    f"Trying more general search with: {general_name}", file=sys.stderr)
                                general_url = f"{API_BASE_URL}/monsters?name={urllib.parse.quote(general_name)}"

                                with urllib.request.urlopen(general_url) as general_response:
                                    if general_response.status == 200:
                                        general_results = json.loads(
                                            general_response.read())
                                        print(
                                            f"General search results count: {general_results.get('count', 0)}", file=sys.stderr)

                                        if general_results.get("count", 0) > 0:
                                            # Found some results with the more general search
                                            monsters_list = "\n".join(
                                                [f"- {m['name']}" for m in general_results.get("results", [])])
                                            return f"Found {general_results.get('count')} monsters related to '{monster_name}':\n\n{monsters_list}\n\nPlease specify a single monster name for detailed information."

                            # Try searching with challenge rating if it's a number
                            if monster_name.replace(".", "").isdigit():
                                cr_search_url = f"{API_BASE_URL}/monsters?challenge_rating={monster_name}"
                                print(
                                    f"Searching by CR: {cr_search_url}", file=sys.stderr)

                                with urllib.request.urlopen(cr_search_url) as cr_response:
                                    if cr_response.status == 200:
                                        cr_results = json.loads(
                                            cr_response.read())
                                        if cr_results.get("count", 0) > 0:
                                            monsters_list = "\n".join(
                                                [f"- {m['name']} (CR {monster_name})" for m in cr_results.get("results", [])])
                                            return f"Found {cr_results.get('count')} monsters with Challenge Rating {monster_name}:\n\n{monsters_list}"

                            # Try a full list search as a last resort
                            print("Trying full monster list search",
                                  file=sys.stderr)
                            full_list_url = f"{API_BASE_URL}/monsters"
                            with urllib.request.urlopen(full_list_url) as full_list_response:
                                if full_list_response.status == 200:
                                    full_list_results = json.loads(
                                        full_list_response.read())
                                    # Search for partial matches in the full list
                                    matches = []
                                    for m in full_list_results.get("results", []):
                                        if monster_name in m.get("name", "").lower():
                                            matches.append(m)

                                    if matches:
                                        print(
                                            f"Found {len(matches)} partial matches in full list", file=sys.stderr)
                                        monsters_list = "\n".join(
                                            [f"- {m['name']}" for m in matches])
                                        return f"Found {len(matches)} monsters related to '{monster_name}':\n\n{monsters_list}\n\nPlease specify a single monster name for detailed information."

                            # Special case for common monsters that might not be in the SRD
                            common_monsters = {
                                "beholder": "The Beholder is an iconic D&D monster but is not included in the SRD API. It's a floating orb-like aberration with a large central eye and multiple eyestalks, each capable of casting different spell-like effects.",
                                "mind flayer": "The Mind Flayer (Illithid) is an iconic D&D monster but is not included in the SRD API. It's a humanoid creature with an octopus-like head that feeds on the brains of sentient creatures.",
                                "tarrasque": "The Tarrasque is an iconic D&D monster but is not included in the SRD API. It's a colossal monstrosity and one of the most powerful monsters in D&D, capable of destroying entire cities.",
                                "displacer beast": "The Displacer Beast is an iconic D&D monster but is not included in the SRD API. It resembles a large panther with six legs and two tentacles sprouting from its shoulders, and has the magical ability to appear to be in a different location than it actually is."
                            }

                            if monster_name in common_monsters:
                                return common_monsters[monster_name]

                            return f"No monsters found matching '{monster_name}'. The D&D 5e SRD API only includes a subset of monsters from the Monster Manual."

                        # If we have results, get the first one's details
                        if search_results.get("count", 0) == 1:
                            monster_url = search_results["results"][0]["url"].lstrip(
                                "/api/")
                            with urllib.request.urlopen(f"{API_BASE_URL}/{monster_url}") as monster_response:
                                if monster_response.status == 200:
                                    monster_data = json.loads(
                                        monster_response.read())
                                    formatted_data = format_monster_data(
                                        monster_data)
                                    return formatted_data
                        else:
                            # Multiple results - list them
                            monsters_list = "\n".join(
                                [f"- {m['name']}" for m in search_results.get("results", [])])
                            return f"Found {search_results.get('count')} monsters matching '{monster_name}':\n\n{monsters_list}\n\nPlease specify a single monster name for detailed information."
            except urllib.error.HTTPError as e:
                print(f"HTTP error in monster search: {e}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                return f"Error searching the D&D API: {str(e)}"
            except Exception as e:
                print(f"Error in monster search: {e}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                return f"Error: {str(e)}"

            return f"Could not find information about '{monster_name}'. The D&D 5e SRD API only includes a subset of monsters from the Monster Manual."
        except Exception as e:
            print(f"Error in query_monster: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return f"Error: {str(e)}"

    # Define the get_spell function
    async def get_spell_handler(name: str) -> str:
        """Get detailed information about a D&D spell.

        Args:
            name: The name of the spell (e.g., fireball, magic missile)
        """
        print(f"Querying spell: {name}", file=sys.stderr)
        try:
            spell_name = name.lower().replace(" ", "-")
            if not spell_name:
                return "Please provide a spell name."

            try:
                with urllib.request.urlopen(f"{API_BASE_URL}/spells/{spell_name}") as response:
                    if response.status == 200:
                        spell_data = json.loads(response.read())
                        formatted_data = format_spell_data(spell_data)
                        return formatted_data
                    else:
                        return f"Spell '{name}' not found."
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    # Try searching by name if direct access fails
                    try:
                        search_url = f"{API_BASE_URL}/spells?name={urllib.parse.quote(name)}"
                        with urllib.request.urlopen(search_url) as search_response:
                            if search_response.status == 200:
                                search_results = json.loads(
                                    search_response.read())
                                if search_results.get("count", 0) > 0:
                                    spell_url = search_results["results"][0]["url"].lstrip(
                                        "/api/")
                                    with urllib.request.urlopen(f"{API_BASE_URL}/{spell_url}") as spell_response:
                                        if spell_response.status == 200:
                                            spell_data = json.loads(
                                                spell_response.read())
                                            formatted_data = format_spell_data(
                                                spell_data)
                                            return formatted_data
                                return f"No spells found matching '{name}'."
                    except Exception as search_e:
                        return f"Error searching for spell: {str(search_e)}"
                return f"Error accessing spell information: {str(e)}"
            except Exception as e:
                return f"Error: {str(e)}"
        except Exception as e:
            print(f"Error in get_spell: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return f"Error: {str(e)}"

    # Define the get_class function
    async def get_class_handler(name: str) -> str:
        """Get information about a D&D character class.

        Args:
            name: The name of the class (e.g., wizard, fighter)
        """
        print(f"Querying class: {name}", file=sys.stderr)
        try:
            class_name = name.lower()
            if not class_name:
                return "Please provide a class name."

            try:
                with urllib.request.urlopen(f"{API_BASE_URL}/classes/{class_name}") as response:
                    if response.status == 200:
                        class_data = json.loads(response.read())
                        formatted_data = format_class_data(class_data)
                        return formatted_data
                    else:
                        return f"Class '{name}' not found."
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return f"Class '{name}' not found."
                return f"Error accessing class information: {str(e)}"
            except Exception as e:
                return f"Error: {str(e)}"
        except Exception as e:
            print(f"Error in get_class: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return f"Error: {str(e)}"

    # Define the search_api function
    async def search_api_handler(endpoint: str, query: str) -> str:
        """Search the D&D API for specific content.

        Args:
            endpoint: The API endpoint to search (e.g., spells, monsters, classes)
            query: The search term
        """
        print(
            f"Searching API: endpoint={endpoint}, query={query}", file=sys.stderr)
        try:
            if not endpoint or not query:
                return "Please provide both an endpoint and a query."

            valid_endpoints = ["monsters", "spells", "classes",
                               "races", "equipment", "magic-items", "features"]
            if endpoint not in valid_endpoints:
                return f"Error: Invalid endpoint. Valid options are: {', '.join(valid_endpoints)}"

            try:
                search_url = f"{API_BASE_URL}/{endpoint}?name={urllib.parse.quote(query)}"
                print(f"Searching API with URL: {search_url}", file=sys.stderr)

                with urllib.request.urlopen(search_url) as response:
                    if response.status == 200:
                        results = json.loads(response.read())
                        if results.get("count", 0) == 0:
                            return f"No results found for '{query}' in {endpoint}."

                        results_text = f"Found {results['count']} results for '{query}' in '{endpoint}':\n\n"
                        for result in results.get("results", []):
                            results_text += f"- {result.get('name')}\n"

                        return results_text
            except urllib.error.HTTPError as e:
                return f"Error searching the D&D API: {str(e)}"
            except Exception as e:
                return f"Error: {str(e)}"
        except Exception as e:
            print(f"Error in search_api: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return f"Error: {str(e)}"

    # Register the tools with FastMCP using the correct pattern
    app.tool()(query_monster_handler)
    app.tool()(get_spell_handler)
    app.tool()(get_class_handler)
    app.tool()(search_api_handler)

    print("Tools registered successfully", file=sys.stderr)
