# D&D Knowledge Navigator - Troubleshooting Guide

This guide provides solutions for common issues you might encounter when using the D&D Knowledge Navigator with Claude Desktop.

## Connection Issues

### Claude Cannot Connect to the D&D Knowledge Navigator

**Symptoms:**

- Claude responds with "I don't have access to that tool" when you ask D&D questions
- Claude doesn't recognize D&D-specific commands

**Solutions:**

1. **Check server status:**

   - Verify that the D&D Knowledge Navigator server is running
   - Look for terminal output indicating successful startup
   - Confirm there are no error messages in the server logs

2. **Verify Claude Desktop configuration:**

   - Ensure Claude Desktop is configured to connect to the correct server URL
   - Check that the connection settings match the server's host and port
   - Restart Claude Desktop after changing connection settings

3. **Check network connectivity:**

   - Verify that your computer can reach the server (try pinging the server IP)
   - Check if any firewalls might be blocking the connection
   - Ensure the server is accessible from your network

4. **Restart components:**
   - Restart the D&D Knowledge Navigator server
   - Restart Claude Desktop
   - If using a remote server, check if it requires authentication

## Search Issues

### No Results Found

**Symptoms:**

- Claude responds with "No results found" for D&D queries
- Searches return empty results even for common D&D terms

**Solutions:**

1. **Check spelling and terminology:**

   - Verify the spelling of D&D-specific terms
   - Try using official terminology from the Player's Handbook
   - Use common abbreviations (AC, HP, etc.) which the query enhancement system can expand

2. **Refine your search:**

   - Be more specific in your query (e.g., "adult red dragon" instead of just "dragon")
   - Include category information if known (e.g., "fireball spell" instead of just "fireball")
   - Try alternative phrasings of your question

3. **Verify API availability:**

   - Ask Claude to "Check API health" to verify the D&D 5e API is operational
   - Check if specific categories are available (spells, monsters, etc.)
   - The API might be experiencing downtime or maintenance

4. **Check SRD limitations:**
   - Confirm that the content you're looking for is part of the SRD
   - Non-SRD content (certain subclasses, spells from supplements, etc.) is not available
   - Try searching for similar SRD content instead

### Slow Search Results

**Symptoms:**

- Claude takes a long time to respond to D&D queries
- Search results appear after significant delay

**Solutions:**

1. **Check internet connection:**

   - Verify your internet connection is stable and fast
   - High latency or packet loss can affect API response times

2. **Consider query complexity:**

   - Complex queries that search multiple categories take longer
   - Queries with many results require more processing time
   - Try more specific queries to reduce result size

3. **Check server load:**

   - The server might be handling multiple requests
   - High CPU or memory usage on the server can cause delays
   - Consider restarting the server if it's been running for a long time

4. **Verify caching:**
   - The cache directory might be corrupted or very large
   - Try clearing the cache directory and restarting the server
   - Ensure the cache directory has proper write permissions

## Content Issues

### Incorrect or Incomplete Information

**Symptoms:**

- Claude provides information that seems incorrect
- Responses are missing key details about D&D content

**Solutions:**

1. **Check confidence level:**

   - Look at the confidence level in the source attribution
   - Lower confidence levels indicate less certain information
   - "High" confidence means direct API match, while "Medium" or "Low" may be inferred

2. **Verify with official sources:**

   - Ask Claude to verify the information using the verification tool
   - Cross-reference with official D&D books if available
   - Check the D&D 5e SRD PDF for official content

3. **Request specific details:**

   - Ask follow-up questions about specific aspects
   - Request the complete entry if you only received partial information
   - Specify the exact details you're looking for

4. **Check for API limitations:**
   - Some information might be abbreviated in the API
   - Certain details might not be included in the SRD version
   - The API might have outdated information compared to errata

### Formatting Issues

**Symptoms:**

- Content is poorly formatted or difficult to read
- Tables, lists, or stat blocks appear broken

**Solutions:**

1. **Check template settings:**

   - Verify that templates are enabled in the configuration
   - Templates might need to be updated for certain content types
   - Some content types might not have specialized templates

2. **Try different query phrasing:**

   - Request specific formatting (e.g., "show me the stat block for...")
   - Ask for specific sections if the full content is too large
   - Break complex queries into simpler ones

3. **Check Claude's rendering:**

   - Claude Desktop might have limitations in rendering complex markdown
   - Very large responses might be truncated
   - Tables and other formatting might render differently across platforms

4. **Update templates:**
   - If you have access to the server code, check for template updates
   - Custom templates can be added for specific content types
   - Existing templates might need adjustments for better readability

## Query Enhancement Issues

### Query Enhancement Not Working

**Symptoms:**

- Misspelled terms are not being corrected
- Abbreviations are not being expanded
- Category prioritization seems incorrect

**Solutions:**

1. **Verify enhancement is enabled:**

   - Check that query enhancement is enabled in the configuration
   - All enhancement features should be enabled by default
   - Individual features (synonyms, fuzzy matching, etc.) can be toggled

2. **Check term coverage:**

   - Very uncommon or new D&D terms might not be in the synonym dictionary
   - Highly misspelled words might be beyond the fuzzy matching threshold
   - Custom or homebrew terminology won't be recognized

3. **Examine enhancement details:**

   - Look for "Query Enhancement" information in the response
   - Check which enhancements were applied to your query
   - See if the enhanced query matches what you expected

4. **Try explicit terminology:**
   - Use official terminology from the Player's Handbook
   - Spell out abbreviations if they're not being recognized
   - Be explicit about categories if prioritization seems off

## Server Issues

### Server Crashes or Errors

**Symptoms:**

- The D&D Knowledge Navigator server stops responding
- Error messages appear in the terminal
- Claude loses connection to the server

**Solutions:**

1. **Check error logs:**

   - Look for error messages in the terminal or log files
   - Note any Python exceptions or error codes
   - Check if specific queries are causing the crashes

2. **Verify dependencies:**

   - Ensure all required Python packages are installed
   - Check for version conflicts between packages
   - Try reinstalling dependencies from requirements.txt

3. **Check system resources:**

   - Monitor CPU, memory, and disk usage
   - Ensure there's enough free disk space for the cache
   - Check if other processes are competing for resources

4. **Restart and update:**
   - Restart the server to clear any memory issues
   - Pull the latest code updates if available
   - Check for known issues in the project repository

### Cache Problems

**Symptoms:**

- Repeated API calls for the same content
- Slow performance even for previously queried content
- Disk space filling up rapidly

**Solutions:**

1. **Verify cache directory:**

   - Check that the cache directory exists and has write permissions
   - Ensure the cache files are being created properly
   - Look for corrupted or incomplete cache files

2. **Clear the cache:**

   - Delete the contents of the cache directory
   - Restart the server to rebuild the cache
   - Monitor cache growth to ensure it's working properly

3. **Check cache implementation:**

   - Verify that the caching mechanism is functioning
   - Check for any error messages related to caching
   - Ensure the cache is being properly accessed

4. **Adjust cache settings:**
   - If available, adjust cache expiration settings
   - Consider limiting cache size if disk space is an issue
   - Implement cache cleanup routines if needed

## Getting Additional Help

If you continue to experience issues with the D&D Knowledge Navigator:

1. **Check documentation:**

   - Review all documentation files for additional guidance
   - Look for updates or known issues in the project repository
   - Check for FAQs or community discussions

2. **Gather information:**

   - Note the exact query that caused the issue
   - Capture any error messages or unexpected responses
   - Document the steps to reproduce the problem

3. **Contact support:**

   - Reach out to the project maintainers with detailed information
   - Share logs and reproduction steps
   - Be specific about what you expected vs. what happened

4. **Consider contributing:**
   - If you identify a bug, consider submitting a fix
   - Suggest improvements to documentation or code
   - Share your use cases to help improve the system
