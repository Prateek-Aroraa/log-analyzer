import re
from datetime import datetime
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Incident:
    line_number:  int
    timestamp:    Optional[str]
    severity:     str
    category:     str
    message:      str
    matched_text: str

    def to_dict(self):
        return {
            "line": self.line_number, "time": self.timestamp,
            "severity": self.severity, "category": self.category,
            "message": self.message[:200], "match": self.matched_text[:100],
        }

@dataclass
class AnalysisResult:
    file_path:    str
    total_lines:  int
    incidents:    List[Incident] = field(default_factory=list)
    slow_queries: list           = field(default_factory=list)
    timeline:     dict           = field(default_factory=dict)
    error_freq:   dict           = field(default_factory=dict)
    analyzed_at:  str            = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def by_severity(self):
        counts = Counter(i.severity for i in self.incidents)
        return {s: counts.get(s, 0) for s in ("CRITICAL","HIGH","MEDIUM","LOW")}

    @property
    def by_category(self):
        return dict(Counter(i.category for i in self.incidents))

PATTERNS = [
    {"name":"http_5xx",    "regex": re.compile(r'HTTP[/ ]\S*\s+(5\d{2})\b'),                                              "severity":"HIGH",     "category":"http_error"},
    {"name":"exception",   "regex": re.compile(r'\b(Exception|FATAL|CRITICAL|Traceback|panic)\b', re.I),                    "severity":"CRITICAL", "category":"exception"},
    {"name":"timeout",     "regex": re.compile(r'\b(timeout|timed.?out|ETIMEDOUT|connection.?reset|deadline.?exceeded)\b', re.I), "severity":"HIGH", "category":"timeout"},
    {"name":"slow_query",  "regex": re.compile(r'(slow.?query|query.?took|execution.?time)[^\d]*([\d.]+)\s*(ms|s)\b', re.I), "severity":"MEDIUM", "category":"slow_query"},
    {"name":"api_failure", "regex": re.compile(r'\b(API|endpoint|request)\b.{0,30}\b(fail|error|unavailable|refused)\b', re.I), "severity":"HIGH", "category":"api_failure"},
    {"name":"oom",         "regex": re.compile(r'\b(OutOfMemory|OOM|heap.?space|memory.?exhausted)\b', re.I),               "severity":"CRITICAL", "category":"exception"},
]
TIMESTAMP_RE = re.compile(r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})')

class LogAnalyzer:
    def __init__(self, deduplicate=True):
        self.deduplicate = deduplicate
        self._seen = Counter()

    def analyze(self, file_path):
        result = AnalysisResult(file_path=file_path, total_lines=0)
        timeline = defaultdict(int)
        slow_queries = []
        with open(file_path, "r", errors="replace") as fh:
            for lineno, raw_line in enumerate(fh, start=1):
                result.total_lines = lineno
                line = raw_line.strip()
                if not line: continue
                timestamp = self._extract_timestamp(line)
                for inc in self._match_patterns(lineno, line, timestamp):
                    result.incidents.append(inc)
                    if timestamp:
                        timeline[timestamp[:13]] += 1
                    if inc.category == "slow_query":
                        dur = self._extract_duration(line)
                        if dur:
                            slow_queries.append({"line": lineno, "duration_ms": dur, "context": line[:180]})
        result.timeline     = dict(sorted(timeline.items()))
        result.slow_queries = sorted(slow_queries, key=lambda x: x["duration_ms"], reverse=True)
        result.error_freq   = dict(Counter(i.message[:80] for i in result.incidents).most_common(10))
        return result

    def _extract_timestamp(self, line):
        m = TIMESTAMP_RE.search(line)
        return m.group(1) if m else None

    def _match_patterns(self, lineno, line, ts):
        found = []
        for pat in PATTERNS:
            m = pat["regex"].search(line)
            if not m: continue
            key = f"{pat['category']}:{line[:80]}"
            if self.deduplicate and self._seen[key] >= 5: continue
            self._seen[key] += 1
            found.append(Incident(lineno, ts, pat["severity"], pat["category"], line, m.group(0)))
            break
        return found

    def _extract_duration(self, line):
        m = re.search(r'([\d.]+)\s*(ms|s)\b', line, re.I)
        if not m: return None
        val, unit = float(m.group(1)), m.group(2).lower()
        return val * 1000 if unit == "s" else val