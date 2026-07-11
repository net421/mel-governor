from __future__ import annotations

import argparse
from pathlib import Path

from .orchestrator import MELGovernor


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run the MEL Governor research pipeline")
    p.add_argument("--question", required=True)
    p.add_argument("--output", type=Path, default=Path("artifacts/latest"))
    return p


def main() -> int:
    args = parser().parse_args()
    governor = MELGovernor()
    result = governor.run(args.question)
    trace, report = governor.publish(result, args.output)
    print(f"provider={result.provider}")
    print(f"agents={len(result.outputs)}")
    print(f"trace={trace}")
    print(f"report={report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
