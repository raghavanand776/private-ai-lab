# ============================================================
# File:     hello_server.py
# Author:   Raghav Anand
# Created:  2026-11-21
# Project:  Private AI Lab - Week 2, Day 2
# Purpose:  First MCP server. Shows MCP's three building blocks:
#             - a TOOL     (a function the AI can run)
#             - a RESOURCE (data the AI can read)
#             - a PROMPT   (a reusable instruction template)
#           Tested by hand in the MCP Inspector (no AI model yet).
# SDK:      mcp 2.3.0 (v2, speaks the 2026-07-28 MCP spec)
# ============================================================

# In SDK v2 the server class is MCPServer.
# (Older v1 tutorials use "from mcp.server.fastmcp import FastMCP" - that import no longer exists in v2.)
from mcp.server import MCPServer

# Create the server and give it a name. Clients see this name.
mcp = MCPServer("Hello Lab Server")


# --- 1. TOOL: something the AI can RUN ------------------------
# @mcp.tool() registers the function below as a tool.
# Like Week 1, the SDK reads the function name, type hints (a: int)
# and docstring to describe the tool to any client.
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two whole numbers and return the sum."""
    return a + b


# --- 2. RESOURCE: data the AI can READ ------------------------
# A resource is addressed by a URI, like a web address.
# "greeting://{name}" is a template: greeting://Raghav fills name="Raghav".
# Resources are for reading data, not for doing actions.
@mcp.resource("greeting://{name}")
def greeting(name: str) -> str:
    """Return a friendly greeting for the given name."""
    return f"Hello, {name}! Welcome to the Private AI Lab."


# --- 3. PROMPT: a reusable instruction TEMPLATE ----------------
# A prompt is a ready-made message the user or app can pick,
# so everyone asks the model in the same, well-tested way.
@mcp.prompt()
def explain_simply(topic: str) -> str:
    """A prompt that asks the model to explain a topic to a beginner."""
    return f"Explain {topic} to someone new to tech, in 3 short bullet points with one real-world example."