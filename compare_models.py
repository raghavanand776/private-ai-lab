# ============================================================
# File:     compare_models.py
# Author:   Raghav Anand
# Created:  2026-11-19
# Project:  Private AI Lab - Week 1, Day 3
# Purpose:  Ask two local models the same 5 questions, time
#           every answer, print a speed table, and save all
#           answers to results.md for a quality review.
# Runs:     100% locally through Ollama. No internet, no cost.
# ============================================================

# --- Imports ------------------------------------------------
import time                 # Stopwatch for timing each answer
from ollama import chat     # Official Ollama Python library

# --- Settings -----------------------------------------------
# Each model, plus how to set its "thinking" option:
#   False = model supports thinking, but we turn it OFF for a fair test
#   None  = model has no thinking mode, so we don't send the option at all
MODELS = {
    "qwen3": False,
    "llama3.2": None,
}

# The same 5 questions go to every model. Each tests a different skill.
QUESTIONS = [
    ("Fact",        "What is the capital of Australia? Answer in one word."),
    ("Math",        "Coffee costs $4 and a muffin costs $3. I buy 3 coffees and 2 muffins and pay with a $20 bill. How much change do I get? Show brief steps."),
    ("Fintech",     "In 2 sentences, what is an ACH return in US payments?"),
    ("Instructions","List exactly 3 fruits as a comma-separated list. Output nothing else."),
    ("Honesty",     "What was Costco's closing stock price yesterday?"),
]

SYSTEM_PROMPT = "You are a concise, accurate assistant. If you do not know something, say so."

NS_PER_SECOND = 1_000_000_000   # Ollama reports durations in nanoseconds


# --- Helper: ask one model one question ---------------------
def ask(model, think_setting, question):
    """Send one question to one model. Returns the answer text and timing numbers."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    # Only include the 'think' option for models that support it.
    extra = {} if think_setting is None else {"think": think_setting}

    start = time.perf_counter()
    response = chat(model=model, messages=messages, **extra)   # The actual call to Ollama
    elapsed = time.perf_counter() - start

    tokens = response.eval_count or 0
    gen_seconds = (response.eval_duration or 0) / NS_PER_SECOND
    load_seconds = (response.load_duration or 0) / NS_PER_SECOND   # Time spent loading the model into memory

    return {
        "answer": response.message.content.strip(),
        "seconds": elapsed,
        "tokens": tokens,
        "tok_per_sec": tokens / gen_seconds if gen_seconds > 0 else 0,
        "load_seconds": load_seconds,
    }


# --- Main: run every model on every question ----------------
results = {}   # results[model][question_number] = the dictionary returned by ask()

for model, think_setting in MODELS.items():
    print(f"\n=== Testing {model} ===")
    results[model] = {}
    for number, (skill, question) in enumerate(QUESTIONS, start=1):
        print(f"  Q{number} ({skill})...", end=" ", flush=True)   # Progress line, so you see it working
        result = ask(model, think_setting, question)
        results[model][number] = result
        print(f"{result['seconds']:.1f}s")

# --- Print the speed table -----------------------------------
print("\n----- SPEED TABLE -----")
print(f"{'Model':<10} {'Q':<3} {'Skill':<13} {'Seconds':>8} {'Tokens':>7} {'Tok/s':>7} {'Load s':>7}")
for model in MODELS:
    for number, (skill, _) in enumerate(QUESTIONS, start=1):
        r = results[model][number]
        print(f"{model:<10} {number:<3} {skill:<13} {r['seconds']:>8.1f} {r['tokens']:>7} {r['tok_per_sec']:>7.1f} {r['load_seconds']:>7.1f}")

# --- Save every answer to results.md for a quality review ----
with open("results.md", "w") as f:
    f.write("# Model comparison: answers\n\n")
    f.write("Score each answer 1 (bad) to 5 (great) in the Score column.\n\n")
    for number, (skill, question) in enumerate(QUESTIONS, start=1):
        f.write(f"## Q{number}: {skill}\n\n")
        f.write(f"**Question:** {question}\n\n")
        for model in MODELS:
            r = results[model][number]
            f.write(f"**{model}** ({r['seconds']:.1f}s) | Score: __\n\n")
            f.write(f"{r['answer']}\n\n")
        f.write("---\n\n")

print("\nAll answers saved to results.md")