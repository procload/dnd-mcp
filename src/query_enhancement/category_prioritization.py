"""
Category prioritization module for D&D Knowledge Navigator.

This module provides functions to determine which D&D categories
are most relevant to a query.
"""

import re
from typing import Dict, List, Set

# Category keywords mapping
# Format: category -> list of keywords that suggest this category
CATEGORY_KEYWORDS = {
    "spells": [
        "spell", "cast", "casting", "magic", "wizard", "sorcerer", "warlock",
        "bard", "cleric", "druid", "paladin", "ranger", "ritual", "cantrip",
        "concentration", "components", "verbal", "somatic", "material",
        "duration", "range", "target", "saving throw", "damage", "heal",
        "healing", "level", "school", "abjuration", "conjuration", "divination",
        "enchantment", "evocation", "illusion", "necromancy", "transmutation"
    ],

    "monsters": [
        "monster", "creature", "beast", "fiend", "dragon", "undead", "aberration",
        "celestial", "construct", "elemental", "fey", "giant", "humanoid",
        "monstrosity", "ooze", "plant", "challenge rating", "cr", "hit points",
        "hp", "armor class", "ac", "attack", "legendary", "lair", "regional",
        "abilities", "actions", "multiattack", "resistances", "immunities",
        "vulnerabilities", "senses", "languages", "environment", "behavior"
    ],

    "classes": [
        "class", "barbarian", "bard", "cleric", "druid", "fighter", "monk",
        "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard", "artificer",
        "subclass", "archetype", "feature", "ability", "level up", "multiclass",
        "proficiency", "saving throw", "skill", "hit dice", "spellcasting",
        "cantrips known", "spells known", "spell slots", "class feature",
        "starting equipment", "primary ability"
    ],

    "races": [
        "race", "ancestry", "species", "dragonborn", "dwarf", "elf", "gnome",
        "half-elf", "half-orc", "halfling", "human", "tiefling", "aasimar",
        "genasi", "goliath", "tabaxi", "firbolg", "subrace", "variant",
        "ability score increase", "age", "alignment", "size", "speed",
        "darkvision", "traits", "languages", "racial feature"
    ],

    "equipment": [
        "equipment", "item", "weapon", "armor", "shield", "gear", "tool",
        "pack", "kit", "longsword", "shortsword", "greatsword", "dagger",
        "battleaxe", "warhammer", "longbow", "shortbow", "crossbow",
        "leather armor", "chain mail", "plate armor", "light armor",
        "medium armor", "heavy armor", "cost", "weight", "damage",
        "properties", "finesse", "versatile", "two-handed", "reach",
        "ammunition", "loading", "thrown", "special"
    ],

    "magic-items": [
        "magic item", "magical item", "enchanted", "artifact", "wondrous item",
        "potion", "ring", "rod", "scroll", "staff", "wand", "weapon", "armor",
        "shield", "rarity", "common", "uncommon", "rare", "very rare", "legendary",
        "attunement", "charges", "cursed", "sentient", "property", "effect",
        "bonus", "resistance", "immunity", "vulnerability"
    ],

    "rules": [
        "rule", "rulebook", "phb", "dmg", "mm", "xge", "tce", "scag", "vgm",
        "mtf", "player's handbook", "dungeon master's guide", "monster manual",
        "xanathar's guide", "tasha's cauldron", "sword coast", "volo's guide",
        "mordenkainen's tome", "chapter", "page", "official", "errata",
        "sage advice", "optional", "variant", "house rule", "mechanics"
    ],

    "backgrounds": [
        "background", "acolyte", "charlatan", "criminal", "entertainer",
        "folk hero", "guild artisan", "hermit", "noble", "outlander",
        "sage", "sailor", "soldier", "urchin", "feature", "personality trait",
        "ideal", "bond", "flaw", "proficiency", "language", "equipment",
        "variant", "custom"
    ],

    "feats": [
        "feat", "ability score improvement", "asi", "prerequisite", "actor",
        "alert", "athlete", "charger", "crossbow expert", "defensive duelist",
        "dual wielder", "dungeon delver", "durable", "elemental adept",
        "grappler", "great weapon master", "healer", "inspiring leader",
        "lucky", "mage slayer", "magic initiate", "martial adept",
        "mobile", "mounted combatant", "observant", "polearm master",
        "resilient", "ritual caster", "savage attacker", "sentinel",
        "sharpshooter", "shield master", "skilled", "skulker", "spell sniper",
        "tavern brawler", "tough", "war caster", "weapon master"
    ],

    "conditions": [
        "condition", "blinded", "charmed", "deafened", "exhaustion", "frightened",
        "grappled", "incapacitated", "invisible", "paralyzed", "petrified",
        "poisoned", "prone", "restrained", "stunned", "unconscious", "level",
        "effect", "remove", "cure", "immune", "resistant", "vulnerable"
    ]
}

# Create a reverse mapping for lookup
KEYWORD_TO_CATEGORY = {}
for category, keywords in CATEGORY_KEYWORDS.items():
    for keyword in keywords:
        if keyword not in KEYWORD_TO_CATEGORY:
            KEYWORD_TO_CATEGORY[keyword] = []
        KEYWORD_TO_CATEGORY[keyword].append(category)


def prioritize_categories(query: str) -> Dict[str, float]:
    """
    Determine which D&D categories are most relevant to a query.

    Args:
        query: The search query

    Returns:
        Dictionary mapping category names to relevance scores (0.0-1.0)
    """
    query = query.lower()
    category_scores = {
        "spells": 0.0,
        "monsters": 0.0,
        "classes": 0.0,
        "races": 0.0,
        "equipment": 0.0,
        "magic-items": 0.0,
        "rules": 0.0,
        "backgrounds": 0.0,
        "feats": 0.0,
        "conditions": 0.0
    }

    # Split the query into words
    words = re.findall(r'\b\w+\b', query.lower())

    # Check for exact category mentions
    for category in category_scores.keys():
        # If the category name is explicitly mentioned, give it a high score
        if category.lower() in query or category.lower().rstrip('s') in query:
            category_scores[category] += 0.8

    # Check for keyword matches
    for word in words:
        if word in KEYWORD_TO_CATEGORY:
            for category in KEYWORD_TO_CATEGORY[word]:
                # Increment the score for each keyword match
                category_scores[category] += 0.2

    # Check for multi-word keywords
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if ' ' in keyword and keyword in query:
                # Multi-word matches are more specific, so give them a higher score
                category_scores[category] += 0.3

    # Normalize scores to be between 0 and 1
    max_score = max(category_scores.values()
                    ) if category_scores.values() else 1.0
    if max_score > 0:
        for category in category_scores:
            category_scores[category] /= max_score

    # If no clear priorities, give a small base score to common categories
    if max_score < 0.2:
        default_categories = ["spells", "monsters", "equipment"]
        for category in default_categories:
            category_scores[category] = max(category_scores[category], 0.3)

    return category_scores


def get_top_categories(query: str, num_categories: int = 3) -> List[str]:
    """
    Get the top N categories most relevant to a query.

    Args:
        query: The search query
        num_categories: Number of top categories to return

    Returns:
        List of category names, ordered by relevance
    """
    scores = prioritize_categories(query)

    # Sort categories by score in descending order
    sorted_categories = sorted(
        scores.items(), key=lambda x: x[1], reverse=True)

    # Return the top N categories
    return [category for category, score in sorted_categories[:num_categories] if score > 0]
