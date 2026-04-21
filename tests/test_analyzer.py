import sys, os, tempfile, pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from analyzer import LogAnalyzer

def tmp(lines):
    tf = tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False)
    tf.write("\n".join(lines)+"\n"); tf.close(); return tf.name

def test_http500(): assert any(i.category=="http_error" for i in LogAnalyzer().analyze(tmp(["2024-01-01 10:00:00 ERROR HTTP/1.1 500 Internal Server Error"])).incidents)
def test_timeout(): assert any(i.category=="timeout"    for i in LogAnalyzer().analyze(tmp(["2024-01-01 10:00:00 WARN Connection timed out (ETIMEDOUT)"])).incidents)
def test_exception(): assert any(i.severity=="CRITICAL" for i in LogAnalyzer().analyze(tmp(["2024-01-01 10:00:00 FATAL NullPointerException: order_id is null"])).incidents)
def test_slow_query():
    r = LogAnalyzer().analyze(tmp(["2024-01-01 10:00:00 WARN slow query: execution time 3400ms — SELECT *"]))
    assert len(r.slow_queries) > 0 and r.slow_queries[0]["duration_ms"] == 3400.0
def test_clean_log(): assert len(LogAnalyzer().analyze(tmp(["2024-01-01 10:00:00 INFO Service started","2024-01-01 10:00:05 INFO Health check passed"])).incidents) == 0
def test_dedup():
    lines = ["2024-01-01 10:00:00 FATAL NullPointerException: order_id is null"] * 20
    assert len(LogAnalyzer(deduplicate=True).analyze(tmp(lines)).incidents) <= 5
def test_no_dedup():
    lines = ["2024-01-01 10:00:00 FATAL NullPointerException: order_id is null"] * 20
    assert len(LogAnalyzer(deduplicate=False).analyze(tmp(lines)).incidents) == 20