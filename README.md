# Wexa AI Graph Database Empirical Benchmark Suite

An empirical systems performance evaluation comparing **CognoDB Cloud** against open-source and managed graph database engines: **FalkorDB**, **Memgraph**, **Neo4j 5**, **ArangoDB**, **KùzuDB**, **JanusGraph**, and **ArcadeDB**.

---

## Executive Report & Key Artifacts

The complete analytical synthesis, high-resolution infographics, and interactive dashboards are located in the [`Final Report/`](./Final%20Report/) directory:

- **Executive Whitepaper:** [`Final Report/FINAL_REPORT.md`](./Final%20Report/FINAL_REPORT.md)
- **Interactive Executive Dashboard:** [`Final Report/index.html`](./Final%20Report/index.html) *(Self-contained, with zoomable lightbox and RTT normalization)*
- **Publication-Grade Infographics:** [`Final Report/assets/`](./Final%20Report/assets/)
- **Consolidated Summary Tables:** [`Final Report/summary_tables.md`](./Final%20Report/summary_tables.md)

---

## Architectural Taxonomy

| Engine | Storage Backend | Computational Paradigm | Traversal Model | Primary Interface |
| :--- | :--- | :--- | :--- | :--- |
| **CognoDB Cloud** | Distributed Native Graph Store | Cloud Native Managed Engine | Direct Pointer Chasing | Bolt Protocol (`bolt+s://`) |
| **FalkorDB** | Redis In-Memory Module | GraphBLAS Sparse Linear Algebra | Matrix Multiplications ($A \times A$) | Redis Protocol / openCypher |
| **Memgraph** | In-Memory C++ Adjacency | Direct Native Pointer Chasing | Unindexed Memory Dereferencing | Bolt Protocol / openCypher |
| **Neo4j 5** | Record Store + Page Cache | JVM Labeled Property Graph | Doubly-Linked Relationship Chains | Bolt Protocol / Cypher |
| **ArangoDB** | RocksDB LSM-Tree Engine | Multi-Model Document + Edge Graph | Index-Backed Edge Iteration | HTTP REST / AQL |
| **KùzuDB** | Columnar On-Disk / Memory | In-Process Columnar Graph Engine | Vectorized Columnar Scanning | Embedded C++ / Python / Cypher |
| **JanusGraph** | BerkeleyJE / Storage Plugins | TinkerPop Gremlin Graph Engine | Vertex-Centric Adjacency Iteration | Gremlin WebSocket |
| **ArcadeDB** | Hybrid Document + Buckets | Multi-Model openCypher Engine | Bucket-Linked Edge Iteration | HTTP / openCypher |

---

## Summary Performance Matrix

### Local Engine Benchmark (8 Engines + CognoDB Baseline)

| Database | Baseline RTT | Index Build | Node Ingest | Edge Ingest | 1-Hop p50 (Net) | 3-Hop p50 (Net) | 40-Client QPS | Degree Agg (Net) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CognoDB Cloud** | 310.68 ms | 608.41 ms | 1,483.0 n/s | 3,565.6 e/s | **0.00 ms** *(raw: 310.16)* | **0.00 ms** *(raw: 306.62)* | 9.11 QPS | 1,287.15 ms |
| **FalkorDB** | 1.69 ms | **3.45 ms** | **41,924.5 n/s** | 10,190.7 e/s | **0.00 ms** *(raw: 1.09)* | **0.00 ms** *(raw: 1.08)* | **766.87 QPS** | 295.94 ms |
| **Memgraph** | 2.12 ms | 9.09 ms | 32,261.5 n/s | **37,930.3 e/s** | **0.00 ms** *(raw: 1.42)* | **0.00 ms** *(raw: 1.68)* | 183.15 QPS | 147.65 ms |
| **Neo4j 5 Community** | 6.85 ms | 684.77 ms | 7,541.5 n/s | 9,437.5 e/s | **0.00 ms** *(raw: 3.92)* | **0.00 ms** *(raw: 3.63)* | 119.95 QPS | 309.33 ms |
| **ArangoDB** | 45.94 ms | 94.27 ms | 27,189.0 n/s | 21,465.1 e/s | **0.00 ms** *(raw: 43.71)* | **0.00 ms** *(raw: 43.75)* | 463.97 QPS | 121.39 ms |
| **JanusGraph** | 50.78 ms | 88.74 ms | 853.8 n/s | 1,266.3 e/s | 4.55 ms *(raw: 55.33)* | 1.90 ms *(raw: 52.68)* | 172.86 QPS | 453.61 ms |
| **ArcadeDB** | 4.92 ms | 408.87 ms | 3,023.7 n/s | 381.2 e/s | 46.98 ms *(raw: 51.90)* | 55.89 ms *(raw: 60.81)* | 2.54 QPS | **47.90 ms** |
| **KùzuDB** | 7.05 ms | 219.78 ms | 191.5 n/s | 149.3 e/s | 44.69 ms *(raw: 51.74)* | 48.04 ms *(raw: 55.09)* | 34.83 QPS | 76.92 ms |

*(Net Latency = Raw Wall-Clock p50 minus Baseline Network RTT, isolating true server-side execution time).*

---

## Repository Structure

```
WEXA/
├── Final Report/                          # Publication-grade deliverables
│   ├── index.html                         # Interactive executive dashboard
│   ├── final_report.html                  # Standalone report mirror
│   ├── FINAL_REPORT.md                    # In-depth executive whitepaper
│   ├── summary_tables.md                  # Consolidated performance tables
│   └── assets/                            # High-resolution vector diagrams
│       ├── 01_ingestion_throughput.png
│       ├── 02_traversal_latency_net_vs_raw.png
│       ├── 03_concurrency_scaling_curves.png
│       ├── 04_concurrency_p95_latency.png
│       ├── 05_architectural_quadrant.png
│       ├── 06_jitter_tail_variance.png
│       ├── 07_radar_performance_profile.png
│       └── 08_benchmark_heatmap_matrix.png
├── Local Run/                             # Local benchmark results & telemetry
│   ├── benchmark_results.json             # Raw measurement JSON arrays
│   ├── summary_tables.md
│   └── assets/
├── CloudRun/                              # Cloud managed tiers benchmark
│   ├── benchmark_results.json
│   ├── summary_tables.md
│   └── assets/
├── benchmarks/                            # Core benchmark execution harness
│   ├── benchmark_suite.py                 # Multi-workload orchestrator
│   ├── config.py                          # Database connection configuration
│   ├── metrics.py                         # Percentile & statistical calculations
│   └── adapters/                          # Database driver adapters
│       ├── cognodb_adapter.py
│       ├── falkordb_adapter.py
│       ├── memgraph_adapter.py
│       ├── neo4j_adapter.py
│       ├── arangodb_adapter.py
│       ├── kuzudb_adapter.py
│       ├── janusgraph_adapter.py
│       └── arcadedb_adapter.py
├── scripts/                               # Automation & reporting scripts
│   ├── generate_final_report_suite.py     # Final Report generator
│   ├── generate_all_diagrams_and_reports.py
│   ├── embed_charts_in_dashboards.py
│   ├── download_dataset_fast.py
│   ├── test_connections.py
│   └── test_adapters.py
├── docker-compose.benchmark.yml           # Multi-database container environment
└── requirements.txt                       # Python dependencies
```

---

## Reproducibility & Setup

### 1. Prerequisites
- Python 3.11+
- Docker & Docker Compose

### 2. Environment Installation
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Launching Local Database Containers
```bash
docker compose -f docker-compose.benchmark.yml up -d
```

### 4. Running the Benchmark Suite
```bash
# Verify database connections
python scripts/test_connections.py

# Execute full benchmark run
python run_benchmark.py
```

### 5. Regenerating Reports & Visualizations
```bash
python scripts/generate_final_report_suite.py
```

---

## Methodology Highlights

- **Standardized Topology:** Evaluated on the Stanford SNAP Pokec social network topology (1.63M nodes, 30.6M relationships).
- **Resource Constraints:** Local database containers are standardized with identical CPU (0.50 vCPU) and RAM (512MB) limits.
- **Statistical Rigor:** All queries undergo warm-up cycles before executing 100+ recorded iterations to compute exact p50, p90, p95, p99, and jitter variance.
- **RTT Normalization:** Baseline network ping RTT is recorded and subtracted to report true server-side compute times alongside raw wall-clock latency.
