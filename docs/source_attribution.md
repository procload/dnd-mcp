# Source Attribution System

## Overview

The Source Attribution System is a comprehensive framework for tracking, storing, and displaying attribution information for all data returned by the D&D Knowledge Navigator. It ensures that users can trust the information provided by clearly indicating where it comes from, how confident the system is in its accuracy, and which tools were used to retrieve it.

## Key Components

### 1. Source Attribution

The core of the system is the `SourceAttribution` class, which stores detailed information about the source of each piece of data:

- **Source**: The name of the source (e.g., "Player's Handbook")
- **API Endpoint**: The API endpoint that provided the data
- **Confidence Level**: How confident the system is in the accuracy of the information (HIGH, MEDIUM, LOW, UNCERTAIN)
- **Relevance Score**: How relevant this information is to the query (0-100)
- **Tool Used**: Which tool/function was used to retrieve this information
- **Page**: Optional page number in the source
- **Metadata**: Additional metadata about the source

### 2. Citation System

The Citation System allows for specific rule citations with proper formatting:

- **Text**: The cited text
- **Attribution**: Attribution information for the citation
- **Context**: Additional context about the citation

Citations are formatted in markdown for clear presentation to the user.

### 3. Confidence Scoring

The Confidence Scoring System calculates how confident the system is in the provided information based on various factors:

- **Direct API Match**: Information comes directly from the API
- **Fuzzy Match**: Information is based on fuzzy matching
- **Inference**: Information is inferred from other data
- **Multiple Sources**: Information is confirmed by multiple sources
- **Contradictory Sources**: Information has contradictions between sources
- **Official Source**: Information comes from an official source
- **Community Source**: Information comes from a community source
- **Incomplete Data**: Information is based on incomplete data

### 4. Tool Usage Tracking

The Tool Usage Tracking System monitors which tools and functions are used to retrieve data:

- **Tool Name**: Name of the tool/function
- **Category**: Category of the tool (SEARCH, AGGREGATION, FORMATTING, INFERENCE, CONTEXT)
- **Input Summary**: Summary of the input to the tool
- **Output Summary**: Summary of the output from the tool
- **Execution Time**: Time taken to execute the tool (in seconds)
- **Metadata**: Additional metadata about the tool usage

### 5. Source Tracking Integration

The Source Tracking Integration System combines all the above components into a cohesive system that can be easily integrated into API responses.

## Usage

### Adding Attribution to a Response

```python
from src.attribution import (
    SourceAttribution,
    ConfidenceLevel,
    attribution_manager,
    source_tracker
)

# Create an attribution
attr_id = attribution_manager.add_attribution(
    attribution=SourceAttribution(
        source="Player's Handbook",
        api_endpoint="/api/spells/fireball",
        confidence=ConfidenceLevel.HIGH,
        relevance_score=95.0,
        tool_used="search_spells",
        page=241,
        metadata={"spell_level": 3}
    )
)

# Create a response
response_data = {
    "name": "Fireball",
    "level": 3,
    "description": "A bright streak flashes from your pointing finger to a point you choose..."
}

# Map response keys to attribution IDs
attribution_map = {
    "name": attr_id,
    "level": attr_id,
    "description": attr_id
}

# Format the response with attributions
formatted_response = source_tracker.prepare_response_with_sources(
    response_data, attribution_map
)
```

### Tracking Tool Usage

```python
from src.attribution import track_tool_usage, ToolCategory

@track_tool_usage(ToolCategory.SEARCH)
def search_function(query):
    # Function implementation
    return results
```

### Calculating Confidence

```python
from src.attribution import ConfidenceScorer, ConfidenceFactors

factors = {
    ConfidenceFactors.DIRECT_API_MATCH: 0.8,
    ConfidenceFactors.OFFICIAL_SOURCE: 1.0,
    ConfidenceFactors.MULTIPLE_SOURCES: 0.5
}

score, level = ConfidenceScorer.calculate_confidence(factors)
explanation = ConfidenceScorer.explain_confidence(factors, score, level)
```

## Integration with Existing Tools

The Source Attribution System has been integrated with the `search_all_categories` function to provide comprehensive attribution information for search results. Each item in the search results includes:

- Source attribution (D&D 5e API)
- Confidence level based on match quality
- Relevance score based on search ranking
- API endpoint information
- Tool usage tracking

## Integration with MCP

The Model Context Protocol (MCP) is a standardized way for LLMs to interact with external tools and data sources. To make our source attribution system work with MCP, we've implemented a special response preparation method that includes the attribution information in the content of the response.

### Using Source Attribution with MCP

When using our tools through MCP, the attribution information is automatically included at the end of the response content. This allows the LLM to see and present the attribution information to the user.

Here's how to use source attribution with MCP:

```python
from src.attribution import (
    SourceAttribution,
    ConfidenceLevel,
    attribution_manager,
    source_tracker
)

@app.tool()
@track_tool_usage(ToolCategory.SEARCH)
def my_search_tool(query: str) -> Dict[str, Any]:
    """Search for information and return results with attribution."""

    # Clear previous tool usages for this request
    source_tracker.tool_tracker.clear()

    # Create your response data
    response_data = {
        "query": query,
        "results": {
            # Your search results here
        }
    }

    # Create attributions
    attr_id = attribution_manager.add_attribution(
        attribution=SourceAttribution(
            source="Your Source",
            api_endpoint="/api/endpoint",
            confidence=ConfidenceLevel.HIGH,
            relevance_score=95.0,
            tool_used="my_search_tool"
        )
    )

    # Map response keys to attribution IDs
    attribution_map = {
        "query": attr_id,
        "results": attr_id
    }

    # Prepare response for MCP with attribution included in content
    return source_tracker.prepare_mcp_response(response_data, attribution_map)
```

### How It Works

The `prepare_mcp_response` method does the following:

1. Prepares the response with all attribution information
2. Formats the attribution information as markdown
3. Adds the formatted attribution to the response content
4. Returns the response with the attribution included

This ensures that when the LLM receives the response, it can see and present the attribution information to the user.

### Example Output

When using a tool with source attribution through MCP, the response will include attribution information like this:

```
# Search Results

Here are the search results for "fireball":

- Fireball (3rd-level evocation)
- Delayed Blast Fireball (7th-level evocation)

---

**Source Information:**

### Player's Handbook

* **Confidence:** High
* **APIs:**
  * /api/spells/fireball
* **Pages:** 241

---

**Tools Used:**

* **search_spells** (search)
  * Execution time: 0.123s
```

This provides transparency about where the information comes from, how confident the system is in its accuracy, and which tools were used to retrieve it.

## Benefits

- **Transparency**: Users can see where information comes from
- **Trust**: Confidence levels help users gauge reliability
- **Traceability**: Tool usage tracking shows how information was retrieved
- **Completeness**: Comprehensive attribution for all data points
- **Clarity**: Clear formatting of citations and attributions
