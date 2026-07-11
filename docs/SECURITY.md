# Security

## Credentials

- Never commit `.env`.
- `.env.example` contains empty placeholders only.
- `GROQ_API_KEY` is read lazily only when `MEL_LLM_PROVIDER=groq`.
- The default provider is offline `mock`.
- Rotate any credential that appeared in prior local ZIPs or workspaces.

## Network boundary

Core tests and CI perform no network calls. Optional providers are explicit, fail closed without credentials, and are excluded from default validation.

## Generated artifacts

`artifacts/` and `release_evidence/` are ignored. They may contain model outputs or research traces and should be reviewed before intentional publication.

## Claims

Mock outputs validate orchestration only. They are not evidence that the political analysis is correct, unbiased, complete, or externally validated.
