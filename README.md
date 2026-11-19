# Private AI Lab

**Author:** Raghav Anand · **Started:** November 2026

A hands-on lab for building a **private AI assistant**: a free, open-source LLM running locally on my Mac, using tools through my own MCP server, and reachable only by my own devices through Tailscale, with Aperture as an identity-aware AI gateway.

No cloud API. No API keys. No per-token cost. Data stays on my machine.

## Why

Many companies (healthcare, fintech, small businesses) want AI without sending sensitive data to a third-party API. This lab explores how to get there with open-weight models, open standards (MCP) and zero-trust networking.

## Stack

| Layer | Tool |
| --- | --- |
| Model | Qwen3 8B (open-weight, Apache 2.0), Q4_K_M quantization |
| Model runtime | Ollama (local server on port 11434) |
| Language | Python 3 + the `ollama` Python library |
| Tools (planned) | Custom MCP server |
| Private network (planned) | Tailscale |
| AI gateway (planned) | Aperture by Tailscale |

## Progress

- [x] **Week 1, Day 1:** installed Ollama, ran Qwen3 8B locally, verified it works fully offline
- [x] **Week 1, Day 2:** called the local model from Python and measured speed (`chat_basic.py`)
- [ ] Week 1, Days 3–5: model comparison and tool calling with a local model
- [ ] Week 2: custom MCP server + prompt-injection testing
- [ ] Week 3: Tailscale private network + Aperture gateway
- [ ] Week 4: guardrails, evals, tests and CI

## Results so far

One run of `chat_basic.py` on a MacBook Pro M1 Max (32 GB), thinking mode on:

| Metric | Value |
| --- | --- |
| Total time | 11.7 seconds |
| Tokens generated | 400 |
| Generation speed | 44.8 tokens/second |

## Run it yourself

1. Install [Ollama](https://ollama.com/download) and pull the model:
   ```
   ollama pull qwen3
   ```
2. Create a virtual environment and install the library:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install ollama
   ```
3. Run:
   ```
   python3 chat_basic.py
   ```

## Files

| File | What it does |
| --- | --- |
| `chat_basic.py` | Sends one question to the local model, prints its reasoning and answer, and reports time and tokens/second |