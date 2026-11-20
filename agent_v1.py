# ============================================================
# File:     agent_v1.py
# Author:   Raghav Anand
# Created:  2026-11-19
# Updated:  Week 1 Day 5 - added second tool (get_stock_price)
#           Week 2 Day 1 - run_agent() now RETURNS results for evals.py
# Project:  Private AI Lab
# Purpose:  Tool-using agent with TWO tools. The local model
#           chooses which tool to call and what input to pass.
#           Shows the full tool loop: model asks -> our code runs
#           the tool -> result goes back -> model answers.
#           get_stock_price uses FAKE demo data (offline).
# Runs:     100% locally through Ollama. No internet, no cost.
# ============================================================

# --- Imports ------------------------------------------------
from datetime import datetime   # Python's built-in date/time tools
from ollama import chat         # Official Ollama Python library

# --- Settings -----------------------------------------------
DEFAULT_MODEL = "qwen3"   # Used when no model is passed in
MAX_STEPS = 5             # Safety limit: the most model calls allowed per question (a first guardrail)

# FAKE prices for learning only. Not real market data.
# Lesson from Day 5: the model trusts whatever a tool returns,
# so a tool's data must be correct and clearly labeled.
DEMO_PRICES = {"COST": 950.25, "AAPL": 230.10, "MSFT": 455.80}


# --- Tool 1: no inputs ---------------------------------------
# A tool is just a normal Python function. The Ollama library reads its
# NAME, its type hints and its docstring (the text in triple quotes) to
# describe it to the model. Lesson from Day 4: the name matters as much
# as the docstring; a clear name like get_current_time does a lot of work.
def get_current_time() -> str:
    """
    Get the current local date and time on this computer.

    Returns:
        The current date and time as readable text.
    """
    return datetime.now().strftime("%A, %B %d, %Y, %I:%M %p")


# --- Tool 2: takes one input (a ticker) ----------------------
# The "Args:" section of the docstring tells the model what to pass in.
# The model must translate a company name ("Costco") into a ticker ("COST").
def get_stock_price(ticker: str) -> str:
    """
    Get the latest stock price for a company by its ticker symbol.

    Args:
        ticker: The stock ticker symbol, for example COST for Costco.

    Returns:
        The price as text, or an error if the ticker is unknown.
    """
    symbol = ticker.strip().upper()           # Clean up the model's input: " cost " -> "COST". Never trust model input as-is.
    if symbol not in DEMO_PRICES:
        # Return an error STRING (not a crash). The model reads it and should
        # admit it doesn't have the data, instead of inventing a price.
        return f"Error: no price data for ticker '{symbol}'."
    return f"{symbol}: ${DEMO_PRICES[symbol]:.2f} (DEMO DATA, not real)"


# --- Allow-list ----------------------------------------------
# A lookup table: tool name (text) -> the real Python function.
# Our code runs ONLY tools on this list. If the model invents a tool
# name (hallucination or prompt injection), it gets an error, not execution.
# This is "least privilege".
AVAILABLE_TOOLS = {
    "get_current_time": get_current_time,
    "get_stock_price": get_stock_price,
}


# --- The agent loop -----------------------------------------
def run_agent(question, model=DEFAULT_MODEL, think=False, verbose=True):
    """
    Ask one question and let the model use tools until it has an answer.

    Args:
        question: The user's question.
        model:    Which Ollama model to use (e.g. "qwen3", "llama3.2").
        think:    True/False for models with a thinking mode; None for models without one.
        verbose:  True = print every step (good for learning);
                  False = stay quiet (good for evals.py, which runs many questions).

    Returns:
        A dictionary with:
          "answer":       the model's final answer text
          "tools_called": list of tool names the model asked for, in order
          "steps":        how many model calls it took
        (NEW in Week 2: returning results lets evals.py score the agent.)
    """
    # The conversation so far. It grows as the loop runs.
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use tools for live information. If a tool returns an error, say you don't have that data. Be concise."},
        {"role": "user", "content": question},
    ]
    tools_called = []   # Record of every tool the model asked for (evals check this)

    # Only include the 'think' option for models that support it.
    # Sending it to a model without thinking (like llama3.2) could be rejected.
    extra = {} if think is None else {"think": think}

    if verbose:
        print("=" * 60)
        print(f"QUESTION: {question}  [model: {model}]")

    # The agent loop: think -> act -> observe, at most MAX_STEPS times.
    for step in range(1, MAX_STEPS + 1):
        # 1. Send the conversation AND the tool menu to the model.
        response = chat(
            model=model,
            messages=messages,
            tools=[get_current_time, get_stock_price],   # The "menu": the library turns these functions into tool descriptions
            **extra,                                      # Adds think=... only when it applies
        )

        # Always add the model's reply (including any tool request) to the history.
        messages.append(response.message)

        # 2. Did the model ask to use a tool?
        tool_calls = response.message.tool_calls
        if not tool_calls:
            # No tool request means this is the final answer. Done.
            answer = (response.message.content or "").strip()
            if verbose:
                how = "after using tools" if tools_called else "directly, no tools"
                print(f"[step {step}] Model answered {how}.")
                print(f"ANSWER: {answer}\n")
            return {"answer": answer, "tools_called": tools_called, "steps": step}

        # 3. The model asked for one or more tools (it can ask for several at once).
        for call in tool_calls:
            name = call.function.name
            args = call.function.arguments or {}     # Inputs the model wants to pass, e.g. {"ticker": "COST"}
            tools_called.append(name)

            tool_function = AVAILABLE_TOOLS.get(name)
            # Run the tool ONLY if it's on the allow-list.
            result = tool_function(**args) if tool_function else f"Error: unknown tool '{name}'."

            if verbose:
                print(f"[step {step}] Model asked to call: {name}({args})")
                print(f"[step {step}] Tool returned: {result}")

            # 4. Send the tool's result back to the model as a 'tool' message.
            #    'tool' is a message role, like 'system', 'user' and 'assistant'.
            messages.append({"role": "tool", "content": str(result), "tool_name": name})

        # Loop again: the model now sees the tool results and can answer.

    # Hit the safety limit without a final answer.
    if verbose:
        print(f"Stopped: reached the {MAX_STEPS}-step limit.\n")
    return {"answer": "", "tools_called": tools_called, "steps": MAX_STEPS}


# --- Demo: runs only when this file is run directly -----------
# "if __name__ == '__main__'" means: run this part only for
# `python3 agent_v1.py`, NOT when another file (like evals.py) imports it.
if __name__ == "__main__":
    run_agent("What is Costco's stock price?")                     # Must turn "Costco" into "COST"
    run_agent("What is Tesla's stock price?")                      # Not in our data: does it admit it?
    run_agent("What is today's date and Costco's stock price?")    # Needs BOTH tools