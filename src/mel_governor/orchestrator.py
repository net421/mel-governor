from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .agents import AgentOutput, PromptRegistry, ResearchAgent
from .providers import LLMProvider, provider_from_env


PIPELINE: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("research_planner", ()),
    ("research_archivist", ("research_planner",)),
    ("source_critic", ("research_archivist",)),
    ("semantic_mapper", ("research_archivist", "source_critic")),
    ("contradiction_finder", ("semantic_mapper", "source_critic")),
    ("marx_governor", ("source_critic", "semantic_mapper", "contradiction_finder")),
    ("engels_governor", ("source_critic", "semantic_mapper", "marx_governor")),
    ("auxiliary_historian", ("semantic_mapper", "contradiction_finder")),
    ("auxiliary_economist", ("source_critic", "contradiction_finder")),
    ("auxiliary_sociologist", ("semantic_mapper", "contradiction_finder")),
    (
        "marx_engels_council",
        (
            "marx_governor",
            "engels_governor",
            "auxiliary_historian",
            "auxiliary_economist",
            "auxiliary_sociologist",
        ),
    ),
    ("debate_engine", ("marx_engels_council", "contradiction_finder")),
    ("confidence_engine", ("source_critic", "debate_engine", "marx_engels_council")),
    ("knowledge_graph", ("semantic_mapper", "contradiction_finder", "confidence_engine")),
    ("research_synthesizer", ("marx_engels_council", "debate_engine", "confidence_engine")),
    ("validator", ("source_critic", "debate_engine", "confidence_engine", "knowledge_graph", "research_synthesizer")),
)


@dataclass(frozen=True)
class RunResult:
    run_id: str
    provider: str
    question: str
    outputs: tuple[AgentOutput, ...]
    human_review_required: bool = True
    autonomous_action_authorized: bool = False

    def as_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "provider": self.provider,
            "question": self.question,
            "human_review_required": self.human_review_required,
            "autonomous_action_authorized": self.autonomous_action_authorized,
            "outputs": [asdict(output) for output in self.outputs],
        }


class MELGovernor:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider or provider_from_env()
        self.registry = PromptRegistry()

    def run(self, question: str) -> RunResult:
        question = question.strip()
        if not question:
            raise ValueError("question must not be empty")
        completed: dict[str, str] = {}
        outputs: list[AgentOutput] = []
        for role, dependencies in PIPELINE:
            context = {dependency: completed[dependency] for dependency in dependencies}
            output = ResearchAgent(role, self.provider, self.registry).run(
                question=question,
                context=context,
            )
            outputs.append(output)
            completed[role] = output.content
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return RunResult(
            run_id=f"mel-{stamp}",
            provider=self.provider.name,
            question=question,
            outputs=tuple(outputs),
        )

    @staticmethod
    def publish(result: RunResult, output_dir: Path) -> tuple[Path, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        trace = output_dir / "trace.json"
        report = output_dir / "research_report.md"
        trace.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        sections = [f"# MEL Governor Research Run\n\n**Question:** {result.question}\n"]
        for output in result.outputs:
            sections.append(f"## {output.role}\n\n{output.content}\n")
        sections.append("## Governance\n\nHuman review is required. No autonomous real-world action is authorized.\n")
        report.write_text("\n".join(sections), encoding="utf-8")
        return trace, report


def pipeline_roles() -> Iterable[str]:
    return (role for role, _ in PIPELINE)
