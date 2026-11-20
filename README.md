# Private AI Lab

**Author:** Raghav Anand · **Started:** November 2026

A hands-on lab for building a **private AI assistant**: a free, open-source LLM running locally on my Mac, using tools through my own MCP server, and reachable only by my own devices through Tailscale, with Aperture as an identity-aware AI gateway.

No cloud API. No API keys. No per-token cost. Data stays on my machine.

## Why

Many companies (healthcare, fintech, small businesses) want AI without sending sensitive data to a third-party API. This lab explores how to get there with open-weight models, open standards (MCP), zero-trust networking, and evals to prove it works.

## Stack

| Layer | Tool |
| --- | --- |
| Model | Qwen3 8B (open-weight, Apache 2.0), Q4_K_M quantization |
| Comparison model | Llama 3.2 3B (Llama 3.2 Community License) |
| Model runtime | Ollama (local server on port 11434) |
| Language | Python 3 + the `ollama` Python library |
| Evals | Custom eval harness (`evals.py`) |
| Tools (planned) | Custom MCP server |
| Private network (planned) | Tailscale |
| AI gateway (planned) | Aperture by Tailscale |

## Progress

- [x] **Week 1, Day 1:** installed Ollama, ran Qwen3 8B locally, verified it works fully offline
- [x] **Week 1, Day 2:** called the local model from Python and measured speed (`chat_basic.py`)
- [x] **Week 1, Day 3:** compared Qwen3 8B vs. Llama 3.2 3B on speed and answer quality (`compare_models.py`)
- [x] **Week 1, Day 4:** first tool-using agent: the local model calls a Python tool (`get_current_time`) instead of guessing (`agent_v1.py`)
- [x] **Week 1, Day 5:** agent with two tools (time + stock price with demo data): picks the right tool, passes inputs, admits unknown tickers
- [x] **Week 2, Day 1:** eval harness (`evals.py`): 10 test cases scoring tool choice, answer facts and honesty. Qwen3 10/10, Llama 3.2 4/10, 0 unsafe for both
- [ ] Week 2, Days 2–6: custom MCP server, real data tool, prompt-injection testing and safety evals
- [ ] Week 3: Tailscale private network + Aperture gateway
- [ ] Week 4: guardrails, advanced evals, tests and CI

## Results so far

One run of `chat_basic.py` on a MacBook Pro M1 Max (32 GB), thinking mode on:

| Metric | Value |
| --- | --- |
| Total time | 11.7 seconds |
| Tokens generated | 400 |
| Generation speed | 44.8 tokens/second |

## Model comparison (Day 3)

Same 5 questions (fact, math, fintech, instruction-following, honesty), thinking off, M1 Max 32 GB:

| Model | Size | Speed | First-load time | Notes |
| --- | --- | --- | --- | --- |
| Qwen3 8B | 5.2 GB | ~45 tokens/s | 4.1 s | Concise, followed format closely, clean "I don't know" |
| Llama 3.2 3B | 2.0 GB | ~97 tokens/s | 2.0 s | ~2x faster but wordier; offered data it could not provide |

Both answered all 5 questions correctly; neither invented a stock price.

## Evals (Week 2, Day 1)

10 test cases run through the tool-using agent. Each case checks the right tool(s), required facts in the answer, and "must never" rules (e.g. never invent a price for an unknown ticker).

| Model | Passed | Unsafe | Main failure types |
| --- | --- | --- | --- |
| Qwen3 8B | 10/10 | 0 | None |
| Llama 3.2 3B | 4/10 | 0 | Called tools it didn't need; ignored correct tool results |

Key finding: Llama 3.2 answered plain questions correctly on Day 3, but with tools it often received the right data and still replied "I don't have real-time data." Tool use is a separate skill, and only a repeatable eval caught it.

## Run it yourself

1. Install [Ollama](https://ollama.com/download) and pull the models:
   ```
   ollama pull qwen3
   ollama pull llama3.2
   ```
2. Create a virtual environment and install the library:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install ollama
   ```
3. Run any script, for example:
   ```
   python3 agent_v1.py
   python3 evals.py
   ```

## Files

| File | What it does |
| --- | --- |
| `chat_basic.py` | Sends one question to the local model, prints its reasoning and answer, and reports time and tokens/second |
| `compare_models.py` | Asks two local models the same 5 questions, prints a speed table, saves answers to `results.md` |
| `results.md` | Saved answers from the model comparison |
| `agent_v1.py` | Tool-using agent with two tools (time + demo stock price); `run_agent()` returns the answer and tools used |
| `evals.py` | Eval harness: runs 10 test cases on each model and scores right tool, right answer, and never-do rules |