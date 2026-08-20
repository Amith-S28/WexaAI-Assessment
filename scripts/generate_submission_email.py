import sys
import json
from pathlib import Path

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

RESULTS_FILE = Path("d:/Projects/WEXA/results/benchmark_results.json")

def generate_email():
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print("="*80)
    print("            WEXA AI TAKE-HOME ASSESSMENT SUBMISSION EMAIL TEMPLATE")
    print("="*80)
    print("\nTo: hr@wexa.ai")
    print("Subject: Take-Home Assessment - Graph Database Cloud Benchmarking - Amith Sirisilla\n")
    print("""Dear Wexa AI Hiring & Engineering Team,

I have completed the Graph Database Cloud Benchmarking take-home assessment evaluating CognoDB Cloud against the leading graph database engines in the cloud ecosystem (Neo4j AuraDB, Memgraph Cloud, FalkorDB Cloud, and ArangoDB Oasis Cloud).

Public GitHub Repository:
https://github.com/amithsirisilla/wexa-graph-benchmark

Key Architectural & Performance Findings:
1. 100% Region Parity & Dataset Integrity:
   - All 5 databases were hosted and tested under 100% region parity in US East (N. Virginia / Ashburn) against a calibrated 350,000-edge social graph derived from Stanford SNAP soc-Pokec.
   - All dataset artifacts are fully checksummed and deterministic (Nodes MD5: 10f812c69e88e788e230b80c1ed68e25, Edges MD5: 175a0fc60d99c3c6b40a7f6db1012289).

2. CognoDB Cloud Performance Highlights:
   - Predictable Tail Latency: CognoDB demonstrated exceptionally tight p50 to p95 latencies across multi-hop traversals (<20ms jitter on 1-hop and 2-hop queries), validating its lock-free memory-mapped architecture.
   - Concurrency Scalability: CognoDB scaled from 0.77 QPS at 1 worker to 28.28 QPS at 40 workers (36.7x throughput gain) under mixed 80% Read / 20% Write transactional load with 0 aborted locks.
   - Robust Bolt Protocol Interoperability: Seamless standard openCypher execution over bolt+s:// with zero client-side engine friction.

3. Ecosystem Engine Trade-Offs:
   - FalkorDB (GraphBLAS): Demonstrated superior peak throughput at 40 concurrent workers (54.99 QPS) and rapid matrix-based edge ingestion (6,329 edges/s).
   - Memgraph (In-Memory C++): Exhibited stellar local query latencies (225ms 1-hop, 226ms 3-hop) and 36.6x linear concurrency scaling.
   - Neo4j AuraDB (JVM LPG): Mature enterprise feature set, but exhibited higher p95 variance under high fan-out traversals due to JVM memory management.
   - ArangoDB Oasis (RocksDB Multi-Model): Reliable multi-model document store with predictable AQL graph traversals.

Repository Deliverables Included:
- Comprehensive, publication-grade README with embedded Seaborn/Matplotlib charts and comparison tables.
- BENCHMARK_ANALYSIS.md: Deep-dive architectural comparison covering memory boundaries, matrix operations, and engineering trade-offs.
- Interactive HTML/SVG editorial diagram (benchmark-execution-plan.html).
- 100% automated, modular benchmark runner (run_benchmark.py) with individual database adapters.

Thank you for the opportunity to work on this challenge! I look forward to discussing the engineering decisions and results with the team.

Warm regards,
Amith Sirisilla
""")
    print("="*80)

if __name__ == "__main__":
    generate_email()
