"""
Core attribution module for D&D Knowledge Navigator.

This module provides the base classes for source attribution.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
import uuid


class ConfidenceLevel(Enum):
    """Enum representing confidence levels for information provided."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


@dataclass
class SourceAttribution:
    """
    Data class for storing attribution information for a piece of data.

    Attributes:
        source: The name of the source (e.g., "Player's Handbook")
        page: Optional page number in the source
        api_endpoint: The API endpoint that provided the data
        confidence: Confidence level in the accuracy of the information
        relevance_score: How relevant this information is to the query (0-100)
        tool_used: Which tool/function was used to retrieve this information
        metadata: Additional metadata about the source
    """
    source: str
    api_endpoint: str
    confidence: ConfidenceLevel
    relevance_score: float  # 0-100
    tool_used: str
    page: Optional[int] = None
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the attribution to a dictionary format."""
        result = {
            "source": self.source,
            "api_endpoint": self.api_endpoint,
            "confidence": self.confidence.value,
            "relevance_score": self.relevance_score,
            "tool_used": self.tool_used
        }

        if self.page:
            result["page"] = self.page

        if self.metadata:
            result["metadata"] = self.metadata

        return result

    def to_markdown(self) -> str:
        """Generate a markdown representation of the attribution."""
        md = f"*Source: {self.source}"

        if self.page:
            md += f", p. {self.page}"

        md += f" | Confidence: {self.confidence.value.capitalize()}"
        md += f" | API: {self.api_endpoint}*"

        return md


class AttributionManager:
    """
    Manager class for handling source attributions throughout the system.
    """

    def __init__(self):
        """Initialize the attribution manager."""
        self.attributions: Dict[str, SourceAttribution] = {}

    def add_attribution(self, data_id: str = None, attribution: SourceAttribution = None) -> str:
        """
        Add attribution information for a piece of data.

        Args:
            data_id: Unique identifier for the data (generated if None)
            attribution: Attribution information

        Returns:
            The data_id used (either provided or generated)
        """
        if data_id is None:
            data_id = str(uuid.uuid4())

        if attribution is not None:
            self.attributions[data_id] = attribution

        return data_id

    def get_attribution(self, data_id: str) -> Optional[SourceAttribution]:
        """
        Get attribution information for a piece of data.

        Args:
            data_id: Unique identifier for the data

        Returns:
            Attribution information if available, None otherwise
        """
        return self.attributions.get(data_id)

    def format_response_with_attributions(self,
                                          response_data: Dict[str, Any],
                                          attribution_map: Dict[str, str]) -> Dict[str, Any]:
        """
        Format a response with attribution information.

        Args:
            response_data: The data to be returned to the user
            attribution_map: Mapping of keys in response_data to attribution IDs

        Returns:
            Response data with added attribution information
        """
        result = response_data.copy()

        # Add attribution metadata
        result["attributions"] = {}

        for key, attr_id in attribution_map.items():
            if attr_id in self.attributions:
                result["attributions"][key] = self.attributions[attr_id].to_dict()

        # Add a summary of sources used
        sources_used = set()
        for attr_id in attribution_map.values():
            if attr_id in self.attributions:
                sources_used.add(self.attributions[attr_id].source)

        result["sources_summary"] = list(sources_used)

        return result


# Global instance of the attribution manager
attribution_manager = AttributionManager()
