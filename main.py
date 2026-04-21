#!/usr/bin/env python3
"""
Log Analyzer CLI
Usage:
  python main.py --generate-sample
  python main.py --file logs/sample.log
  python main.py --file app.log --json-out report.json --severity HIGH
"""
import sys, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from analyzer import LogAnalyzer
from reporter import ConsoleReporter, JsonReporter
from sample_generator import generate_sample_log

def main():
    p = argparse.ArgumentParser(description="Production Log Analyzer")
    p.add_argument("--file",            metavar="PATH")
    p.add_argument("--json-out",        metavar="PATH")
    p.add_argument("--severity",        choices=["CRITICAL","HIGH","MEDIUM","LOW"])
    p.add_argument("--no-dedup",        action="store_true")
    p.add_argument("--generate-sample", action="store_true")
    args = p.parse_args()

    if args.generate_sample:
        file_path = generate_sample_log("logs/sample.log")
    elif args.file:
        file_path = args.file
    else:
        p.print_help(); return 0

    if not Path(file_path).exists():
        print(f"  ❌  File not found: {file_path}"); return 1

    result = LogAnalyzer(deduplicate=not args.no_dedup).analyze(file_path)
    if args.severity:
        order = ["LOW","MEDIUM","HIGH","CRITICAL"]
        cutoff = order.index(args.severity)
        result.incidents = [i for i in result.incidents if order.index(i.severity) >= cutoff]

    ConsoleReporter().render(result)
    out = args.json_out or (Path(file_path).stem + "_report.json")
    JsonReporter().write(result, out)
    return 2 if result.by_severity["CRITICAL"] > 0 else 0

if __name__ == "__main__":
    sys.exit(main())