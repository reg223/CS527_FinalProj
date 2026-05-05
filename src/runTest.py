import humanTest
import os

codePath = "./testsuites"
# List of target repositories
codes = ['loguru', 'marshmallow', 'arrow', 'tenacity', 'click', 'validators', 'monkeytype', 'googlemaps', 'mechanicalsoup']
resultPath = "./reports"

# Ensure report directory exists
os.makedirs(resultPath, exist_ok=True)

def main():
    for code in codes:
        # Paths setup
        repo_tests = os.path.join(codePath, code, "tests")
        
        # KEY CHANGE: source_dir should be the package name (e.g., 'click') 
        # so Coverage.py can find it in the PYTHONPATH
        source_package_name = code 
        
        # Ensure the report has a .json extension
        report_file = os.path.join(resultPath, f"{code}_coverage.json")
        
        print(f"\n{'='*20} EVALUATING: {code.upper()} {'='*20}")
        
        evaluator = humanTest.HumanTrackEvaluator(
            repo_path=repo_tests, 
            source_dir=source_package_name, 
            report_path=report_file
        )
        
        try:
            evaluator.run_coverage_analysis()
            evaluator.run_complexity_analysis()
            
            report = evaluator.get_report()
            print(f"Success for {code}: {report}")
        except Exception as e:
            print(f"Failed to evaluate {code}: {str(e)}")
    
if __name__ == "__main__":
    main()