# llm-client

One interface for several LLM providers (anthropic, openai, gemini, ollama)
with record/replay modes, so development can run with zero token spend.

## Install (WSL)

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    cp .env.example .env      # then add your API key
    code .

If venv is missing: `sudo apt install python3-venv`.

## Use

    llm "write hello world in Python"
    llm --provider ollama --mode replay "..."

    from llm_client import LLMClient
    r = LLMClient().chat("hello", system="Answer briefly")
    print(r.text, r.input_tokens, r.output_tokens)

Modes (`LLM_MODE`): live, record, replay, auto.
