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


DEFAULT_CODEBASES = [
    "loguru",
    "marshmallow",
    "arrow",
    "tenacity",
    "click",
    "validators",
    "monkeytype",
    "googlemaps",
    "mechanicalsoup",
]
TESTSUITE_ROOT = "./testsuites"
REPORT_ROOT = "./reports"


def _llm_coverage_json_path(code: str) -> str:
    """Path written by HumanTrackEvaluator for the LLM track (``reports/<code>_llm_coverage.json``)."""
    return os.path.join(REPORT_ROOT, f"{code}_llm_coverage.json")


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
    parser.add_argument(
        "--llm-force",
        action="store_true",
        help="LLM track only: rerun even if reports/<code>_llm_coverage.json already exists.",
    )
    args = parser.parse_args()

    os.makedirs(REPORT_ROOT, exist_ok=True)

    print(
        f"Codebases in this run ({len(args.codes)}): {', '.join(args.codes)}\n"
        f"(Each needs `testsuites/<name>/<name>/` sources; "
        f"human track also needs `testsuites/<name>/tests/`.)"
    )

    for code in args.codes:
        print(f"\n========== codebase: {code} ==========\n")

        if args.track in ("human", "both"):
            try:
                _run_human(code)
            except (FileNotFoundError, subprocess.CalledProcessError) as exc:
                print(f"[human] Skip or error on {code}: {exc}")

        if args.track in ("llm", "both"):
            llm_json = _llm_coverage_json_path(code)
            if not args.llm_force and os.path.isfile(llm_json):
                print(
                    f"[llm] Skip {code}: `{llm_json}` already exists. "
                    f"Pass --llm-force to regenerate tests and overwrite reports."
                )
                continue

            try:
                _run_llm(code)
            except FileNotFoundError as exc:
                print(f"[llm] Skip {code} (missing sources/tests layout): {exc}")
            except RuntimeError as exc:
                print(f"[llm] Skipped ({code}): {exc}")
            except subprocess.CalledProcessError as exc:
                report_json = _llm_coverage_json_path(code)
                print(
                    f"[llm] Skip {code}: pytest/coverage exited {exc.returncode}. "
                    f"No NEW report was written for this codebase "
                    f"(expect `{report_json}` only after a successful pytest run under coverage)."
                )

    reports_dir = os.path.abspath(REPORT_ROOT)
    print(f"\n--- Artifact root: {reports_dir} ---")
    print(
        "    JSON:  <name>_coverage.json  (human) / <name>_llm_coverage.json (LLM)\n"
        "    A codebase gets LLM reports ONLY if generate + pytest both succeed; failures skip file output.\n"
        "    LLM: existing `*_llm_coverage.json` skips that codebase unless you pass `--llm-force`."
    )


if __name__ == "__main__":
    main()
