# MEL Governor

**MEL Governor** is a multi-agent political-economy research and evidence-governance laboratory. It coordinates specialized agents for planning, archival organization, source criticism, semantic mapping, contradiction analysis, Marx–Engels–Lenin interpretation, auxiliary review, MEL synthesis, Stalin–Hoxha analysis, anti-revisionist synthesis, adversarial debate, confidence calibration, knowledge graphs, research synthesis, and validation.

The political orientation is explicit. The project does not claim neutrality, automatic truth, or autonomous decision authority. Its engineering contribution is a reproducible, inspectable orchestration pattern for evidence-intensive research.

## Pipeline

```text
Planner → Archivist → Source Critic → Semantic Mapper → Contradiction Finder
        → Marx → Engels → Lenin → Auxiliary Reviews → MEL Council
        → Stalin → Hoxha → Anti-Revisionist Council
        → Debate → Confidence → Knowledge Graph → Synthesis → Validator
```

The complete graph contains **20 named roles** with topologically validated dependencies.

## Safe offline validation

```bash
python -m pip install -e ".[dev]"
make verify
```

The default provider is deterministic and offline. It performs no network calls and spends no tokens.

```bash
mel-governor \
  --question "How should evidence, interpretation, and normative judgment be distinguished?" \
  --output artifacts/example
```

This writes:

- `trace.json` with role dependencies and outputs;
- `research_report.md` with all twenty stages;
- explicit human-review and no-autonomy boundaries.

Mock responses demonstrate orchestration only. They are not substantive political conclusions.

## Optional Groq provider

Install the optional dependency and pass the key through the environment:

```bash
python -m pip install -e ".[groq]"
export MEL_LLM_PROVIDER=groq
export GROQ_API_KEY="..."
mel-governor --question "..."
```

Never commit credentials. Any key that appeared in earlier local ZIP files should be revoked or rotated independently.

## Engineering controls

- offline-by-default provider;
- lazy optional provider import;
- fail-closed credential handling;
- versioned prompt registry;
- explicit dependency graph;
- deterministic end-to-end tests;
- secret and release hygiene validator;
- pinned GitHub Actions;
- generated outputs excluded from source control;
- human review required;
- autonomous real-world action disabled.

## Epistemic boundaries

Outputs should distinguish source material, factual claims, inference, theoretical interpretation, normative judgment, unresolved contradiction, and confidence. The system is a research aid, not an authority.

It does not provide operational instructions for violence, illegality, clandestinity, sabotage, evasion, or real-world insurrection.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Security](docs/SECURITY.md)

## License

MIT.
