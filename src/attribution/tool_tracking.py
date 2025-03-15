"""
Tool tracking module for D&D Knowledge Navigator.

This module provides functionality to track which tools and functions
are used to retrieve and process information.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import time
import functools


class ToolCategory(Enum):
    """Categories of tools used in the system."""
    SEARCH = "search"
    AGGREGATION = "aggregation"
    FORMATTING = "formatting"
    INFERENCE = "inference"
    CONTEXT = "context"


@dataclass
class ToolUsage:
    """
    Data class for storing information about tool usage.

    Attributes:
        tool_name: Name of the tool/function
        category: Category of the tool
        input_summary: Summary of the input to the tool
        output_summary: Summary of the output from the tool
        execution_time: Time taken to execute the tool (in seconds)
        metadata: Additional metadata about the tool usage
    """
    tool_name: str
    category: ToolCategory
    input_summary: str
    output_summary: str
    execution_time: float
    metadata: Optional[Dict[str, Any]] = None


class ToolTracker:
    """
    Class for tracking tool usage throughout the system.
    """

    def __init__(self):
        """Initialize the tool tracker."""
        self.tool_usages: List[ToolUsage] = []

    def add_usage(self, usage: ToolUsage) -> None:
        """
        Add a tool usage record.

        Args:
            usage: The tool usage record to add
        """
        self.tool_usages.append(usage)

    def get_usages_for_response(self) -> List[Dict[str, Any]]:
        """
        Get all tool usages formatted for inclusion in a response.

        Returns:
            List of tool usage records as dictionaries
        """
        return [
            {
                "tool": usage.tool_name,
                "category": usage.category.value,
                "execution_time": f"{usage.execution_time:.3f}s",
                "input": usage.input_summary,
                "output": usage.output_summary
            }
            for usage in self.tool_usages
        ]

    def clear(self) -> None:
        """Clear all tool usage records."""
        self.tool_usages = []


# Global instance of the tool tracker
tool_tracker = ToolTracker()


def track_tool_usage(category: ToolCategory,
                     input_summary_func: Optional[Callable] = None,
                     output_summary_func: Optional[Callable] = None):
    """
    Decorator to track tool usage.

    Args:
        category: Category of the tool
        input_summary_func: Function to generate input summary (defaults to str)
        output_summary_func: Function to generate output summary (defaults to str)

    Returns:
        Decorated function
    """
    if input_summary_func is None:
        def input_summary_func(x): return str(
            x)[:100] + "..." if len(str(x)) > 100 else str(x)

    if output_summary_func is None:
        def output_summary_func(x): return str(
            x)[:100] + "..." if len(str(x)) > 100 else str(x)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            # Generate input summary
            args_summary = ", ".join(input_summary_func(arg) for arg in args)
            kwargs_summary = ", ".join(
                f"{k}={input_summary_func(v)}" for k, v in kwargs.items())
            input_summary = f"{args_summary}{', ' if args_summary and kwargs_summary else ''}{kwargs_summary}"

            # Execute the function
            result = func(*args, **kwargs)

            # Calculate execution time
            execution_time = time.time() - start_time

            # Generate output summary
            output_summary = output_summary_func(result)

            # Create and add tool usage record
            usage = ToolUsage(
                tool_name=func.__name__,
                category=category,
                input_summary=input_summary,
                output_summary=output_summary,
                execution_time=execution_time
            )
            tool_tracker.add_usage(usage)

            return result
        return wrapper
    return decorator
