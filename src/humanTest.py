import json
import os
import subprocess
import sys
from pathlib import Path

from cognitive_complexity.api import get_cognitive_complexity
from radon.complexity import cc_visit


class HumanTrackEvaluator:
    def __init__(self, repo_path, source_dir, report_path=None):
        self.repo_path = repo_path
        self.source_dir = source_dir
        self.results = {}
        self.report_path = (
            f"{report_path}_coverage.json" if report_path else f"{self.source_dir}_coverage.json"
        )

    def run_coverage_analysis(self):
        """Runs human tests and captures branch coverage."""
        if self.report_path and os.path.exists(self.report_path):
            print("Coverage report already exists, skipping analysis.")
            with open(self.report_path, encoding="utf-8") as f:
                data = json.load(f)
                self.results["overall_precision"] = data["totals"]["percent_covered"]
                self.results["branch_coverage"] = data["totals"]["covered_branches"]
            return

        print(f"--- Running Coverage.py on {self.repo_path} ---")

        env = os.environ.copy()
        src_parent = str(Path(self.source_dir).resolve().parent)
        env["PYTHONPATH"] = src_parent + os.pathsep + env.get("PYTHONPATH", "")

        cmd = [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--branch",
            f"--source={self.source_dir}",
            "-m",
            "pytest",
            self.repo_path,
        ]
        subprocess.run(cmd, check=True, env=env)

        subprocess.run(
            [sys.executable, "-m", "coverage", "json", "-o", self.report_path],
            check=True,
            env=env,
        )

        print(f"--- Coverage JSON: {self.report_path} ---")
        with open(self.report_path, encoding="utf-8") as f:
            data = json.load(f)
            self.results["overall_precision"] = data["totals"]["percent_covered"]
            self.results["branch_coverage"] = data["totals"]["covered_branches"]

    def run_complexity_analysis(self):
        """Measures both Cyclomatic and Cognitive Complexity of the tests."""
        print("--- Running Radon & Cognitive Static Analysis ---")
        test_files = [
            os.path.join(dp, f)
            for dp, _, filenames in os.walk(self.repo_path)
            for f in filenames
            if f.startswith("test_") and f.endswith(".py")
        ]

        cc_scores = []
        cog_scores = []

        for file in test_files:
            with open(file, "r", encoding="utf-8") as f:
                code = f.read()
                for item in cc_visit(code):
                    cc_scores.append(item.complexity)
                cog_scores.append(get_cognitive_complexity(code))

        self.results["avg_cyclomatic_complexity"] = (
            sum(cc_scores) / len(cc_scores) if cc_scores else 0
        )
        self.results["avg_cognitive_complexity"] = (
            sum(cog_scores) / len(cog_scores) if cog_scores else 0
        )

    def get_report(self):
        return self.results