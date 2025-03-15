"""
Synonyms module for D&D Knowledge Navigator.

This module provides functions to expand queries with D&D-specific synonyms.
"""

import re
from typing import Dict, List, Tuple, Set

# Dictionary of D&D-specific synonyms
# Format: term -> list of synonyms
DND_SYNONYMS = {
    # Stats and abilities
    "strength": ["str", "might", "power", "muscle"],
    "dexterity": ["dex", "agility", "reflexes", "coordination"],
    "constitution": ["con", "endurance", "stamina", "toughness", "fortitude"],
    "intelligence": ["int", "intellect", "smarts", "brains"],
    "wisdom": ["wis", "perception", "insight", "awareness"],
    "charisma": ["cha", "personality", "presence", "persuasion"],

    # Common game terms
    "armor class": ["ac", "defense", "armor", "defence"],
    "hit points": ["hp", "health", "life", "vitality"],
    "temporary hit points": ["temp hp", "temporary health"],
    "attack roll": ["to hit", "attack", "hit roll"],
    "saving throw": ["save", "saving", "resist"],
    "difficulty class": ["dc", "difficulty", "target number"],

    # Character creation
    "class": ["character class", "job", "profession", "role"],
    "race": ["ancestry", "heritage", "species", "lineage"],
    "background": ["origin", "history", "backstory"],
    "level": ["character level", "lvl"],
    "ability score": ["stat", "attribute", "characteristic"],
    "proficiency": ["prof", "training", "skill bonus"],

    # Combat
    "initiative": ["init", "combat order", "turn order"],
    "attack": ["strike", "hit", "assault"],
    "damage": ["dmg", "harm", "injury", "hurt"],
    "critical hit": ["crit", "critical", "nat 20"],
    "bonus action": ["bonus", "swift action"],
    "reaction": ["react", "immediate action"],

    # Magic
    "spell": ["magic", "incantation", "arcane"],
    "cantrip": ["level 0 spell", "minor spell", "at-will spell"],
    "spell slot": ["spell level", "spell capacity"],
    "concentration": ["focus", "maintain spell"],
    "ritual": ["ceremony", "extended casting"],

    # Items
    "magic item": ["magical item", "enchanted item", "magic gear"],
    "weapon": ["arms", "armament", "implement of war"],
    "armor": ["protection", "defense", "shield"],
    "potion": ["elixir", "brew", "concoction"],
    "scroll": ["spell scroll", "magical writing"],

    # Creatures
    "monster": ["creature", "beast", "enemy", "foe"],
    "undead": ["zombie", "skeleton", "ghoul", "ghost", "specter"],
    "fiend": ["demon", "devil", "hellspawn"],
    "dragon": ["drake", "wyrm", "serpent"],

    # Game mechanics
    "advantage": ["adv", "favorable", "upper hand"],
    "disadvantage": ["disadv", "unfavorable", "hindered"],
    "short rest": ["short break", "brief respite"],
    "long rest": ["extended rest", "overnight rest", "full rest"],
    "experience points": ["xp", "exp", "experience"],

    # Conditions
    "condition": ["status effect", "status", "affliction"],
    "exhaustion": ["fatigue", "tiredness", "weariness"],
    "prone": ["knocked down", "lying down", "flat"],
    "stunned": ["dazed", "incapacitated", "unable to act"],
    "unconscious": ["knocked out", "ko", "passed out"],
}

# Create a reverse mapping for lookup
REVERSE_SYNONYMS = {}
for term, synonyms in DND_SYNONYMS.items():
    for synonym in synonyms:
        if synonym not in REVERSE_SYNONYMS:
            REVERSE_SYNONYMS[synonym] = []
        REVERSE_SYNONYMS[synonym].append(term)

# Add the original terms to the reverse mapping
for term in DND_SYNONYMS:
    if term not in REVERSE_SYNONYMS:
        REVERSE_SYNONYMS[term] = []
    REVERSE_SYNONYMS[term].append(term)


def expand_query_with_synonyms(query: str) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Expand a query with D&D-specific synonyms.

    Args:
        query: The original search query

    Returns:
        Tuple of (expanded query, list of (original term, expanded term) pairs)
    """
    original_query = query.lower()
    expanded_terms = []

    # Check for exact matches of multi-word terms first
    for term, synonyms in DND_SYNONYMS.items():
        if " " in term and term.lower() in original_query:
            # Don't expand if the term is already in the query
            continue

        # Check if any of the synonyms are in the query
        for synonym in synonyms:
            if synonym.lower() in original_query:
                # Replace the synonym with the canonical term
                pattern = r'\b' + re.escape(synonym.lower()) + r'\b'
                if re.search(pattern, original_query):
                    expanded_terms.append((synonym, term))
                    break

    # Now check for single word terms
    words = original_query.split()
    for word in words:
        word = word.lower().strip('.,?!;:()"\'')
        if word in REVERSE_SYNONYMS:
            for canonical in REVERSE_SYNONYMS[word]:
                if canonical != word and canonical not in original_query:
                    expanded_terms.append((word, canonical))

    # Build the expanded query
    expanded_query = original_query
    for original, expanded in expanded_terms:
        # Only add terms that aren't already in the query
        if expanded.lower() not in expanded_query.lower():
            expanded_query += f" {expanded}"

    return expanded_query, expanded_terms


def get_all_synonyms(term: str) -> Set[str]:
    """
    Get all synonyms for a given term.

    Args:
        term: The term to get synonyms for

    Returns:
        Set of all synonyms for the term
    """
    term = term.lower()
    synonyms = set()

    # Check if the term is a canonical term
    if term in DND_SYNONYMS:
        synonyms.update(DND_SYNONYMS[term])
        synonyms.add(term)

    # Check if the term is a synonym
    if term in REVERSE_SYNONYMS:
        for canonical in REVERSE_SYNONYMS[term]:
            synonyms.add(canonical)
            if canonical in DND_SYNONYMS:
                synonyms.update(DND_SYNONYMS[canonical])

    return synonyms
