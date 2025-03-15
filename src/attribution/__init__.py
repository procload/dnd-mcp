"""
Source attribution package for D&D Knowledge Navigator.

This package provides functionality to track, store, and display attribution
information for all data returned by the system.
"""

from src.attribution.core import (
    SourceAttribution,
    AttributionManager,
    ConfidenceLevel,
    attribution_manager
)
from src.attribution.citation import (
    Citation,
    CitationManager,
    citation_manager
)
from src.attribution.confidence import (
    ConfidenceScorer,
    ConfidenceFactors
)
from src.attribution.tool_tracking import (
    ToolUsage,
    ToolTracker,
    ToolCategory,
    track_tool_usage,
    tool_tracker
)
from src.attribution.source_tracking import (
    SourceTracker,
    source_tracker
)

__all__ = [
    'SourceAttribution',
    'AttributionManager',
    'ConfidenceLevel',
    'attribution_manager',
    'Citation',
    'CitationManager',
    'citation_manager',
    'ConfidenceScorer',
    'ConfidenceFactors',
    'ToolUsage',
    'ToolTracker',
    'ToolCategory',
    'track_tool_usage',
    'tool_tracker',
    'SourceTracker',
    'source_tracker'
]
