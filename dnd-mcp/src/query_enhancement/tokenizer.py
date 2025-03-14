"""
Tokenizer module for D&D Knowledge Navigator.

This module provides functions to tokenize D&D queries and handle special terms.
"""

import re
from typing import List, Tuple, Set

# Special D&D terms that should be preserved as single tokens
SPECIAL_DND_TERMS = {
    # Game mechanics
    "AC": "armor class",
    "HP": "hit points",
    "DC": "difficulty class",
    "XP": "experience points",
    "CR": "challenge rating",
    "AoE": "area of effect",
    "THP": "temporary hit points",

    # Ability scores
    "STR": "strength",
    "DEX": "dexterity",
    "CON": "constitution",
    "INT": "intelligence",
    "WIS": "wisdom",
    "CHA": "charisma",

    # Dice notation
    "d4": "four-sided die",
    "d6": "six-sided die",
    "d8": "eight-sided die",
    "d10": "ten-sided die",
    "d12": "twelve-sided die",
    "d20": "twenty-sided die",
    "d100": "hundred-sided die",

    # Common abbreviations
    "PHB": "Player's Handbook",
    "DMG": "Dungeon Master's Guide",
    "MM": "Monster Manual",
    "XGE": "Xanathar's Guide to Everything",
    "TCE": "Tasha's Cauldron of Everything",
    "SCAG": "Sword Coast Adventurer's Guide",
    "VGM": "Volo's Guide to Monsters",
    "MTF": "Mordenkainen's Tome of Foes",

    # Class features
    "ASI": "ability score improvement",
    "DPR": "damage per round",
    "AoO": "attack of opportunity",

    # Spellcasting
    "AOE": "area of effect",
    "DOT": "damage over time",
    "CC": "crowd control",

    # Combat
    "OA": "opportunity attack",
    "AoO": "attack of opportunity",
    "DPR": "damage per round",

    # Character creation
    "PC": "player character",
    "NPC": "non-player character",
    "DMPC": "dungeon master player character",
}

# Regex patterns for special D&D formats
# Matches dice notation like 2d6+3
DICE_PATTERN = r'\b(\d+)?d(\d+)(\s*[\+\-]\s*\d+)?\b'
# Matches ability checks
ABILITY_CHECK_PATTERN = r'\b(STR|DEX|CON|INT|WIS|CHA)\s+check\b'
# Matches saving throws
SAVING_THROW_PATTERN = r'\b(STR|DEX|CON|INT|WIS|CHA)\s+save\b'
SKILL_CHECK_PATTERN = r'\b(Athletics|Acrobatics|Sleight of Hand|Stealth|Arcana|History|Investigation|Nature|Religion|Animal Handling|Insight|Medicine|Perception|Survival|Deception|Intimidation|Performance|Persuasion)\s+check\b'  # Matches skill checks


def tokenize_dnd_query(query: str) -> Tuple[List[str], List[str]]:
    """
    Tokenize a D&D query, preserving special terms.

    Args:
        query: The query to tokenize

    Returns:
        Tuple of (list of tokens, list of special terms found)
    """
    # Convert to lowercase for easier matching
    original_query = query
    query = query.lower()

    # Find special terms in the query
    special_terms_found = []

    # Check for special D&D terms
    for term, meaning in SPECIAL_DND_TERMS.items():
        pattern = r'\b' + re.escape(term) + r'\b'
        if re.search(pattern, original_query, re.IGNORECASE):
            special_terms_found.append((term, meaning))

    # Check for dice notation
    dice_matches = re.finditer(DICE_PATTERN, query)
    for match in dice_matches:
        special_terms_found.append((match.group(0), "dice notation"))

    # Check for ability checks
    ability_check_matches = re.finditer(
        ABILITY_CHECK_PATTERN, query, re.IGNORECASE)
    for match in ability_check_matches:
        special_terms_found.append((match.group(0), "ability check"))

    # Check for saving throws
    save_matches = re.finditer(SAVING_THROW_PATTERN, query, re.IGNORECASE)
    for match in save_matches:
        special_terms_found.append((match.group(0), "saving throw"))

    # Check for skill checks
    skill_matches = re.finditer(SKILL_CHECK_PATTERN, query, re.IGNORECASE)
    for match in skill_matches:
        special_terms_found.append((match.group(0), "skill check"))

    # Tokenize the query
    # First, replace special patterns with placeholders to preserve them
    placeholder_map = {}
    modified_query = query

    # Replace dice notation
    modified_query = re.sub(
        DICE_PATTERN, lambda m: f"__DICE_{len(placeholder_map)}__", modified_query)
    placeholder_map[f"__DICE_{len(placeholder_map)}__"] = re.search(
        DICE_PATTERN, query).group(0) if re.search(DICE_PATTERN, query) else ""

    # Replace ability checks
    modified_query = re.sub(
        ABILITY_CHECK_PATTERN, lambda m: f"__ABILITY_CHECK_{len(placeholder_map)}__", modified_query, flags=re.IGNORECASE)
    placeholder_map[f"__ABILITY_CHECK_{len(placeholder_map)}__"] = re.search(
        ABILITY_CHECK_PATTERN, query, re.IGNORECASE).group(0) if re.search(ABILITY_CHECK_PATTERN, query, re.IGNORECASE) else ""

    # Replace saving throws
    modified_query = re.sub(
        SAVING_THROW_PATTERN, lambda m: f"__SAVE_{len(placeholder_map)}__", modified_query, flags=re.IGNORECASE)
    placeholder_map[f"__SAVE_{len(placeholder_map)}__"] = re.search(SAVING_THROW_PATTERN, query, re.IGNORECASE).group(
        0) if re.search(SAVING_THROW_PATTERN, query, re.IGNORECASE) else ""

    # Replace skill checks
    modified_query = re.sub(
        SKILL_CHECK_PATTERN, lambda m: f"__SKILL_{len(placeholder_map)}__", modified_query, flags=re.IGNORECASE)
    placeholder_map[f"__SKILL_{len(placeholder_map)}__"] = re.search(SKILL_CHECK_PATTERN, query, re.IGNORECASE).group(
        0) if re.search(SKILL_CHECK_PATTERN, query, re.IGNORECASE) else ""

    # Split into tokens
    tokens = []
    for word in modified_query.split():
        # Check if it's a placeholder
        if word in placeholder_map:
            tokens.append(placeholder_map[word])
        else:
            # Clean up punctuation
            clean_word = word.strip('.,?!;:()"\'')
            if clean_word:
                tokens.append(clean_word)

    return tokens, [term for term, _ in special_terms_found]


def is_dnd_special_term(term: str) -> bool:
    """
    Check if a term is a special D&D term.

    Args:
        term: The term to check

    Returns:
        True if the term is a special D&D term, False otherwise
    """
    term = term.upper()

    # Check if it's in our special terms dictionary
    if term in SPECIAL_DND_TERMS:
        return True

    # Check if it matches dice notation
    if re.match(DICE_PATTERN, term):
        return True

    # Check if it's an ability score abbreviation
    if term in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
        return True

    return False
