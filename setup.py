#!/usr/bin/env python3
"""
Setup script for the D&D Knowledge Navigator.
"""

from setuptools import setup, find_packages

setup(
    name="dnd-knowledge-navigator",
    version="1.0.0",
    description="A Model Context Protocol (MCP) server for D&D 5e information",
    author="D&D Knowledge Navigator Contributors",
    author_email="your.email@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastmcp",
        "requests",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "dnd-knowledge-navigator=dnd_mcp_server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
)
