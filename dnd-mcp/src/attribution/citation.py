"""
Citation module for D&D Knowledge Navigator.

This module provides functionality to create, format, and manage citations
for specific rules, descriptions, and other D&D content.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from src.attribution.core import SourceAttribution


@dataclass
class Citation:
    """
    Data class for storing citation information.

    Attributes:
        text: The cited text
        attribution: Attribution information for the citation
        context: Additional context about the citation
    """
    text: str
    attribution: SourceAttribution
    context: Optional[str] = None

    def to_markdown(self) -> str:
        """Generate a markdown representation of the citation."""
        md = f"> \"{self.text}\"\n>\n"
        md += f"> {self.attribution.to_markdown()}"

        if self.context:
            md += f"\n>\n> *Context: {self.context}*"

        return md


class CitationManager:
    """
    Manager class for handling citations throughout the system.
    """

    def __init__(self):
        """Initialize the citation manager."""
        self.citations: List[Citation] = []

    def add_citation(self, citation: Citation) -> int:
        """
        Add a citation to the manager.

        Args:
            citation: The citation to add

        Returns:
            Index of the added citation
        """
        self.citations.append(citation)
        return len(self.citations) - 1

    def get_citation(self, index: int) -> Optional[Citation]:
        """
        Get a citation by index.

        Args:
            index: Index of the citation

        Returns:
            Citation if found, None otherwise
        """
        if 0 <= index < len(self.citations):
            return self.citations[index]
        return None

    def format_citations(self, indices: List[int]) -> str:
        """
        Format multiple citations as markdown.

        Args:
            indices: Indices of citations to format

        Returns:
            Markdown formatted citations
        """
        result = "## Citations\n\n"

        for i, idx in enumerate(indices, 1):
            citation = self.get_citation(idx)
            if citation:
                result += f"### {i}. {citation.to_markdown()}\n\n"

        return result


# Global instance of the citation manager
citation_manager = CitationManager()
