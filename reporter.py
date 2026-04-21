import json
from datetime import datetime
from analyzer import AnalysisResult

R="[91m"; Y="[93m"; G="[92m"; B="[94m"; W="[97m"; DIM="[2m"; RST="[0m"
SEV_COLOR={"CRITICAL":R,"HIGH":R,"MEDIUM":Y,"LOW":DIM}
SEV_ICON ={"CRITICAL":"⛔","HIGH":"🔴","MEDIUM":"🟡","LOW":"⚪"}

class ConsoleReporter:
    def render(self, result):
        self._header(result); self._severity_table(result); self._category_breakdown(result)
        self._timeline(result); self._slow_queries(result); self._recurring_errors(result); self._footer(result)

    def _header(self, r):
        print(f"\n{B}{'═'*66}{RST}")
        print(f"{W}  🔍  LOG ANALYZER  —  Production Incident Intelligence{RST}")
        print(f"{DIM}  File: {r.file_path}  |  Lines: {r.total_lines:,}  |  Incidents: {len(r.incidents):,}{RST}")
        print(f"{B}{'═'*66}{RST}")

    def _severity_table(self, r):
        print(f"\n{W}  SEVERITY BREAKDOWN{RST}"); print(f"  {'─'*40}")
        for s, count in r.by_severity.items():
            if count == 0: continue
            print(f"  {SEV_ICON[s]}  {s:<10} {count:>5}   {SEV_COLOR[s]}{'█'*min(count,30)}{RST}")

    def _category_breakdown(self, r):
        if not r.by_category: return
        print(f"\n{W}  CATEGORY BREAKDOWN{RST}"); print(f"  {'─'*40}")
        for cat, count in sorted(r.by_category.items(), key=lambda x: -x[1]):
            print(f"  ▸ {cat:<20} {count:>5}")

    def _timeline(self, r):
        if not r.timeline: return
        peak = max(r.timeline, key=r.timeline.get)
        print(f"\n{W}  ERROR TIMELINE{RST}"); print(f"  {'─'*40}")
        for hour, count in sorted(r.timeline.items())[-8:]:
            flag = f"  {R}← PEAK{RST}" if hour == peak else ""
            print(f"  {DIM}{hour}{RST}  {Y}{'▓'*min(count,25)}{RST} {count}{flag}")

    def _slow_queries(self, r):
        if not r.slow_queries: return
        print(f"\n{W}  SLOWEST QUERIES{RST}"); print(f"  {'─'*40}")
        for sq in r.slow_queries[:5]:
            print(f"  {Y}⏱  {sq['duration_ms']:.0f}ms{RST}  line {sq['line']}  {DIM}{sq['context'][:55]}…{RST}")

    def _recurring_errors(self, r):
        if not r.error_freq: return
        print(f"\n{W}  TOP RECURRING ERRORS{RST}"); print(f"  {'─'*40}")
        for msg, count in list(r.error_freq.items())[:6]:
            print(f"  {R}[{count}×]{RST}  {DIM}{msg[:65]}…{RST}")

    def _footer(self, r):
        sev = r.by_severity
        status = "🚨 ACTION REQUIRED" if sev["CRITICAL"] > 0 else ("⚠  REVIEW NEEDED" if sev["HIGH"] > 0 else "✅ STABLE")
        print(f"\n{'─'*66}"); print(f"  STATUS: {W}{status}{RST}"); print(f"{'─'*66}\n")

class JsonReporter:
    def write(self, result, path):
        payload = {
            "meta": {"file": result.file_path, "analyzed_at": result.analyzed_at, "total_lines": result.total_lines, "total_incidents": len(result.incidents)},
            "summary": {"by_severity": result.by_severity, "by_category": result.by_category},
            "timeline": result.timeline, "slow_queries": result.slow_queries[:10],
            "top_errors": [{"message": k, "count": v} for k, v in result.error_freq.items()],
            "incidents": [i.to_dict() for i in result.incidents[:200]],
        }
        with open(path, "w") as fh: json.dump(payload, fh, indent=2)
        print(f"  💾  JSON report saved → {path}")