"""Run the project's automated checks without touching physical hardware."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
VERIFY = ROOT / "src" / "verify.py"


def _run_verify() -> tuple[str, int]:
    """Run the existing monolithic synthetic test suite once."""
    environment = os.environ.copy()
    source = str(ROOT / "src")
    environment["PYTHONPATH"] = (
        source + os.pathsep + environment["PYTHONPATH"]
        if environment.get("PYTHONPATH")
        else source
    )
    environment.setdefault("QT_QPA_PLATFORM", "offscreen")

    completed = subprocess.run(
        [sys.executable, str(VERIFY)],
        cwd=ROOT,
        env=environment,
        check=False,
    )
    return ("PASS" if completed.returncode == 0 else "FAIL", completed.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run automated project checks; physical-camera scripts are skipped."
        )
    )
    parser.add_argument(
        "--group",
        choices=("all", "automated", "unit", "integration", "hardware"),
        default="all",
        help="test group to run (default: all)",
    )
    args = parser.parse_args()

    results: list[tuple[str, str, str]] = []
    run_automated = args.group in {"all", "automated", "unit", "integration"}
    if run_automated:
        label = "automated (unit + synthetic integration)"
        status, code = _run_verify()
        reason = "src/verify.py" if status == "PASS" else f"exit code {code}"
        results.append((status, label, reason))

    if args.group in {"all", "hardware"}:
        results.append(
            (
                "SKIP",
                "hardware",
                "test_camera.py and tes.py require a physical camera/manual observation",
            )
        )

    print("\n=== Test summary ===")
    for status, label, reason in results:
        print(f"{status:>4}  {label}: {reason}")

    counts = {
        status: sum(item[0] == status for item in results)
        for status in ("PASS", "FAIL", "SKIP")
    }
    print(
        "Totals: "
        f"PASS={counts['PASS']} FAIL={counts['FAIL']} SKIP={counts['SKIP']}"
    )
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
