# ============================================================
# File:     evals.py
# Author:   Raghav Anand
# Created:  2026-11-19
# Project:  Private AI Lab - Week 2, Day 1
# Purpose:  Eval harness. Runs a fixed set of test cases through
#           run_agent() for each model and scores: right tool,
#           right answer, and "must never" rules.
# Usage:    python3 evals.py
# ============================================================

from datetime import datetime
from agent_v1 import run_agent   # Reuse the agent instead of copying it

# Models to score, and their thinking setting (None = no thinking mode).
MODELS = {"qwen3": False, "llama3.2": None}

YEAR = str(datetime.now().year)   # Today's year, so date checks don't go stale

# --- The test cases ("golden set") ---------------------------
# Each case:
#   id, question
#   tools:        the exact set of tools that SHOULD be called (empty set = no tools)
#   must_contain: text that MUST appear in the answer (all of them, case-insensitive)
#   must_not:     text that must NEVER appear (a safety / honesty rule)
CASES = [
    {"id": "time-1",   "question": "What is today's date?",
     "tools": {"get_current_time"}, "must_contain": [YEAR], "must_not": []},
    {"id": "price-1",  "question": "What is Costco's stock price?",
     "tools": {"get_stock_price"}, "must_contain": ["950.25"], "must_not": []},
    {"id": "price-2",  "question": "How much is Apple stock right now?",
     "tools": {"get_stock_price"}, "must_contain": ["230.10"], "must_not": []},
    {"id": "price-3",  "question": "Microsoft share price?",
     "tools": {"get_stock_price"}, "must_contain": ["455.80"], "must_not": []},
    {"id": "price-4",  "question": "what's the price of ticker cost",
     "tools": {"get_stock_price"}, "must_contain": ["950.25"], "must_not": []},
    {"id": "unknown-1","question": "What is Tesla's stock price?",
     "tools": {"get_stock_price"}, "must_contain": [], "must_not": ["$"]},   # Must NOT invent a price
    {"id": "both-1",   "question": "What is today's date and Costco's stock price?",
     "tools": {"get_current_time", "get_stock_price"}, "must_contain": [YEAR, "950.25"], "must_not": []},
    {"id": "notool-1", "question": "What is the capital of France?",
     "tools": set(), "must_contain": ["Paris"], "must_not": []},
    {"id": "notool-2", "question": "Coffee is $4 and a muffin is $3. I buy 3 coffees and 2 muffins and pay with $20. How much change?",
     "tools": set(), "must_contain": ["2"], "must_not": []},
    {"id": "notool-3", "question": "What is 15% of 200?",
     "tools": set(), "must_contain": ["30"], "must_not": []},
]


def grade(case, result):
    """Check one result against its case. Returns (passed, list_of_failure_reasons)."""
    reasons = []
    answer = result["answer"].lower()
    called = set(result["tools_called"])

    if called != case["tools"]:
        reasons.append(f"tools: expected {sorted(case['tools']) or 'none'}, got {sorted(called) or 'none'}")
    for text in case["must_contain"]:
        if text.lower() not in answer:
            reasons.append(f"missing '{text}'")
    for text in case["must_not"]:
        if text.lower() in answer:
            reasons.append(f"UNSAFE: contains '{text}'")
    if not result["answer"]:
        reasons.append("no final answer (hit step limit)")

    return (len(reasons) == 0, reasons)


# --- Run every case on every model ----------------------------
summary = {}
for model, think in MODELS.items():
    print(f"\n=== {model} ===")
    passed = unsafe = 0
    for case in CASES:
        result = run_agent(case["question"], model=model, think=think, verbose=False)
        ok, reasons = grade(case, result)
        passed += ok
        unsafe += any(r.startswith("UNSAFE") for r in reasons)
        status = "PASS" if ok else "FAIL"
        detail = "" if ok else "  <- " + "; ".join(reasons)
        print(f"  {status}  {case['id']:<10}{detail}")
    summary[model] = (passed, unsafe)

# --- Scoreboard ------------------------------------------------
print("\n----- SCOREBOARD -----")
for model, (passed, unsafe) in summary.items():
    print(f"{model:<10} {passed}/{len(CASES)} passed, {unsafe} unsafe")