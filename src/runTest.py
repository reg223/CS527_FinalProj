"""Run human and/or LLM evaluation tracks across configured codebases."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

_SRC = os.path.dirname(os.path.abspath(__file__))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import humanTest  # noqa: E402
import llmTest  # noqa: E402


DEFAULT_CODEBASES = ["loguru", "marshmallow"]
TESTSUITE_ROOT = "./testsuites"
REPORT_ROOT = "./reports"


def _run_human(code: str):
    evaluator = humanTest.HumanTrackEvaluator(
        repo_path=os.path.join(TESTSUITE_ROOT, code, "tests"),
        source_dir=os.path.join(TESTSUITE_ROOT, code, code),
        report_path=os.path.join(REPORT_ROOT, code),
    )
    evaluator.run_coverage_analysis()
    evaluator.run_complexity_analysis()
    print(evaluator.get_report())


def _run_llm(code: str):
    evaluator = llmTest.LLMTrackEvaluator(
        repo_path=os.path.join(TESTSUITE_ROOT, code, "llm_tests"),
        source_dir=os.path.join(TESTSUITE_ROOT, code, code),
        report_path=os.path.join(REPORT_ROOT, f"{code}_llm"),
    )
    evaluator.generate_and_validate_tests()
    evaluator.run_coverage_analysis()
    evaluator.run_complexity_analysis()
    print(evaluator.get_report())


def main():
    parser = argparse.ArgumentParser(description="Human vs LLM test-track evaluation runners.")
    parser.add_argument(
        "--track",
        choices=("human", "llm", "both"),
        default="human",
        help="Which evaluation track to run (LLM requires OPENAI_API_KEY). Default: human only.",
    )
    parser.add_argument(
        "--codes",
        nargs="*",
        default=list(DEFAULT_CODEBASES),
        help=f"Codebases under {TESTSUITE_ROOT} (default: {DEFAULT_CODEBASES}).",
    )
    args = parser.parse_args()

    os.makedirs(REPORT_ROOT, exist_ok=True)

    for code in args.codes:
        print(f"\n========== codebase: {code} ==========\n")

        if args.track in ("human", "both"):
            try:
                _run_human(code)
            except (FileNotFoundError, subprocess.CalledProcessError) as exc:
                print(f"[human] Skip or error on {code}: {exc}")

        if args.track in ("llm", "both"):
            try:
                _run_llm(code)
            except FileNotFoundError as exc:
                print(f"[llm] Skip {code} (missing sources/tests layout): {exc}")
            except RuntimeError as exc:
                print(f"[llm] Skipped ({code}): {exc}")


if __name__ == "__main__":
    main()
