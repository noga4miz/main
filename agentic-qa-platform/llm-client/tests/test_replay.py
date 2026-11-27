import pytest

from llm_client import LLMClient, LLMResponse, ReplayMiss


def test_replay_miss_raises(tmp_path):
    c = LLMClient(provider="ollama", mode="replay", recordings_dir=tmp_path)
    with pytest.raises(ReplayMiss):
        c.chat("hello")


def test_record_then_replay(tmp_path, monkeypatch):
    rec = LLMClient(provider="ollama", mode="record", recordings_dir=tmp_path)
    monkeypatch.setattr(
        rec, "_call_provider",
        lambda *a, **k: LLMResponse("hello back", "m", "ollama", 5, 2),
    )
    assert rec.chat("hi").text == "hello back"

    rep = LLMClient(provider="ollama", mode="replay", recordings_dir=tmp_path)
    out = rep.chat("hi")
    assert out.text == "hello back" and out.cached
