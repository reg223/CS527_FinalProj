import json
import os
import subprocess
from pathlib import Path

from radon.complexity import cc_visit
from contextlib import contextmanager

@contextmanager
def change_dir(destination):
    """Context manager to safely change directory and return back."""
    origin = os.getcwd()
    try:
        os.chdir(destination)
        yield
    finally:
        os.chdir(origin)

class HumanTrackEvaluator:
    def __init__(self, repo_path, source_dir, report_path):
        self.repo_path = repo_path
        self.source_dir = source_dir # e.g., 'loguru/'
        self.results = {}
        self.report_path = report_path+"_coverage.json"

    def run_coverage_analysis(self):
        """Runs human tests and captures branch coverage with environment isolation."""
        if self.report_path and os.path.exists(self.report_path):
            print(f"Coverage report already exists, skipping analysis.")
            with open(self.report_path) as f:
                data = json.load(f)
                self.results['overall_precision'] = data['totals']['percent_covered']
                self.results['branch_coverage'] = data['totals']['covered_branches']
            return

        print(f"--- Running Coverage.py on {self.repo_path} ---")
        
        # Identify the repository root (one level up from /tests)
        repo_root = os.path.abspath(os.path.join(self.repo_path, ".."))
        report_abs_path = os.path.abspath(self.report_path)

        with change_dir(repo_root):
            # 1. Run pytest under coverage
            # -p no:cov: Disables the pytest-cov plugin to avoid conflict with standalone coverage
            # --override-ini: Ensures we don't inherit problematic settings from tox.ini/pytest.ini
            cmd = [
                "coverage", "run", "--branch", 
                # "-q",
                f"--source={self.source_dir}", 
                "-m", "pytest", 
                "tests", # Use relative path since we are now inside repo_root
                "-p", "no:cov",
                "-o", "cache_dir=.pytest_cache", # Force cache to local folder, not /dev/
                "-c", "/dev/null"
            ]

            # Use check=False: We want coverage even if some tests fail (Exit Code 1)
            # We only care if the process crashes completely (Exit Code 4, etc.)
            result = subprocess.run(cmd, check=False)

            if result.returncode not in [0, 1]:
                print(f"Warning: Pytest exited with unexpected code {result.returncode}")

            # 2. Export report to JSON using the absolute path for the output
            subprocess.run(["coverage", "json", "-o", report_abs_path], check=True)
                
    def run_complexity_analysis(self):
        """Measures Cyclomatic Complexity of the human-authored tests."""
        print("--- Running Radon Static Analysis ---")
        test_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.repo_path) 
                      for f in filenames if f.startswith('test_') and f.endswith('.py')]
        
        complexities = []
        for file in test_files:
            with open(file, 'r') as f:
                code = f.read()
                results = cc_visit(code)
                for item in results:
                    complexities.append(item.complexity)
        
        self.results['avg_test_complexity'] = sum(complexities) / len(complexities) if complexities else 0

    def get_report(self):
        return self.results

# Example Usage for your study
# evaluator = HumanTrackEvaluator(repo_path='loguru/tests', source_dir='loguru')
# evaluator.run_coverage_analysis()
# evaluator.run_complexity_analysis()
# print(evaluator.get_report())