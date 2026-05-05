import subprocess
import json
import os
from radon.complexity import cc_visit

class HumanTrackEvaluator:
    def __init__(self, repo_path, source_dir):
        self.repo_path = repo_path
        self.source_dir = source_dir # e.g., 'loguru/'
        self.results = {}

    def run_coverage_analysis(self):
        """Runs human tests and captures branch coverage."""
        print(f"--- Running Coverage.py on {self.repo_path} ---")
        
        # 1. Run pytest under coverage
        # --branch is critical for your dual-track comparison
        cmd = [
            "coverage", "run", "--branch", 
            f"--source={self.source_dir}", 
            "-m", "pytest", self.repo_path
        ]
        subprocess.run(cmd, check=True)

        # 2. Export report to JSON for easy parsing
        subprocess.run(["coverage", "json", "-o", "coverage.json"], check=True)
        
        with open("coverage.json") as f:
            data = json.load(f)
            self.results['overall_precision'] = data['totals']['percent_covered']
            self.results['branch_coverage'] = data['totals']['covered_branches']
            
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