# ============================================================
# File:     chat_basic.py
# Author:   Raghav Anand
# Created:  2026-11-19
# Project:  Private AI Lab - Week 1, Day 2
# Purpose:  Send one question to the local Qwen3 model running
#           in Ollama, print its thinking and answer, and
#           measure how long it took (total time + tokens/sec).
# Runs:     100% locally. No internet, no API key, no cost.
# ============================================================

# --- Imports ------------------------------------------------
import time                 # Python's built-in clock, used to time the call
from ollama import chat     # The official Ollama Python library's chat function

# --- Settings (change these to experiment) ------------------
MODEL = "qwen3"             # Which local model to use (from `ollama list`)
THINK = True                # True = show the model's reasoning; False = answer only (faster)

QUESTION = "In 3 bullet points, explain why a company would run an AI model locally instead of using a cloud API."

# --- Build the conversation ---------------------------------
# A chat is a list of messages. Each message has a "role" and "content".
#   "system" = standing instructions for the model (the system prompt)
#   "user"   = what you are asking
messages = [
    {"role": "system", "content": "You are a concise, accurate assistant. If you are not sure, say so."},
    {"role": "user", "content": QUESTION},
]

# --- Call the model and time it -----------------------------
print(f"Asking {MODEL}: {QUESTION}\n")

start = time.perf_counter()          # Start the stopwatch (high-precision timer)

# This one line sends an HTTP request to http://localhost:11434/api/chat
# (the same server you just hit with curl) and waits for the full reply.
response = chat(
    model=MODEL,
    messages=messages,
    think=THINK,
)

elapsed = time.perf_counter() - start  # Stop the stopwatch: seconds as a decimal

# --- Print the model's thinking (if any) ---------------------
# getattr(..., None) safely returns None if the field doesn't exist,
# so the script doesn't crash on models without a thinking mode.
thinking = getattr(response.message, "thinking", None)
if thinking:
    print("----- THINKING -----")
    print(thinking.strip())
    print()

# --- Print the final answer ---------------------------------
print("----- ANSWER -----")
print(response.message.content.strip())
print()

# --- Print performance stats ---------------------------------
# Ollama reports durations in NANOSECONDS (1 second = 1,000,000,000 ns).
# eval_count    = how many tokens the model generated
# eval_duration = how long generating those tokens took
tokens_out = response.eval_count or 0
gen_seconds = (response.eval_duration or 0) / 1_000_000_000

print("----- STATS -----")
print(f"Total wall-clock time : {elapsed:.1f} seconds")
print(f"Tokens generated      : {tokens_out}")
if gen_seconds > 0:
    print(f"Generation speed      : {tokens_out / gen_seconds:.1f} tokens/second")