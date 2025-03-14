"""
Query Enhancement module for D&D Knowledge Navigator.

This module provides functions to enhance search queries by handling
synonyms, special D&D terms, and implementing fuzzy matching.
"""

from src.query_enhancement.synonyms import expand_query_with_synonyms
from src.query_enhancement.tokenizer import tokenize_dnd_query
from src.query_enhancement.fuzzy_matching import fuzzy_match, correct_misspellings
from src.query_enhancement.category_prioritization import prioritize_categories, get_top_categories

__all__ = [
    'expand_query_with_synonyms',
    'tokenize_dnd_query',
    'fuzzy_match',
    'correct_misspellings',
    'prioritize_categories',
    'get_top_categories',
    'enhance_query'
]


def enhance_query(query: str, use_synonyms: bool = True,
                  use_special_tokenization: bool = True,
                  use_fuzzy_matching: bool = True):
    """
    Enhance a D&D query by applying various enhancement techniques.

    Args:
        query: The original search query
        use_synonyms: Whether to expand the query with synonyms
        use_special_tokenization: Whether to use special D&D tokenization
        use_fuzzy_matching: Whether to apply fuzzy matching

    Returns:
        Enhanced query and metadata about the enhancements
    """
    enhanced_query = query
    enhancements = {
        "original_query": query,
        "enhanced_query": query,
        "synonyms_added": [],
        "special_terms": [],
        "fuzzy_matches": [],
        "category_priorities": {}
    }

    # Apply tokenization if enabled
    if use_special_tokenization:
        tokens, special_terms = tokenize_dnd_query(query)
        enhancements["special_terms"] = special_terms
    else:
        tokens = query.split()

    # Apply synonym expansion if enabled
    if use_synonyms:
        expanded_query, synonyms_added = expand_query_with_synonyms(query)
        enhanced_query = expanded_query
        enhancements["synonyms_added"] = synonyms_added
        enhancements["enhanced_query"] = enhanced_query

    # Apply fuzzy matching if enabled
    if use_fuzzy_matching:
        fuzzy_matches = fuzzy_match(tokens)
        enhancements["fuzzy_matches"] = fuzzy_matches
        # We don't modify the query here, just provide potential corrections

    # Determine category priorities
    category_priorities = prioritize_categories(enhanced_query)
    enhancements["category_priorities"] = category_priorities

    return enhanced_query, enhancements
