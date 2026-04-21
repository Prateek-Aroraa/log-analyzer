import random
from datetime import datetime, timedelta
from pathlib import Path

SERVICES  = ["order-service","shipment-service","tracking-api","payment-gateway","courier-integration"]
ENDPOINTS = ["/api/v2/orders","/api/v2/shipments","/api/v3/tracking","/api/v2/rates","/api/v2/manifest"]
COURIERS  = ["BlueDart","FedEx","Delhivery","Ecom Express"]
EXCEPTIONS= ["NullPointerException: order_id cannot be null","DatabaseException: max connection pool size reached",
              "NullPointerException: shipment_weight is null","OutOfMemoryError: Java heap space exhausted"]
SLOW_SQL  = ["SELECT * FROM shipments WHERE courier_id IN (SELECT id FROM couriers WHERE region='North')",
             "UPDATE orders SET status='dispatched' WHERE created_at < '2023-01-01'",
             "SELECT m.name, COUNT(o.id) FROM merchants m JOIN orders o ON o.merchant_id=m.id GROUP BY m.id"]
NORMAL    = ["INFO  Service started successfully on port 8080","INFO  Connected to MySQL: orders_db (pool=20)",
             "INFO  Redis cache connected — hit rate 94%","INFO  Health check passed — all dependencies OK"]

def generate_sample_log(output_path="logs/sample.log", n_events=120):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    base = datetime(2024, 3, 15, 8, 0, 0)
    lines = []
    for i in range(n_events):
        ts   = (base + timedelta(minutes=i*3+random.randint(0,2))).strftime("%Y-%m-%d %H:%M:%S")
        svc  = random.choice(SERVICES)
        roll = random.random()
        if   roll < 0.35: lines.append(f"{ts} [{svc}] {random.choice(NORMAL)}")
        elif roll < 0.50:
            code = random.choice([500,502,503,504])
            lines.append(f"{ts} [{svc}] ERROR HTTP/1.1 {code} Internal Server Error — {random.choice(ENDPOINTS)}")
        elif roll < 0.62:
            exc = random.choice(EXCEPTIONS)
            lines.append(f"{ts} [{svc}] {'FATAL' if 'OutOfMemory' in exc else 'ERROR'} {exc}")
        elif roll < 0.72:
            lines.append(f"{ts} [{svc}] WARN  Connection timed out (ETIMEDOUT after 5000ms)")
        elif roll < 0.82:
            lines.append(f"{ts} [{svc}] WARN  slow query: execution time {random.randint(800,8000)}ms — {random.choice(SLOW_SQL)[:80]}")
        elif roll < 0.92:
            lines.append(f"{ts} [{svc}] ERROR API failure: {random.choice(COURIERS)} integration error")
        else:
            lines.append(f"{ts} [{svc}] WARN  HTTP/1.1 404 Not Found — {random.choice(ENDPOINTS)}")
    with open(output_path, "w") as fh: fh.write("\n".join(lines)+"\n")
    print(f"  📝  Sample log generated → {output_path}  ({len(lines)} lines)")
    return output_path