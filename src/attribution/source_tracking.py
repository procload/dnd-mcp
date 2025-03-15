"""
Source tracking integration module for D&D Knowledge Navigator.

This module integrates attribution, citation, confidence scoring, and tool tracking
to provide comprehensive source tracking for all information.
"""

from typing import Dict, Any, List, Optional, Tuple
from src.attribution.core import (
    SourceAttribution,
    AttributionManager,
    ConfidenceLevel,
    attribution_manager
)
from src.attribution.citation import Citation, CitationManager, citation_manager
from src.attribution.confidence import ConfidenceScorer, ConfidenceFactors
from src.attribution.tool_tracking import ToolTracker, ToolCategory, tool_tracker, track_tool_usage
from src.attribution.formatters import format_all_attribution_for_display


class SourceTracker:
    """
    Class for integrating all source tracking functionality.
    """

    def __init__(self):
        """Initialize the source tracker."""
        self.attribution_manager = attribution_manager
        self.citation_manager = citation_manager
        self.tool_tracker = tool_tracker

    @track_tool_usage(ToolCategory.CONTEXT)
    def prepare_response_with_sources(self,
                                      response_data: Dict[str, Any],
                                      attribution_map: Dict[str, str],
                                      citation_indices: Optional[List[int]] = None,
                                      include_formatted_attribution: bool = True) -> Dict[str, Any]:
        """
        Prepare a response with comprehensive source information.

        Args:
            response_data: The data to be returned to the user
            attribution_map: Mapping of keys in response_data to attribution IDs
            citation_indices: Optional list of citation indices to include
            include_formatted_attribution: Whether to include formatted attribution in the response

        Returns:
            Response data with added source information
        """
        result = self.attribution_manager.format_response_with_attributions(
            response_data, attribution_map
        )

        # Add tool usage information
        result["tool_usage"] = self.tool_tracker.get_usages_for_response()

        # Add citations if provided
        if citation_indices:
            result["citations_markdown"] = self.citation_manager.format_citations(
                citation_indices)

        # Add formatted attribution for display to the user
        if include_formatted_attribution:
            result["formatted_attribution"] = format_all_attribution_for_display(
                result)

        return result

    @track_tool_usage(ToolCategory.INFERENCE)
    def calculate_overall_confidence(self, attribution_ids: List[str]) -> Tuple[float, ConfidenceLevel]:
        """
        Calculate overall confidence based on multiple attributions.

        Args:
            attribution_ids: List of attribution IDs

        Returns:
            Tuple of (confidence_score, confidence_level)
        """
        # Get all attributions
        attributions = [
            self.attribution_manager.get_attribution(attr_id)
            for attr_id in attribution_ids
            if self.attribution_manager.get_attribution(attr_id) is not None
        ]

        if not attributions:
            return 0.0, ConfidenceLevel.UNCERTAIN

        # Calculate average confidence and relevance
        confidence_values = {
            ConfidenceLevel.HIGH: 0.9,
            ConfidenceLevel.MEDIUM: 0.6,
            ConfidenceLevel.LOW: 0.3,
            ConfidenceLevel.UNCERTAIN: 0.1
        }

        avg_confidence = sum(
            confidence_values[attr.confidence] for attr in attributions) / len(attributions)
        avg_relevance = sum(
            attr.relevance_score for attr in attributions) / len(attributions) / 100

        # Check for multiple or contradictory sources
        sources = set(attr.source for attr in attributions)
        has_multiple_sources = len(sources) > 1

        # Determine if there are official sources
        official_sources = ["Player's Handbook",
                            "Dungeon Master's Guide", "Monster Manual"]
        has_official_source = any(
            source in official_sources for source in sources)

        # Build confidence factors
        factors = {
            ConfidenceFactors.DIRECT_API_MATCH: avg_confidence,
            ConfidenceFactors.MULTIPLE_SOURCES: 1.0 if has_multiple_sources else 0.0,
            ConfidenceFactors.OFFICIAL_SOURCE: 1.0 if has_official_source else 0.0,
        }

        return ConfidenceScorer.calculate_confidence(factors)

    @track_tool_usage(ToolCategory.CONTEXT)
    def prepare_mcp_response(self,
                             response_data: Dict[str, Any],
                             attribution_map: Dict[str, str],
                             citation_indices: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Prepare a response for MCP with source information included in the content.

        This method is specifically designed for MCP responses, where we need to include
        the attribution information in the content itself rather than as separate metadata.

        Args:
            response_data: The data to be returned to the user
            attribution_map: Mapping of keys in response_data to attribution IDs
            citation_indices: Optional list of citation indices to include

        Returns:
            Response data with attribution information included in the content
        """
        # First, prepare the response with sources
        result = self.prepare_response_with_sources(
            response_data, attribution_map, citation_indices, include_formatted_attribution=True
        )

        # Get the formatted attribution
        formatted_attribution = result.get("formatted_attribution", "")

        # Create a new response with the attribution included in the content
        mcp_response = {}

        # Copy the original response data
        for key, value in response_data.items():
            mcp_response[key] = value

        # Add the formatted attribution to the response
        if "content" in mcp_response and isinstance(mcp_response["content"], str):
            mcp_response["content"] += formatted_attribution
        elif isinstance(mcp_response, dict):
            # Convert the response to a string representation
            content = ""
            for key, value in mcp_response.items():
                if key not in ["attributions", "tool_usage", "sources_summary", "citations_markdown", "formatted_attribution"]:
                    if isinstance(value, dict):
                        content += f"\n## {key.capitalize()}\n"
                        for subkey, subvalue in value.items():
                            content += f"\n### {subkey.capitalize()}\n"
                            content += f"{subvalue}\n"
                    else:
                        content += f"\n## {key.capitalize()}\n"
                        content += f"{value}\n"

            # Add the formatted attribution
            content += formatted_attribution
            mcp_response["content"] = content

        return mcp_response


# Global instance of the source tracker
source_tracker = SourceTracker()
