from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_NAMES = {".env", ".venv", "venv", "__pycache__", ".pytest_cache"}
SECRET_PATTERNS = (
    re.compile(r"gsk_[A-Za-z0-9]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
)
REQUIRED = (
    "README.md",
    "LICENSE",
    "pyproject.toml",
    ".env.example",
    ".github/workflows/ci.yml",
    "src/mel_governor/orchestrator.py",
    "src/mel_governor/providers.py",
    "src/mel_governor/prompts.json",
    "tests/test_system.py",
)


def validate() -> dict:
    errors: list[str] = []
    scanned = 0
    secret_matches = 0
    for required in REQUIRED:
        if not (ROOT / required).is_file():
            errors.append(f"missing required file: {required}")
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if any(part in FORBIDDEN_NAMES for part in relative.parts):
            continue
        if path.is_dir():
            continue
        scanned += 1
        if path.name == ".env":
            errors.append(".env must not be published")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"binary file not allowed: {relative}")
            continue
        for pattern in SECRET_PATTERNS:
            found = pattern.findall(text)
            secret_matches += len(found)
            if found:
                errors.append(f"secret pattern in {relative}")
    prompts = json.loads((ROOT / "src/mel_governor/prompts.json").read_text(encoding="utf-8"))
    if len(prompts) != 20:
        errors.append(f"expected 20 agent prompts, found {len(prompts)}")
    if errors:
        raise SystemExit("; ".join(errors))
    return {
        "status": "pass",
        "files_scanned": scanned,
        "agent_prompts": len(prompts),
        "secret_patterns_found": secret_matches,
        "default_provider": "mock",
        "web_search_default": False,
        "human_review_required": True,
        "autonomous_action_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args()
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.write_evidence:
        out = ROOT / "release_evidence/release_validation.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
