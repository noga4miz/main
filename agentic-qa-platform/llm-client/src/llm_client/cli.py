import argparse
import sys

from .client import LLMClient


def main() -> None:
    p = argparse.ArgumentParser(prog="llm", description="LLM client CLI")
    p.add_argument("prompt", nargs="?", help="Prompt text (read from stdin if omitted)")
    p.add_argument("--system", default="")
    p.add_argument("--provider")
    p.add_argument("--model")
    p.add_argument("--mode", choices=["live", "record", "replay", "auto"])
    p.add_argument("--max-tokens", type=int, default=1024)
    a = p.parse_args()

    prompt = a.prompt or sys.stdin.read()
    client = LLMClient(provider=a.provider, model=a.model, mode=a.mode)
    r = client.chat(prompt, system=a.system, max_tokens=a.max_tokens)
    print(r.text)
    tag = "cache" if r.cached else "live"
    print(f"\n[{r.provider}/{r.model} | {tag} | in={r.input_tokens} out={r.output_tokens}]",
          file=sys.stderr)


if __name__ == "__main__":
    main()
