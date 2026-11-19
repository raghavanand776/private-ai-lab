# ============================================================
# File:     agent_v1.py
# Author:   Raghav Anand
# Created:  2026-11-19
# Project:  Private AI Lab - Week 1, Day 4
# Purpose:  First tool-using agent. Gives the local Qwen3 model
#           one tool (get_current_time) and shows the full
#           tool loop: model asks -> our code runs the tool ->
#           result goes back -> model answers.
# Runs:     100% locally through Ollama. No internet, no cost.
# ============================================================

# --- Imports ------------------------------------------------
from datetime import datetime   # Python's built-in date/time tools
from ollama import chat         # Official Ollama Python library

# --- Settings -----------------------------------------------
MODEL = "qwen3"
MAX_STEPS = 5   # Safety limit: the most model calls allowed per question (a first guardrail)


# --- The tool -----------------------------------------------
# A tool is just a normal Python function. The Ollama library reads its
# name, its type hints and its docstring (the text in triple quotes) to
# describe it to the model. So the docstring matters: it is what the
# model reads when deciding whether to use the tool.
def get_current_time() -> str:
    """
   Get the current local date and time on this computer.

    Returns:
        The current date and time as readable text.
    """
    return datetime.now().strftime("%A, %B %d, %Y, %I:%M %p")


# A lookup table: tool name (text) -> the real Python function.
# When the model asks for a tool by name, we find it here.
AVAILABLE_TOOLS = {
    "get_current_time": get_current_time,
}


# --- The agent loop -----------------------------------------
def run_agent(question):
    """Ask one question and let the model use tools until it has an answer."""
    print("=" * 60)
    print(f"QUESTION: {question}")

    # The conversation so far. It grows as the loop runs.
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use a tool when you need live information. Be concise."},
        {"role": "user", "content": question},
    ]

    for step in range(1, MAX_STEPS + 1):
        # 1. Send the conversation AND the tool menu to the model.
        response = chat(
            model=MODEL,
            messages=messages,
            tools=[get_current_time],   # The "menu": the library turns this function into a tool description
            think=False,                # Thinking off for speed; tool calling still works
        )

        # Always add the model's reply to the conversation history.
        messages.append(response.message)

        # 2. Did the model ask to use a tool?
        tool_calls = response.message.tool_calls
        if not tool_calls:
            # No tool request means this is the final answer. Done.
            print(f"[step {step}] Model answered directly.")
            print(f"ANSWER: {response.message.content.strip()}\n")
            return

        # 3. The model asked for one or more tools. Run each one.
        for call in tool_calls:
            name = call.function.name
            args = call.function.arguments or {}   # Inputs the model wants to pass (none for this tool)
            print(f"[step {step}] Model asked to call tool: {name}({args})")

            tool_function = AVAILABLE_TOOLS.get(name)
            if tool_function is None:
                # Never run anything the model invents. Only tools on our list.
                result = f"Error: unknown tool '{name}'."
            else:
                result = tool_function(**args)

            print(f"[step {step}] Tool returned: {result}")

            # 4. Send the tool's result back to the model as a 'tool' message.
            messages.append({"role": "tool", "content": str(result), "tool_name": name})

        # Loop again: the model now sees the tool result and can answer.

    print(f"Stopped: reached the {MAX_STEPS}-step safety limit without a final answer.\n")


# --- Try it with two different questions ---------------------
if __name__ == "__main__":
    run_agent("What is today's date and the current time?")    # Should use the tool
    run_agent("What is the capital of France?")                # Should NOT need the tool
