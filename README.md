# 🔍 Log Analyzer — Production Incident Intelligence

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://python.org)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)](.)

A production-grade Python CLI that parses log files, detects errors, classifies severity, and exports JSON reports.

> Built from **5 years of production experience** at Shiprocket — India's largest logistics platform.

## Quick Start
```bash
git clone https://github.com/Prateek-Aroraa/log-analyzer.git
cd log-analyzer
python main.py --generate-sample
python main.py --file logs/sample.log --json-out report.json
```

## Features
- Detects HTTP 5xx · Timeouts · Exceptions · Slow queries · API failures · OOM
- CRITICAL / HIGH / MEDIUM / LOW severity triage
- Hourly timeline — spot incident peaks instantly
- Slow query ranking by duration
- JSON export for downstream tooling
- Zero external dependencies

## Project Structure
```
log-analyzer/
├── main.py
├── analyzer.py
├── reporter.py
├── sample_generator.py
├── tests/test_analyzer.py
└── README.md
```

## CLI Options
| Flag | Description |
|---|---|
| `--file PATH` | Log file to analyze |
| `--generate-sample` | Create demo log and analyze |
| `--json-out PATH` | Save JSON report |
| `--severity LEVEL` | Filter: CRITICAL / HIGH / MEDIUM / LOW |

**Author:** Prateek Arora — Production Engineer · 5 years at Shiprocket
[github.com/Prateek-Aroraa](https://github.com/Prateek-Aroraa)