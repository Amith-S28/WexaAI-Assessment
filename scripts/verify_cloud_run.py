import sys
import json
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent

def main():
    p = REPO_ROOT / "CloudRun" / "results" / "benchmark_results.json"
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)

    expected_dbs = [
        "CognoDB Cloud",
        "Neo4j AuraDB",
        "Memgraph Cloud",
        "FalkorDB Cloud",
        "ArangoDB Oasis"
    ]
    expected_queries = [
        "point_lookup",
        "indexed_lookup",
        "traversal_1_hop",
        "traversal_2_hop",
        "traversal_3_hop",
        "aggregation"
    ]
    expected_concurrency = ["1", "10", "40"]

    print("========================================================================")
    print("                CLOUD RUN TELEMETRY & STATISTICAL AUDIT                 ")
    print("========================================================================")
    print(f"Total Databases in Dataset: {len(data.keys())}")
    
    all_passed = True
    
    for db_name in expected_dbs:
        if db_name not in data:
            print(f"[FAIL] Missing Database: {db_name}")
            all_passed = False
            continue
            
        db = data[db_name]
        ingest = db.get("ingest", {})
        nodes = ingest.get("nodes_ingested", 0)
        edges = ingest.get("edges_ingested", 0)
        wall_clock = ingest.get("total_ingest_wall_clock_sec", 0)
        rtt = db.get("baseline_rtt_ms", 0)
        
        print(f"\n--- {db_name.upper()} ---")
        print(f"  • Baseline Ping RTT : {rtt:.2f} ms")
        print(f"  • Ingest Volume     : {nodes:,} nodes | {edges:,} edges in {wall_clock:.2f}s")
        print(f"  • Ingest Rates      : {ingest.get('nodes_per_sec', 0):.1f} nodes/s | {ingest.get('edges_per_sec', 0):.1f} edges/s")
        
        if nodes != 148587 or edges != 350000:
            print(f"  [ERROR] Ingest count mismatch (Expected 148,587 / 350,000)")
            all_passed = False
            
        # Verify Queries
        queries = db.get("queries", {})
        print("  • Query Latency Workloads (100 Iterations Each):")
        for qk in expected_queries:
            q = queries.get(qk, {})
            cnt = q.get("count", 0)
            p50 = q.get("p50_ms", 0)
            p95 = q.get("p95_ms", 0)
            p99 = q.get("p99_ms", 0)
            std = q.get("stddev_ms", 0)
            qps = q.get("qps", 0)
            raw_len = len(q.get("raw_latencies_ms", []))
            
            if cnt != 100 or raw_len != 100:
                print(f"    [FAIL] {qk:30}: count={cnt}, raw_len={raw_len}")
                all_passed = False
            else:
                print(f"    ✓ {qk:30}: p50={p50:6.2f}ms | p95={p95:6.2f}ms | p99={p99:6.2f}ms | std={std:5.2f}ms | QPS={qps:4.2f}")
                
        # Verify Concurrency
        conc = db.get("concurrency", {})
        print("  • Concurrency & ACID Transactions (80% Read / 20% Write):")
        for ck in expected_concurrency:
            c_key = f"concurrency_{ck}_clients"
            c = conc.get(c_key, {})
            qps = c.get("qps", 0)
            succ = c.get("success_count", 0)
            fail = c.get("fail_count", 0)
            p50 = c.get("p50_ms", 0)
            p95 = c.get("p95_ms", 0)
            
            if fail != 0 or succ <= 0:
                print(f"    [FAIL] Worker {ck:2}: Succ={succ}, Fail={fail}")
                all_passed = False
            else:
                print(f"    ✓ Concurrency [{ck:2} Workers]: QPS={qps:5.2f} | p50={p50:7.2f}ms | p95={p95:7.2f}ms | (Success: {succ:4}, Fail: {fail})")

    # Check Assets
    assets_dir = REPO_ROOT / "CloudRun" / "assets"
    expected_assets = [
        "architectural_tradeoff_quadrant.png",
        "cold_vs_warm_latency.png",
        "comprehensive_benchmark_matrix.png",
        "concurrency_p95_latency.png",
        "concurrency_scaling_qps.png",
        "concurrency_speedup_factor.png",
        "ingestion_throughput.png",
        "jitter_tail_latency_comparison.png",
        "radar_performance_profile.png",
        "traversal_latency_comparison.png"
    ]
    
    print("\n========================================================================")
    print("                    ASSET INTEGRITY & CHART VERIFICATION                ")
    print("========================================================================")
    for asset in expected_assets:
        ap = assets_dir / asset
        if ap.exists() and ap.stat().st_size > 10000:
            print(f"  ✓ Found valid chart: {asset:40} ({ap.stat().st_size / 1024:.1f} KB)")
        else:
            print(f"  ✗ Missing or corrupt asset: {asset}")
            all_passed = False
            
    print("\n========================================================================")
    if all_passed:
        print("  🎉 VERIFICATION RESULT: 100% COMPLETE & PASSING (READY FOR LOCAL RUN)")
    else:
        print("  ⚠️ VERIFICATION RESULT: ISSUES DETECTED")
    print("========================================================================")

if __name__ == "__main__":
    main()
