from __future__ import annotations

import json
from pathlib import Path

import pytest

from mel_governor.agents import PromptRegistry
from mel_governor.orchestrator import MELGovernor, PIPELINE
from mel_governor.providers import MockProvider, ProviderError, provider_from_env


def test_registry_matches_pipeline() -> None:
    registry = PromptRegistry()
    assert set(registry.roles) == {role for role, _ in PIPELINE}


def test_pipeline_has_all_governance_layers() -> None:
    roles = [role for role, _ in PIPELINE]
    for required in (
        "mel_council",
        "anti_revisionist_council",
        "debate_engine",
        "confidence_engine",
        "knowledge_graph",
        "research_synthesizer",
        "validator",
    ):
        assert required in roles
    assert len(roles) == 20


def test_dependencies_are_topologically_ordered() -> None:
    seen: set[str] = set()
    for role, dependencies in PIPELINE:
        assert set(dependencies) <= seen
        seen.add(role)


def test_mock_provider_is_deterministic() -> None:
    provider = MockProvider()
    kwargs = {"role": "validator", "system_prompt": "audit", "user_prompt": "claim"}
    assert provider.complete(**kwargs) == provider.complete(**kwargs)


def test_default_provider_is_offline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MEL_LLM_PROVIDER", raising=False)
    assert provider_from_env().name == "mock"


def test_groq_fails_closed_without_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MEL_LLM_PROVIDER", "groq")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ProviderError):
        provider_from_env()


def test_unknown_provider_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MEL_LLM_PROVIDER", "unknown")
    with pytest.raises(ProviderError):
        provider_from_env()


def test_empty_question_is_rejected() -> None:
    with pytest.raises(ValueError):
        MELGovernor(MockProvider()).run("  ")


def test_full_pipeline_executes_offline() -> None:
    result = MELGovernor(MockProvider()).run("What distinguishes evidence from doctrine?")
    assert len(result.outputs) == 20
    assert result.outputs[-1].role == "validator"
    assert result.human_review_required is True
    assert result.autonomous_action_authorized is False
    assert all("OFFLINE MOCK" in output.content for output in result.outputs)


def test_publish_writes_trace_and_report(tmp_path: Path) -> None:
    result = MELGovernor(MockProvider()).run("How should confidence be calibrated?")
    trace, report = MELGovernor.publish(result, tmp_path)
    payload = json.loads(trace.read_text(encoding="utf-8"))
    assert payload["provider"] == "mock"
    assert payload["human_review_required"] is True
    assert payload["autonomous_action_authorized"] is False
    assert len(payload["outputs"]) == 20
    assert "No autonomous real-world action is authorized" in report.read_text(encoding="utf-8")
