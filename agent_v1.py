# ============================================================
# File:     agent_v1.py
# Author:   Raghav Anand
# Created:  2026-11-19 (updated Day 5: second tool with an input)
# Project:  Private AI Lab - Week 1, Days 4-5
# Purpose:  Tool-using agent with TWO tools. The local model
#           chooses which tool to call and what input to pass.
#           get_stock_price uses FAKE demo data (offline).
# Runs:     100% locally through Ollama. No internet, no cost.
# ============================================================

from datetime import datetime
from ollama import chat

MODEL = "qwen3"
MAX_STEPS = 5   # Safety limit on model calls per question

# FAKE prices for learning only. Not real market data.
DEMO_PRICES = {"COST": 950.25, "AAPL": 230.10, "MSFT": 455.80}


# --- Tool 1: no inputs ---------------------------------------
def get_current_time() -> str:
    """
    Get the current local date and time on this computer.

    Returns:
        The current date and time as readable text.
    """
    return datetime.now().strftime("%A, %B %d, %Y, %I:%M %p")


# --- Tool 2: takes one input (a ticker) ----------------------
def get_stock_price(ticker: str) -> str:
    """
    Get the latest stock price for a company by its ticker symbol.

    Args:
        ticker: The stock ticker symbol, for example COST for Costco.

    Returns:
        The price as text, or an error if the ticker is unknown.
    """
    symbol = ticker.strip().upper()           # Clean up the model's input: " cost " -> "COST"
    if symbol not in DEMO_PRICES:
        return f"Error: no price data for ticker '{symbol}'."
    return f"{symbol}: ${DEMO_PRICES[symbol]:.2f} (DEMO DATA, not real)"


# Allow-list: the ONLY tools our code will run.
AVAILABLE_TOOLS = {
    "get_current_time": get_current_time,
    "get_stock_price": get_stock_price,
}


def run_agent(question):
    print("=" * 60)
    print(f"QUESTION: {question}")
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use tools for live information. If a tool returns an error, say you don't have that data. Be concise."},
        {"role": "user", "content": question},
    ]
    used_tools = False

    for step in range(1, MAX_STEPS + 1):
        response = chat(
            model=MODEL,
            messages=messages,
            tools=[get_current_time, get_stock_price],   # Two tools on the menu now
            think=False,
        )
        messages.append(response.message)

        tool_calls = response.message.tool_calls
        if not tool_calls:
            how = "after using tools" if used_tools else "directly, no tools"
            print(f"[step {step}] Model answered {how}.")
            print(f"ANSWER: {response.message.content.strip()}\n")
            return

        used_tools = True
        for call in tool_calls:
            name = call.function.name
            args = call.function.arguments or {}     # e.g. {"ticker": "COST"}
            print(f"[step {step}] Model asked to call: {name}({args})")

            tool_function = AVAILABLE_TOOLS.get(name)
            result = tool_function(**args) if tool_function else f"Error: unknown tool '{name}'."
            print(f"[step {step}] Tool returned: {result}")
            messages.append({"role": "tool", "content": str(result), "tool_name": name})

    print(f"Stopped: reached the {MAX_STEPS}-step limit.\n")


if __name__ == "__main__":
    run_agent("What is Costco's stock price?")                     # Must turn "Costco" into "COST"
    run_agent("What is Tesla's stock price?")                      # Not in our data: does it admit it?
    run_agent("What is today's date and Costco's stock price?")    # Needs BOTH tools