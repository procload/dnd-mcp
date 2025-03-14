# Query Enhancement System

The Query Enhancement System improves search results by understanding D&D-specific terminology, handling synonyms, recognizing special terms, and correcting common misspellings.

## Overview

The D&D Knowledge Navigator's Query Enhancement System processes user queries to make them more effective when searching the D&D 5e API. It addresses several common challenges in D&D searches:

1. **Terminology Variations**: Users may use different terms for the same concept (e.g., "AC" vs "armor class")
2. **Special D&D Terms**: Recognition of game-specific notation and abbreviations (e.g., "2d6+3", "STR save")
3. **Common Misspellings**: Correction of frequently misspelled D&D terms (e.g., "firball" → "fireball")
4. **Category Prioritization**: Intelligent routing of queries to the most relevant API categories

## Key Components

### Synonym Expansion

The system maintains a comprehensive dictionary of D&D-specific synonyms, allowing it to understand various ways users might refer to the same concept:

- Abbreviations: "AC" → "armor class", "HP" → "hit points"
- Game terms: "save" → "saving throw", "stat" → "ability score"
- Variations: "armor" → "armour", "defense" → "defence"

When a query contains a term with known synonyms, the system can expand the query to include the canonical term, improving search results.

### Special Term Tokenization

D&D has many special terms and notation that require special handling:

- Dice notation: "2d6+3", "1d20"
- Ability scores: "STR", "DEX", "CON", "INT", "WIS", "CHA"
- Book abbreviations: "PHB", "DMG", "XGE"
- Game mechanics: "DC", "CR", "AoE"

The tokenizer preserves these special terms as single tokens rather than breaking them apart, ensuring they're properly understood during searches.

### Fuzzy Matching

The system includes a database of commonly misspelled D&D terms and can suggest corrections:

- "firball" → "fireball"
- "rouge" → "rogue"
- "wizzard" → "wizard"
- "armour class" → "armor class"

This helps users get accurate results even when they make typing errors or use alternative spellings.

### Category Prioritization

Not all D&D content categories are equally relevant for every query. The system analyzes queries to determine which categories are most likely to contain relevant information:

- Spell-related terms prioritize the "spells" category
- Monster-related terms prioritize the "monsters" category
- Equipment-related terms prioritize the "equipment" and "magic-items" categories

This improves search efficiency and result relevance.

## Usage

The Query Enhancement System is integrated into the main search tools:

```python
from src.query_enhancement import enhance_query

# Enhance a query
enhanced_query, enhancements = enhance_query("What is the AC of a dragon?")

# Access enhancement details
synonyms_added = enhancements["synonyms_added"]  # [("AC", "armor class")]
special_terms = enhancements["special_terms"]    # ["AC"]
fuzzy_matches = enhancements["fuzzy_matches"]    # []
category_priorities = enhancements["category_priorities"]  # {"monsters": 0.9, ...}
```

### Individual Components

You can also use the individual components directly:

```python
from src.query_enhancement import (
    expand_query_with_synonyms,
    tokenize_dnd_query,
    fuzzy_match,
    prioritize_categories
)

# Expand synonyms
expanded_query, synonyms = expand_query_with_synonyms("What is the AC of a dragon?")
# "what is the ac of a dragon? armor class", [("ac", "armor class")]

# Tokenize with special term handling
tokens, special_terms = tokenize_dnd_query("How much damage does 2d6+3 do?")
# ["how", "much", "damage", "does", "2d6+3", "do"], ["2d6+3"]

# Find potential corrections for misspellings
corrections = fuzzy_match(["firball", "rouge", "wizzard"])
# [("firball", "fireball"), ("rouge", "rogue"), ("wizzard", "wizard")]

# Get category priorities for a query
priorities = prioritize_categories("How does fireball spell work?")
# {"spells": 1.0, "monsters": 0.3, ...}
```

## Benefits

The Query Enhancement System provides several key benefits:

1. **Improved Search Accuracy**: Users get relevant results even when using abbreviations, alternative terms, or making spelling errors
2. **Better User Experience**: Less frustration from "no results found" responses
3. **More Efficient Searches**: Focusing on relevant categories reduces API calls and improves response time
4. **Handling of D&D Jargon**: Special recognition of game-specific terminology that general search systems wouldn't understand

## Configuration

The system is designed to be configurable:

- Synonym dictionaries can be extended with new terms
- Special term recognition can be updated for new game content
- Fuzzy matching thresholds can be adjusted for more or less aggressive correction
- Category prioritization weights can be tuned based on usage patterns

## Integration with Other Components

The Query Enhancement System works seamlessly with other D&D Knowledge Navigator components:

- **Source Attribution**: Enhanced queries maintain proper attribution to original sources
- **Template System**: Enhanced search results work with the template formatting system
- **MCP Integration**: All enhancements are included in the MCP response for transparency
