# D&D Knowledge Navigator - Usage Guide for Claude Desktop

This guide will help you get the most out of the D&D Knowledge Navigator when using it with Claude Desktop.

## Getting Started

The D&D Knowledge Navigator is a specialized tool that allows Claude to access official D&D 5e information. When properly connected, Claude can search for spells, monsters, equipment, classes, and more from the official D&D 5e SRD (System Reference Document).

### Prerequisites

1. Claude Desktop client installed
2. D&D Knowledge Navigator server running
3. Claude Desktop configured to connect to the server

## Basic Usage

When the D&D Knowledge Navigator is connected, you can ask Claude questions about D&D 5e content. Claude will use the appropriate tools to search for and retrieve information from the official D&D 5e API.

### Example Queries

Here are some example queries you can try:

#### Spell Information

- "Tell me about the Fireball spell"
- "What level is Counterspell?"
- "How does Magic Missile work?"
- "What are the components for Wish?"
- "Show me all 3rd level Wizard spells"

#### Monster Information

- "What is the AC of an Adult Red Dragon?"
- "How many hit points does a Goblin have?"
- "What are the abilities of a Beholder?"
- "Show me monsters with challenge rating 5"
- "What legendary actions can an Ancient Black Dragon take?"

#### Class Information

- "What are the features of a level 5 Barbarian?"
- "How does Sneak Attack work for Rogues?"
- "What spells can a Paladin cast?"
- "Tell me about the Fighter's Action Surge"
- "What equipment does a Cleric start with?"

#### Equipment and Items

- "How much damage does a Greatsword do?"
- "What are the properties of Plate Armor?"
- "Tell me about the Bag of Holding"
- "What weapons can a Monk use?"
- "How much does a Potion of Healing cost?"

#### Rules and Mechanics

- "Explain how death saving throws work"
- "What are the conditions for being stunned?"
- "How does advantage work?"
- "What is passive perception?"
- "Explain the rules for long rests"

## Advanced Features

### Verification of D&D Information

You can ask Claude to verify specific D&D statements:

- "Verify if Fireball is a 3rd level spell"
- "Is it true that dragons have immunity to their breath weapon damage type?"
- "Verify if Barbarians can cast spells while raging"

### API Health Check

You can check the status of the D&D 5e API:

- "Check if the D&D API is working"
- "Is the monster data available in the API?"
- "Can you check the health of the D&D database?"

## Understanding Responses

### Source Attribution

All information provided by the D&D Knowledge Navigator includes source attribution, which tells you:

- The source of the information (e.g., D&D 5e API)
- The specific API endpoint used
- A confidence level indicating how reliable the information is
- Relevance score showing how well it matches your query

Example attribution:

```
Source: D&D 5e API
Endpoint: /api/spells/fireball
Confidence: High (Direct API match)
Relevance: 0.95
```

### Formatted Content

The D&D Knowledge Navigator formats content to make it easy to read:

- Monster stat blocks with organized attributes and abilities
- Spell descriptions with formatted components and effects
- Equipment details with organized properties

## Troubleshooting

### Common Issues

#### No Results Found

If Claude reports that no results were found:

1. **Check your spelling**: The D&D Knowledge Navigator includes fuzzy matching, but very misspelled terms might not be recognized.
2. **Try alternative terms**: Use common D&D terminology (e.g., "AC" instead of "armor class").
3. **Be more specific**: Instead of "dragon," try "red dragon" or "adult red dragon."
4. **Check if the content is in the SRD**: Not all D&D content is available in the free SRD.

#### Slow Responses

If responses are taking a long time:

1. **Check your internet connection**: The server needs to communicate with the D&D 5e API.
2. **Verify server status**: Make sure the D&D Knowledge Navigator server is running.
3. **Consider the query complexity**: Complex queries that search multiple categories may take longer.

#### Incorrect Information

If you believe the information provided is incorrect:

1. **Ask for verification**: Use the verification tool to double-check the information.
2. **Check the source attribution**: Lower confidence levels indicate less certain information.
3. **Request clarification**: Ask Claude to explain where the information came from.

### API Limitations

The D&D Knowledge Navigator uses the official D&D 5e API, which has some limitations:

1. **SRD Content Only**: Only content from the SRD is available, not all D&D 5e content.
2. **No Homebrew**: Custom or homebrew content is not included.
3. **No Images**: The API does not provide images for monsters, items, etc.

## Tips for Better Results

1. **Be specific**: Ask about specific spells, monsters, or rules rather than broad categories.
2. **Use D&D terminology**: Using terms like "AC," "HP," or "CR" helps the system understand your query.
3. **One question at a time**: For best results, focus on one topic per query.
4. **Check attribution**: Pay attention to the confidence level in the attribution to gauge reliability.
5. **Use verification**: When in doubt, ask Claude to verify information against the official API.

## Example Workflows

### Character Building

1. "What are the features of a Wood Elf?"
2. "Show me the Ranger class abilities"
3. "What equipment does a Ranger start with?"
4. "Tell me about the Animal Handling skill"

### Combat Reference

1. "How does the Dodge action work?"
2. "What are the rules for cover?"
3. "Explain opportunity attacks"
4. "How does the Stunned condition affect a creature?"

### Spell Research

1. "Show me all Wizard cantrips"
2. "What concentration spells are available to Druids?"
3. "Tell me about area of effect spells"
4. "How does the Counterspell spell work?"
