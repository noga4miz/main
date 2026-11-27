"""One interface for several providers, with live / record / replay / auto modes.

Environment variables (or .env):
  LLM_PROVIDER    anthropic | openai | gemini | ollama   (default: anthropic)
  LLM_MODEL       model name (falls back to the provider default)
  LLM_MODE        live | record | replay | auto          (default: auto)
  LLM_RECORDINGS  recordings directory                   (default: ./recordings)

Modes:
  live    always call the real API, never save
  record  call the real API and save the response
  replay  read from recordings only; raise if missing (zero tokens spent)
  auto    use a recording if one exists, otherwise call the API and save it
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from dotenv import load_dotenv

PRESETS = {
    "anthropic": {"model": "claude-haiku-5-5", "key_env": "ANTHROPIC_API_KEY"},
    "openai": {"model": "gpt-4.1-mini", "key_env": "OPENAI_API_KEY", "base_url": None},
    "gemini": {
        "model": "gemini-2.5-flash",
        "key_env": "GEMINI_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
    },
    "ollama": {
        "model": "qwen2.5-coder:7b",
        "key_env": None,
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
    },
}
MODES = {"live", "record", "replay", "auto"}


class ReplayMiss(RuntimeError):
    """Raised in replay mode when no matching recording exists."""


@dataclass
class LLMResponse:
    text: str
    model: str
    provider: str
    input_tokens: int = 0
    output_tokens: int = 0
    cached: bool = False


class LLMClient:
    def __init__(self, provider=None, model=None, mode=None, recordings_dir=None):
        load_dotenv()
        self.provider = (provider or os.getenv("LLM_PROVIDER") or "anthropic").lower()
        if self.provider not in PRESETS:
            raise ValueError(f"Unknown provider: {self.provider}. Options: {', '.join(PRESETS)}")
        preset = PRESETS[self.provider]
        self.model = model or os.getenv("LLM_MODEL") or preset["model"]
        self.mode = (mode or os.getenv("LLM_MODE") or "auto").lower()
        if self.mode not in MODES:
            raise ValueError(f"Unknown mode: {self.mode}. Options: {', '.join(sorted(MODES))}")
        self.recordings_dir = Path(
            recordings_dir or os.getenv("LLM_RECORDINGS") or "recordings"
        )
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self._sdk = None  # created lazily, so replay mode needs no API key

    # ---------- public API ----------
    def chat(self, prompt: str, system: str = "", max_tokens: int = 1024,
             temperature: float = 0.0) -> LLMResponse:
        key = self._key(prompt, system, max_tokens, temperature)
        path = self.recordings_dir / f"{key}.json"

        if self.mode in ("replay", "auto") and path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            data["cached"] = True
            return LLMResponse(**data)
        if self.mode == "replay":
            raise ReplayMiss(
                f"No recording for {key} (provider={self.provider}, model={self.model})"
            )

        resp = self._call_provider(prompt, system, max_tokens, temperature)
        self.total_input_tokens += resp.input_tokens
        self.total_output_tokens += resp.output_tokens

        if self.mode in ("record", "auto"):
            self.recordings_dir.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(asdict(resp), ensure_ascii=False, indent=2), encoding="utf-8"
            )
        return resp

    # ---------- internals ----------
    def _key(self, prompt, system, max_tokens, temperature) -> str:
        blob = json.dumps(
            [self.provider, self.model, system, prompt, max_tokens, temperature],
            ensure_ascii=False,
        )
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:24]

    def _call_provider(self, prompt, system, max_tokens, temperature) -> LLMResponse:
        if self.provider == "anthropic":
            return self._call_anthropic(prompt, system, max_tokens, temperature)
        return self._call_openai_compat(prompt, system, max_tokens, temperature)

    def _require_key(self) -> str:
        env = PRESETS[self.provider]["key_env"]
        if env is None:
            return "ollama"  # Ollama ignores the key, but the SDK requires a value
        val = os.getenv(env)
        if not val:
            raise RuntimeError(f"Missing {env}. Add it to .env or your environment.")
        return val

    def _call_anthropic(self, prompt, system, max_tokens, temperature) -> LLMResponse:
        if self._sdk is None:
            import anthropic
            self._sdk = anthropic.Anthropic(api_key=self._require_key())
        kwargs = dict(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        if system:
            kwargs["system"] = system
        r = self._sdk.messages.create(**kwargs)
        text = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
        return LLMResponse(text, self.model, self.provider,
                           r.usage.input_tokens, r.usage.output_tokens)

    def _call_openai_compat(self, prompt, system, max_tokens, temperature) -> LLMResponse:
        if self._sdk is None:
            from openai import OpenAI
            self._sdk = OpenAI(
                api_key=self._require_key(),
                base_url=PRESETS[self.provider].get("base_url"),
            )
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        r = self._sdk.chat.completions.create(
            model=self.model, messages=messages,
            max_tokens=max_tokens, temperature=temperature,
        )
        u = r.usage
        return LLMResponse(
            r.choices[0].message.content or "", self.model, self.provider,
            getattr(u, "prompt_tokens", 0) or 0, getattr(u, "completion_tokens", 0) or 0,
        )
