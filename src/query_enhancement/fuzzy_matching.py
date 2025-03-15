"""
Fuzzy matching module for D&D Knowledge Navigator.

This module provides functions to perform fuzzy matching on D&D terms.
"""

import re
from typing import List, Dict, Tuple, Set
from difflib import get_close_matches

# Common D&D terms that are frequently misspelled
DND_COMMON_TERMS = [
    # Classes
    "barbarian", "bard", "cleric", "druid", "fighter", "monk", "paladin",
    "ranger", "rogue", "sorcerer", "warlock", "wizard", "artificer",

    # Races
    "dragonborn", "dwarf", "elf", "gnome", "half-elf", "half-orc", "halfling",
    "human", "tiefling", "aasimar", "genasi", "goliath", "tabaxi", "firbolg",

    # Monsters
    "aboleth", "beholder", "chimera", "displacer beast", "dragon", "gelatinous cube",
    "goblin", "hobgoblin", "kobold", "lich", "mimic", "mind flayer", "owlbear",
    "tarrasque", "troll", "vampire", "werewolf", "wyvern", "zombie",

    # Spells
    "fireball", "magic missile", "wish", "counterspell", "feather fall",
    "identify", "mage hand", "prestidigitation", "eldritch blast", "cure wounds",
    "healing word", "revivify", "resurrection", "teleport", "polymorph",

    # Items
    "longsword", "shortsword", "greatsword", "dagger", "battleaxe", "warhammer",
    "longbow", "shortbow", "crossbow", "shield", "armor", "potion", "scroll",
    "wand", "staff", "ring", "amulet", "cloak", "boots", "gloves",

    # Game terms
    "initiative", "attack", "damage", "saving throw", "ability check", "skill check",
    "advantage", "disadvantage", "inspiration", "exhaustion", "concentration",
    "spell slot", "cantrip", "ritual", "bonus action", "reaction",

    # Books
    "player's handbook", "dungeon master's guide", "monster manual",
    "xanathar's guide to everything", "tasha's cauldron of everything",
    "sword coast adventurer's guide", "volo's guide to monsters",
    "mordenkainen's tome of foes",

    # Common misspellings
    "armor class", "hit points", "constitution", "dexterity", "strength",
    "intelligence", "wisdom", "charisma", "proficiency", "experience",
]

# Common misspellings of D&D terms
COMMON_MISSPELLINGS = {
    # Classes
    "barberian": "barbarian",
    "rouge": "rogue",
    "sorcerror": "sorcerer",
    "sourcerer": "sorcerer",
    "wizzard": "wizard",
    "artifacer": "artificer",
    "palidin": "paladin",
    "worlock": "warlock",

    # Races
    "dragornborn": "dragonborn",
    "dwarve": "dwarf",
    "halforc": "half-orc",
    "halfelf": "half-elf",
    "teifling": "tiefling",
    "trifling": "tiefling",
    "asimar": "aasimar",
    "genasai": "genasi",

    # Monsters
    "beholder": "beholder",
    "mindflayer": "mind flayer",
    "gelatanous cube": "gelatinous cube",
    "tarasque": "tarrasque",
    "terrasque": "tarrasque",
    "vampyre": "vampire",
    "werewolf": "werewolf",
    "zombie": "zombie",

    # Spells
    "fireball": "fireball",
    "magicmissile": "magic missile",
    "counter spell": "counterspell",
    "featherfall": "feather fall",
    "magehand": "mage hand",
    "prestidigitation": "prestidigitation",
    "prestidigation": "prestidigitation",
    "eldrich blast": "eldritch blast",
    "curewounds": "cure wounds",
    "healingword": "healing word",
    "revivify": "revivify",
    "ressurection": "resurrection",
    "ressurect": "resurrect",
    "teleport": "teleport",
    "polymorph": "polymorph",

    # Items
    "long sword": "longsword",
    "short sword": "shortsword",
    "great sword": "greatsword",
    "battle axe": "battleaxe",
    "war hammer": "warhammer",
    "long bow": "longbow",
    "short bow": "shortbow",
    "cross bow": "crossbow",

    # Game terms
    "initative": "initiative",
    "inititive": "initiative",
    "saving trow": "saving throw",
    "ability check": "ability check",
    "skill check": "skill check",
    "advantige": "advantage",
    "disadvantige": "disadvantage",
    "insperation": "inspiration",
    "exaustion": "exhaustion",
    "concentraition": "concentration",
    "spell slot": "spell slot",
    "cantrip": "cantrip",
    "rituel": "ritual",
    "bonus action": "bonus action",
    "reaction": "reaction",

    # Books
    "players handbook": "player's handbook",
    "dungeon masters guide": "dungeon master's guide",
    "monster manual": "monster manual",
    "xanathars guide": "xanathar's guide to everything",
    "tashas cauldron": "tasha's cauldron of everything",
    "sword coast guide": "sword coast adventurer's guide",
    "volos guide": "volo's guide to monsters",
    "mordenkainens tome": "mordenkainen's tome of foes",

    # Common misspellings
    "armour class": "armor class",
    "armor clas": "armor class",
    "hit point": "hit points",
    "constituion": "constitution",
    "dexterity": "dexterity",
    "strenght": "strength",
    "inteligence": "intelligence",
    "wisdon": "wisdom",
    "charisma": "charisma",
    "proficency": "proficiency",
    "experiance": "experience",
}


def fuzzy_match(tokens: List[str]) -> List[Tuple[str, str]]:
    """
    Perform fuzzy matching on tokens to find potential corrections.

    Args:
        tokens: List of tokens to match

    Returns:
        List of (original token, suggested correction) pairs
    """
    corrections = []

    for token in tokens:
        # Skip short tokens
        if len(token) < 3:
            continue

        # Check for exact matches in common misspellings
        if token.lower() in COMMON_MISSPELLINGS:
            corrections.append((token, COMMON_MISSPELLINGS[token.lower()]))
            continue

        # Try fuzzy matching against common D&D terms
        matches = get_close_matches(
            token.lower(), DND_COMMON_TERMS, n=1, cutoff=0.8)
        if matches:
            # Only suggest a correction if it's different from the original
            if matches[0] != token.lower():
                corrections.append((token, matches[0]))

    return corrections


def correct_misspellings(query: str) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Correct common misspellings in a D&D query.

    Args:
        query: The query to correct

    Returns:
        Tuple of (corrected query, list of (original, correction) pairs)
    """
    words = query.split()
    corrections = []
    corrected_words = []

    for word in words:
        # Clean the word
        clean_word = word.lower().strip('.,?!;:()"\'')

        # Skip short words
        if len(clean_word) < 3:
            corrected_words.append(word)
            continue

        # Check for exact matches in common misspellings
        if clean_word in COMMON_MISSPELLINGS:
            correction = COMMON_MISSPELLINGS[clean_word]
            corrections.append((clean_word, correction))

            # Replace the word with its correction, preserving case and punctuation
            prefix = ""
            suffix = ""

            # Extract any leading punctuation
            match = re.match(r'^([^\w]*)(.*)$', word)
            if match:
                prefix = match.group(1)
                word = match.group(2)

            # Extract any trailing punctuation
            match = re.match(r'^(.*?)([^\w]*)$', word)
            if match:
                word = match.group(1)
                suffix = match.group(2)

            # Apply the correction, preserving case
            if word.isupper():
                corrected_word = correction.upper()
            elif word[0].isupper():
                corrected_word = correction[0].upper() + correction[1:]
            else:
                corrected_word = correction

            corrected_words.append(prefix + corrected_word + suffix)
        else:
            corrected_words.append(word)

    corrected_query = " ".join(corrected_words)
    return corrected_query, corrections
