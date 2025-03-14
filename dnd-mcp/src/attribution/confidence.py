"""
Confidence scoring module for D&D Knowledge Navigator.

This module provides functionality to calculate and manage confidence scores
for information provided by the system.
"""

from typing import Dict, Any, List, Tuple
from enum import Enum
from src.attribution.core import ConfidenceLevel


class ConfidenceFactors(Enum):
    """Factors that influence confidence scoring."""
    DIRECT_API_MATCH = "direct_api_match"
    FUZZY_MATCH = "fuzzy_match"
    INFERENCE = "inference"
    MULTIPLE_SOURCES = "multiple_sources"
    CONTRADICTORY_SOURCES = "contradictory_sources"
    OFFICIAL_SOURCE = "official_source"
    COMMUNITY_SOURCE = "community_source"
    INCOMPLETE_DATA = "incomplete_data"


class ConfidenceScorer:
    """
    Class for calculating confidence scores for information.
    """

    # Base weights for different confidence factors
    FACTOR_WEIGHTS = {
        ConfidenceFactors.DIRECT_API_MATCH: 0.9,
        ConfidenceFactors.FUZZY_MATCH: 0.6,
        ConfidenceFactors.INFERENCE: 0.4,
        ConfidenceFactors.MULTIPLE_SOURCES: 0.2,  # Bonus
        ConfidenceFactors.CONTRADICTORY_SOURCES: -0.3,  # Penalty
        ConfidenceFactors.OFFICIAL_SOURCE: 0.15,  # Bonus
        ConfidenceFactors.COMMUNITY_SOURCE: -0.1,  # Penalty
        ConfidenceFactors.INCOMPLETE_DATA: -0.2,  # Penalty
    }

    @classmethod
    def calculate_confidence(cls,
                             factors: Dict[ConfidenceFactors, float]) -> Tuple[float, ConfidenceLevel]:
        """
        Calculate a confidence score based on various factors.

        Args:
            factors: Dictionary mapping confidence factors to their values (0-1)

        Returns:
            Tuple of (confidence_score, confidence_level)
        """
        base_score = 0.5  # Start at 50%

        for factor, value in factors.items():
            weight = cls.FACTOR_WEIGHTS.get(factor, 0)
            base_score += weight * value

        # Clamp score between 0 and 1
        confidence_score = max(0, min(1, base_score))

        # Convert to percentage
        confidence_percentage = confidence_score * 100

        # Determine confidence level
        if confidence_percentage >= 80:
            confidence_level = ConfidenceLevel.HIGH
        elif confidence_percentage >= 50:
            confidence_level = ConfidenceLevel.MEDIUM
        elif confidence_percentage >= 30:
            confidence_level = ConfidenceLevel.LOW
        else:
            confidence_level = ConfidenceLevel.UNCERTAIN

        return confidence_percentage, confidence_level

    @classmethod
    def explain_confidence(cls,
                           factors: Dict[ConfidenceFactors, float],
                           confidence_score: float,
                           confidence_level: ConfidenceLevel) -> str:
        """
        Generate an explanation for a confidence score.

        Args:
            factors: Dictionary mapping confidence factors to their values
            confidence_score: The calculated confidence score
            confidence_level: The determined confidence level

        Returns:
            Markdown formatted explanation
        """
        explanation = f"**Confidence: {confidence_level.value.capitalize()} ({confidence_score:.1f}%)**\n\n"
        explanation += "Factors affecting this confidence score:\n\n"

        for factor, value in factors.items():
            weight = cls.FACTOR_WEIGHTS.get(factor, 0)
            impact = weight * value

            if impact > 0:
                direction = "Increased"
            elif impact < 0:
                direction = "Decreased"
            else:
                direction = "No impact on"

            explanation += f"- {factor.value.replace('_', ' ').capitalize()}: {direction} confidence by {abs(impact)*100:.1f}%\n"

        return explanation
