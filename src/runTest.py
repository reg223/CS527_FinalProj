import humanTest
import os



codePath = "./testsuites"
codes = ['loguru','marshmallow','arrow','tenacity','click','validators','monkeytype','googlemaps','mechanicalsoup']
resultPath = "./reports"
  
def main():
  for code in codes:
      evaluator = humanTest.HumanTrackEvaluator(repo_path=f'{codePath}/{code}/tests', source_dir=f'{codePath}/{code}/{code}', report_path=resultPath+ f"/{code}")
      evaluator.run_coverage_analysis()
      evaluator.run_complexity_analysis()
      report = evaluator.get_report()
      print(report)
    
if __name__ == "__main__":
  main()