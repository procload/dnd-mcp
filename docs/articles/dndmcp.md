Tired: Endless debates about which AI model hallucinates less.
Wired: Building systems that give AI models access to accurate, real-time data.
The Model Context Protocol (MCP) is worth looking at. It's not about ditching RAG - that still is great for large static datasets - but about adding live data capabilities where it makes sense.
I spent a weekend hooking Claude up to the D&D 5e API, so it can pull accurate monster stats, spell details, and magical item properties on demand. The code tracks attribution for every information source, enhances queries with D&D-specific processing, and gives Claude a verification tool to fact-check itself.
One of the best parts is the ability for developers to add swap data sources without changing application architecture.
MCP can be thought of as an architecture as similar to HTTP—a standard protocol that lets AI developers build applications with outside context or tools in a standardized way.

What's really cool isn't the technical implementation, but the shift in how we can approach AI accessing knowledge in large, dynamic systems.

The possibilities from here get even more interesting—beyond pulling API information, we can use MCP to control scriptable applications like Blender, Unity or Unreal Engine. What happens when generative AI can directly manipulate creative tools rather than just suggesting how to use them?

Check out my full write-up on implementing MCP for D&D.

## The Model Context Protocol: A New Paradigm for AI Applications

The model context protocol (MCP) represents a significant shift in how AI applications access and interact with external data and actions. Unlike traditional approaches, MCP establishes a two-way communication channel that makes it dramatically easier for AI models to work with the specific data they need.

MCP follows a client-server architecture, with each MCP server functioning as a gateway to a particular data source or capability. One server might interact with the Dungeons and Dragons API for accurate game information, while another might connect with Google Drive or Dropbox to retrieve existing character sheets. The MCP server handles authentication, data retrieval, and returns information in a format the AI model can readily consume. This allows an AI to access fresh, updated context that's not part of its training data. Beyond just pulling information, MCP servers can take actions on behalf of an LLM, such as writing new data to a database.

One of the biggest advantages over specialized RAG applications is the clear separation between LLM logic and the data sources or logic living in the servers. Developers can add or swap data sources using MCP without changing the underlying architecture of their LLM application.

### MCP vs. RAG: A Critical Distinction

Unlike RAG, which pre-indexes documents into embeddings stored in vector databases for later retrieval, MCP enables real-time querying of live data sources without pre-processing or embedding generation. RAG is inherently static and limited to its indexed information, while MCP is dynamic and can integrate with APIs, databases, or tools on demand. That said, RAG might still be more efficient for large, unchanging datasets, while MCP truly shines in scenarios requiring up-to-the-minute data or complex actions.

A community is rapidly forming around this shared protocol, allowing AI developers to mix and match pre-built MCP servers without custom API development.

The real breakthrough here is enabling MCP servers to easily integrate with various data sources without rewriting the logic for fetching and delivering data to the LLM. In theory, if an MCP server exists for a data source, we can use it off-the-shelf without writing custom code for manual information retrieval.

MCP also allows applications to switch underlying AI models without changing application logic. Claude currently supports this standard, but since it's open, other models can easily adopt it. This flexibility is particularly valuable for enterprises starting with frontier models like Claude but planning to transition to their own hosted solutions after proving their concept.

There's a growing ecosystem of open source contributions creating MCP connections for everything from Slack to Jira. This ecosystem should significantly reduce development time for AI applications connecting to third-party data sources—developers can use these integrations off-the-shelf rather than building the plumbing themselves. It's similar to NPM and package management in the JavaScript world.

And because an MCP server can both read data and take actions, it simplifies application logic. An application might handle a user request to find information on an item and then update its description using the same MCP server. The traditional approach would require fetching information via RAG and then separately updating the database through another mechanism.

Think of MCP architecture as similar to HTTP—a standard protocol that allows AI developers to build applications with outside context or tools in a standardized way, without getting bogged down in integration work or one-off solutions.

## Implementation Experience

I started by following Anthropic's [getting started guide](https://modelcontextprotocol.io/quickstart/server) to fetch weather results from an API using the Claude Mac desktop client. I immediately hit a snag when configuring the `claude_desktop_config.json`—it couldn't find the package manager, uv. Easy fix: specify the absolute path in the config file:

```json
{
  "mcpServers": {
    "weather": {
      "command": "/Users/USERPATH/.local/bin/uv",
      "args": [
        "--directory",
        "/Users/ryanmerrill/Sites/weather",
        "run",
        "weather.py"
      ]
    }
  }
}
```

After sorting that out, I wanted to try something more interesting: Dungeons and Dragons.

A fun use case I'm thinking about building is configuring Claude's desktop app to pull data from the Dungeons and Dragons API in real time, ensuring we're using proper rules rather than relying on whatever made it into the training data.

There's a free [D&D API](https://5e-bits.github.io/docs/) that works great for this experiment. Claude handles MCP interactions beautifully. Anthropic [suggests using this text file](https://modelcontextprotocol.io/llms-full.txt) in your LLM-powered editor to provide context on MCP best practices. Working in Cursor, I quickly added tools for looking up monsters and magical items.

The MCP architecture also lets us define custom prompts on the server for the client to use. While the UX in the Claude desktop app needs some refinement, it's not hard to see the potential.

I created a prompt that generates new D&D adventures populated with appropriate monsters, magical items, and settings pulled directly from the API. This means we're relying on accurate, up-to-date information rather than whatever knowledge the LLM happened to absorb during training.

Here's an example prompt implementation:

```python
types.Prompt(
    name="adventure-hook",
    description="Generate a D&D adventure hook",
    arguments=[
        types.PromptArgument(
            name="setting",
            description="The adventure setting (e.g., dungeon, forest)",
            required=True
        ),
        types.PromptArgument(
            name="level_range",
            description="The level range (e.g., 1-5, 5-10)",
            required=True
        ),
        types.PromptArgument(
            name="theme",
            description="The adventure theme (optional)",
            required=False
        )
    ]
)
if name == "adventure-hook":
    setting = arguments.get("setting", "") if arguments else ""
    level_range = arguments.get("level_range", "") if arguments else ""
    theme = arguments.get("theme", "") if arguments else ""

    prompt_text = f"Create a D&D adventure hook set in a {setting} for character levels {level_range}"
    if theme:
        prompt_text += f" with a {theme} theme"
    prompt_text += "."

    prompt_text += "\n\nInclude:\n1. A compelling hook to draw players in\n2. Key NPCs involved\n3. Potential challenges and encounters\n4. Possible rewards"

    return types.GetPromptResult(
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=prompt_text
                )
            )
        ]
    )
```

## D&D Knowledge Navigator: A Practical MCP Implementation

Building on this foundation, I expanded the prototype into a comprehensive D&D Knowledge Navigator with help from Cursor and Claude 3.7 that showcases the full potential of MCP architecture. This project demonstrates how MCP can enhance AI interactions with specialized knowledge domains.

### Core Tools and Features

Our D&D Knowledge Navigator implements several MCP tools that Claude can use to access accurate D&D information:

1. **Search Across Categories**: The `search_all_categories` tool allows Claude to search for any D&D term across spells, monsters, equipment, classes, and more:

```python
@app.tool()
@track_tool_usage(ToolCategory.SEARCH)
def search_all_categories(query: str) -> Dict[str, Any]:
    """
    Search across all available D&D categories for the given query.

    Args:
        query: The search term to look for across all categories

    Returns:
        Dictionary containing search results organized by category
    """
    # Clear previous attributions for this tool
    source_tracker.clear_tool_usages()

    # Enhance the query with D&D-specific processing
    enhanced_query, enhancements = enhance_query(query)

    # Search across categories with the enhanced query
    # ...

    # Add attribution for the search results
    attribution_id = attribution_manager.add_attribution(
        source="D&D 5e API",
        api_endpoint=f"/api/search?query={enhanced_query}",
        confidence=ConfidenceLevel.HIGH,
        relevance_score=0.95,
        tool_used="search_all_categories"
    )

    # Prepare the response with proper attribution
    return source_tracker.prepare_mcp_response(
        content=response_content,
        attribution_map=attribution_map
    )
```

2. **Verification Tool**: The `verify_with_api` tool allows Claude to fact-check D&D statements against the official API:

```python
@app.tool()
@track_tool_usage(ToolCategory.SEARCH)
def verify_with_api(statement: str, category: str = None) -> Dict[str, Any]:
    """
    Verify a D&D statement by checking it against the D&D 5e API.

    Args:
        statement: The statement to verify
        category: Optional category to focus the search on

    Returns:
        Dictionary containing verification results and confidence
    """
    # Implementation details...
```

3. **API Health Check**: The `check_api_health` tool ensures the D&D API is operational:

```python
@app.tool()
@track_tool_usage(ToolCategory.CONTEXT)
def check_api_health() -> Dict[str, Any]:
    """
    Check the health and status of the D&D 5e API.

    Returns:
        Dictionary containing API status and available endpoints
    """
    # Implementation details...
```

### Advanced Features

What makes our implementation particularly powerful are the additional systems we've built on top of the basic MCP framework:

1. **Source Attribution System**: Every piece of information is tracked with its source, API endpoint, confidence level, and relevance score:

```python
# Example of how attribution is added to responses
attribution_id = attribution_manager.add_attribution(
    source="D&D 5e API",
    api_endpoint="/api/spells/fireball",
    confidence=ConfidenceLevel.HIGH,
    relevance_score=0.98,
    tool_used="search_all_categories",
    metadata={"spell_level": "3rd", "school": "evocation"}
)

# The attribution appears in Claude's response like this:
"""
Source: D&D 5e API
Endpoint: /api/spells/fireball
Confidence: High (Direct API match)
Relevance: 0.98
"""
```

2. **Query Enhancement System**: We've implemented D&D-specific query processing that significantly improves search results:

```python
# The enhance_query function applies multiple enhancements
enhanced_query, enhancements = enhance_query(query)

# It handles D&D abbreviations and terminology
# "What is the AC of a dragon?" → "What is the armor class of a dragon?"

# It recognizes special D&D notation
# "How much damage does 2d6+3 do?" → Preserves "2d6+3" as a special term

# It corrects common misspellings
# "Tell me about firball" → "Tell me about fireball"

# It prioritizes relevant categories
# For "fireball", it prioritizes the "spells" category
```

Claude 3.7 and Cursor helped implement much of this—the tools, advanced features, source attribution system, search filtering, and query enhancement system. Without that help, I would have spent far more time figuring out the MCP architecture and these advanced features. Instead, I could focus on user features rather than underlying plumbing.

The possibilities from here are fascinating. Instead of just pulling API information, we can use MCP to control scriptable applications like [Blender MCP](https://x.com/aisdk/status/1899752483783671864?s=12). What about controlling game engines like Unity or Unreal Engine?

Super cool stuff.
