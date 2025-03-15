"""
Formatters for attribution information.

This module provides functions to format attribution information for display to the user.
"""

from typing import Dict, Any, List
from src.attribution.core import SourceAttribution


def format_attribution_for_display(attribution: Dict[str, Any]) -> str:
    """
    Format attribution information for display to the user.

    Args:
        attribution: Attribution information as a dictionary

    Returns:
        Markdown formatted attribution information
    """
    if not attribution:
        return ""

    md = "\n\n---\n\n**Source Information:**\n\n"

    # Source and confidence
    md += f"* **Source:** {attribution.get('source', 'Unknown')}\n"

    confidence = attribution.get('confidence', 'unknown')
    md += f"* **Confidence:** {confidence.capitalize()}\n"

    # Page number if available
    if 'page' in attribution and attribution['page']:
        md += f"* **Page:** {attribution['page']}\n"

    # API endpoint
    if 'api_endpoint' in attribution:
        md += f"* **API:** {attribution['api_endpoint']}\n"

    # Relevance score if available
    if 'relevance_score' in attribution:
        md += f"* **Relevance:** {attribution['relevance_score']:.1f}%\n"

    return md


def format_attributions_for_display(attributions: Dict[str, Dict[str, Any]]) -> str:
    """
    Format multiple attributions for display to the user.

    Args:
        attributions: Dictionary mapping keys to attribution information

    Returns:
        Markdown formatted attribution information
    """
    if not attributions:
        return ""

    # Group attributions by source
    sources = {}
    for key, attr in attributions.items():
        source = attr.get('source', 'Unknown')
        if source not in sources:
            sources[source] = []
        sources[source].append(attr)

    md = "\n\n---\n\n**Source Information:**\n\n"

    for source, attrs in sources.items():
        md += f"### {source}\n\n"

        # Get unique confidence levels
        confidence_levels = set(attr.get('confidence', 'unknown')
                                for attr in attrs)
        confidence_str = ", ".join(level.capitalize()
                                   for level in confidence_levels)
        md += f"* **Confidence:** {confidence_str}\n"

        # Get unique API endpoints
        endpoints = set(attr.get('api_endpoint', '')
                        for attr in attrs if 'api_endpoint' in attr)
        if endpoints:
            md += "* **APIs:**\n"
            for endpoint in endpoints:
                md += f"  * {endpoint}\n"

        # Page numbers if available
        pages = set(attr.get('page', None)
                    for attr in attrs if 'page' in attr and attr['page'])
        if pages:
            page_str = ", ".join(str(page) for page in pages)
            md += f"* **Pages:** {page_str}\n"

        md += "\n"

    return md


def format_tool_usage_for_display(tool_usage: List[Dict[str, Any]]) -> str:
    """
    Format tool usage information for display to the user.

    Args:
        tool_usage: List of tool usage records

    Returns:
        Markdown formatted tool usage information
    """
    if not tool_usage:
        return ""

    md = "\n\n---\n\n**Tools Used:**\n\n"

    for usage in tool_usage:
        md += f"* **{usage.get('tool', 'Unknown Tool')}** ({usage.get('category', 'unknown')})\n"
        md += f"  * Execution time: {usage.get('execution_time', 'unknown')}\n"

    return md


def format_sources_summary_for_display(sources_summary: List[str]) -> str:
    """
    Format sources summary for display to the user.

    Args:
        sources_summary: List of source names

    Returns:
        Markdown formatted sources summary
    """
    if not sources_summary:
        return ""

    md = "\n\n---\n\n**Sources:**\n\n"

    for source in sources_summary:
        md += f"* {source}\n"

    return md


def format_all_attribution_for_display(response_data: Dict[str, Any]) -> str:
    """
    Format all attribution information from a response for display to the user.

    Args:
        response_data: Response data containing attribution information

    Returns:
        Markdown formatted attribution information
    """
    md = ""

    # Add attributions if available
    if 'attributions' in response_data and response_data['attributions']:
        md += format_attributions_for_display(response_data['attributions'])

    # Add tool usage if available
    if 'tool_usage' in response_data and response_data['tool_usage']:
        md += format_tool_usage_for_display(response_data['tool_usage'])

    # Add sources summary if available
    if 'sources_summary' in response_data and response_data['sources_summary']:
        md += format_sources_summary_for_display(
            response_data['sources_summary'])

    # Add citations if available
    if 'citations_markdown' in response_data and response_data['citations_markdown']:
        md += f"\n\n{response_data['citations_markdown']}"

    return md
