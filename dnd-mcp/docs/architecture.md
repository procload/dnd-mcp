Below is an engineering implementation plan for building a FastMCP-based server that integrates resources from the D&D 5e API (`https://www.dnd5eapi.co`) with tools and prompts. This plan leverages our previous discussions, focusing on exposing API data (e.g., `/api/equipment/wand`) as resources, adding tools for enhanced functionality, and including prompts for LLM guidance. The goal is to create a robust MCP server that allows an LLM to discover, explore, and interact with D&D 5e data effectively.

---

# Engineering Implementation Plan: FastMCP Server for D&D 5e API

## Objective

Develop a FastMCP server that exposes D&D 5e API resources (e.g., equipment, races), provides tools for querying and filtering, and includes prompts to guide LLM interactions, ensuring discoverability and usability.

## Scope

- **Resources**: Expose API categories and items (e.g., `/api/equipment/wand`) with descriptive metadata.
- **Tools**: Add functionality like searching or filtering (e.g., by cost or level).
- **Prompts**: Provide templates for LLM tasks (e.g., describing items).
- **Target API**: `https://www.dnd5eapi.co`.

## Requirements

### Functional

1. **Resources**:
   - List all API categories (e.g., `equipment`, `races`).
   - List items within a category with dynamic descriptions.
   - Provide detailed data for specific items.
2. **Tools**:
   - Search equipment by cost (e.g., items ≤ 10 gp).
   - Filter items by relevant attributes (e.g., spell level, if applicable).
3. **Prompts**:
   - Generate descriptive templates for items (e.g., "Describe Wand").
4. **Discovery**:
   - LLM can find resources, tools, and prompts via `mcp.listResources`, `mcp.listTools`, `prompts/list`.

### Non-Functional

- **Performance**: Cache API responses (1-hour TTL) to reduce latency.
- **Scalability**: Handle all API categories dynamically.
- **Reliability**: Graceful error handling for invalid inputs or API failures.

## Design

### Architecture

- **Framework**: FastMCP (`github.com/jlowin/fastmcp`) with Python.
- **Server**: Single `DnDAPIServer` class, hosted on `localhost:5000`.
- **Data Source**: `https://www.dnd5eapi.co/api/` (root) and sub-endpoints.
- **Components**:
  - **Resources**: `@mcp.resource` for categories, items, and details.
  - **Tools**: `@mcp.tool` for search/filter operations.
  - **Prompts**: `@mcp.prompt` for LLM templates.
  - **Caching**: In-memory dictionary with TTL.

### Endpoints

1. **Resources**:
   - `categories`: List all API categories with descriptions.
   - `items`: List items in a category (e.g., equipment) with metadata.
   - `item_details`: Fetch full data for an item URI.
2. **Tools**:
   - `search_equipment_by_cost`: Find equipment by max cost.
3. **Prompts**:
   - `describe_item`: Template for item descriptions.

### Schemas

- **Resources**:
  ```json
  [
    {
      "uri": "string",
      "name": "string",
      "mime_type": "string",
      "description": "string"
    }
  ]
  ```
- **Tools**:
  ```json
  {
    "name": "string",
    "description": "string",
    "parameters": [
      { "name": "string", "type": "string", "description": "string" }
    ]
  }
  ```
- **Prompts**:
  ```json
  {"prompts": [{"name": "string", "description": "string", "arguments": [{"name": "string", "required": bool}]}]}
  ```

## Implementation Plan

### Phase 1: Setup and Prerequisites

- **Duration**: 1 day
- **Tasks**:
  1. Install FastMCP: `pip install fastmcp` (or clone from GitHub).
  2. Install dependencies: `pip install requests`.
  3. Create project structure:
     ```
     dnd_fastmcp/
     ├── server.py
     ├── requirements.txt
     ```
  4. Test API connectivity: `curl https://www.dnd5eapi.co/api/equipment/wand`.

### Phase 2: Core Server and Resources

- **Duration**: 2 days
- **Tasks**:
  1. **Initialize Server**:
     - Use `FastMCP("DnDAPIServer")` and define `DnDAPIServer` class.
  2. **Implement Caching**:
     - Add `_get_cached` and `_cache_data` methods with 1-hour TTL.
  3. **Define Resources**:
     - `@mcp.resource("categories")`: Fetch `/api/` and list categories.
     - `@mcp.resource("items")`: Fetch `/api/{category}` with dynamic descriptions (e.g., for "Wand").
     - `@mcp.resource("item_details")`: Fetch item URI details (e.g., `/api/equipment/wand`).
  4. **Test**:
     - `mcp.listResources` → Verify "equipment" and "Wand" appear with descriptions.
     - `mcp.readResource` → Confirm Wand details match API.

### Phase 3: Add Tools

- **Duration**: 1 day
- **Tasks**:
  1. **Define Tool**:
     - `@mcp.tool("search_equipment_by_cost")`: Search equipment by max cost.
     - Parameters: `max_cost` (integer).
  2. **Implement Logic**:
     - Fetch `/api/equipment`, filter items where `cost.quantity` ≤ `max_cost`.
  3. **Test**:
     - `mcp.callTool("search_equipment_by_cost", {"max_cost": 10})` → Expect "Wand" (10 gp) in results.

### Phase 4: Add Prompts

- **Duration**: 1 day
- **Tasks**:
  1. **Define Prompt**:
     - `@mcp.prompt("describe_item")`: Template for item descriptions.
     - Parameter: `item_name` (string).
  2. **Implement Logic**:
     - Return a string like "Describe the D&D 5e item '{item_name}'...".
  3. **Test**:
     - `prompts/list` → Verify "describe_item" appears.
     - `prompts/get("describe_item", {"item_name": "Wand"})` → Check response.

### Phase 5: Integration and Validation

- **Duration**: 1 day
- **Tasks**:
  1. **End-to-End Test**:
     - LLM flow: List categories → List equipment → Describe "Wand" → Search by cost.
  2. **Error Handling**:
     - Add checks for invalid categories, URIs, or API failures.
  3. **Performance**:
     - Confirm caching reduces API calls (e.g., second "Wand" fetch is instant).

## Implementation Code

```python
# server.py
import requests
from fastmcp import FastMCP
from datetime import datetime, timedelta
from typing import List, Dict, Any

mcp = FastMCP("DnDAPIServer", host="localhost", port=5000)

class DnDAPIServer:
    def __init__(self):
        self.base_url = "https://www.dnd5eapi.co"
        self.cache = {}
        self.cache_ttl = timedelta(hours=1)
        self.categories = requests.get(f"{self.base_url}/api/").json()
        self.category_descriptions = {
            "equipment": "Gear and items for adventuring in D&D 5e",
            "races": "Playable races with proficiencies and traits",
        }

    def _get_cached(self, uri: str) -> str | None:
        if uri in self.cache:
            data, timestamp = self.cache[uri]
            if datetime.now() - timestamp < self.cache_ttl:
                return data
        return None

    def _cache_data(self, uri: str, data: str):
        self.cache[uri] = (data, datetime.now())

    @mcp.resource(name="categories", description="Available D&D 5e resource categories")
    def get_categories(self) -> List[Dict[str, str]]:
        return [
            {
                "name": key,
                "description": self.category_descriptions.get(key, f"List of {key} from D&D 5e"),
                "uri": f"{self.base_url}{value}"
            }
            for key, value in self.categories.items()
        ]

    @mcp.resource(name="items", description="Items from a D&D 5e category with details")
    def get_items(self, category: str, max_items: int = 10) -> List[Dict[str, str]]:
        if category not in self.categories:
            raise ValueError("Invalid category.")
        response = requests.get(f"{self.base_url}/api/{category}").json()
        items = response["results"][:max_items]
        result = []
        for item in items:
            uri = f"{self.base_url}{item['url']}"
            item_data = self._get_cached(uri)
            if not item_data:
                item_data = str(requests.get(uri).json())
                self._cache_data(uri, item_data)
            item_dict = eval(item_data)
            desc = item_dict.get("desc", ["No description"])[0] if isinstance(item_dict.get("desc"), list) else item_dict.get("desc", "No description")
            if category == "equipment" and "equipment_category" in item_dict:
                desc = f"{desc[:50]}... Category: {item_dict['equipment_category']['name']}"
            desc = desc[:100] + "..." if len(desc) > 100 else desc
            result.append({
                "uri": uri,
                "name": item["name"],
                "mime_type": "application/json",
                "description": desc
            })
        return result

    @mcp.resource(name="item_details", description="Detailed data for a specific item")
    def get_item_details(self, uri: str) -> Dict[str, str]:
        cached_data = self._get_cached(uri)
        if cached_data:
            return {"contents": cached_data}
        response = requests.get(uri).json()
        data = str(response)
        self._cache_data(uri, data)
        return {"contents": data}

    @mcp.tool(
        name="search_equipment_by_cost",
        description="Search equipment by maximum cost in gold pieces",
        parameters=[
            {"name": "max_cost", "type": "integer", "description": "Maximum cost in gp"}
        ]
    )
    def search_equipment_by_cost(self, max_cost: int) -> List[Dict[str, Any]]:
        response = requests.get(f"{self.base_url}/api/equipment").json()
        items = response["results"]
        filtered = []
        for item in items:
            uri = f"{self.base_url}{item['url']}"
            item_data = self._get_cached(uri)
            if not item_data:
                item_data = str(requests.get(uri).json())
                self._cache_data(uri, item_data)
            item_dict = eval(item_data)
            if "cost" in item_dict and item_dict["cost"]["unit"] == "gp" and item_dict["cost"]["quantity"] <= max_cost:
                desc = item_dict.get("desc", ["No description"])[0][:100] + "..."
                filtered.append({
                    "uri": uri,
                    "name": item_dict["name"],
                    "description": desc,
                    "cost": item_dict["cost"]["quantity"]
                })
        return filtered

    @mcp.prompt()
    def describe_item(self, item_name: str) -> str:
        """Generate a description for a D&D 5e item."""
        return f"Provide a detailed description of the D&D 5e item '{item_name}' based on its properties, usage, and lore."

server = DnDAPIServer()

if __name__ == "__main__":
    mcp.run()
```

### requirements.txt

```
fastmcp
requests
```

## Deployment

- **Run**: `python server.py`
- **Test**:
  - `curl -X POST -d '{"jsonrpc": "2.0", "method": "mcp.listResources", "params": {"resource": "items", "category": "equipment"}, "id": 1}' http://localhost:5000`
  - `curl -X POST -d '{"jsonrpc": "2.0", "method": "mcp.callTool", "params": {"tool": "search_equipment_by_cost", "parameters": {"max_cost": 10}}, "id": 2}' http://localhost:5000`

## Validation

- **Resources**: "Wand" appears in `get_items("equipment")` with description and in `get_item_details`.
- **Tools**: `search_equipment_by_cost(10)` returns "Wand" (10 gp).
- **Prompts**: `describe_item("Wand")` generates a usable template.

## Timeline

- **Total**: 6 days (Mar 10–15, 2025).
- **Milestones**: Setup (Mar 10), Resources (Mar 11–12), Tools (Mar 13), Prompts (Mar 14), Validation (Mar 15).

## Risks & Mitigations

- **API Changes**: Monitor `dnd5eapi.co` for updates; use caching to buffer.
- **Performance**: Limit `max_items` to 10; scale cache if needed.

---

This plan ensures the LLM can explore D&D 5e resources (like `/api/equipment/wand`), filter them with tools, and describe them via prompts. Ready to tweak or proceed? Let me know!
