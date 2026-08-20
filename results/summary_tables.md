### 📊 Ingestion & Indexing Performance

| Database | Paradigm | Index Build (ms) | Node Ingest (n/s) | Edge Ingest (e/s) | Wall-Clock (s) |
|:---|:---|:---:|:---:|:---:|:---:|
| **CognoDB Cloud** | Cloud Managed Native Graph (Bolt Protocol) | 533.81 ms | 2,317.7 | 3,946.5 | 2.13s |
| **Neo4j AuraDB** | JVM Labeled Property Graph (LPG) | 459.43 ms | 2,686.4 | 5,135.2 | 1.72s |
| **Memgraph Cloud** | In-Memory C++ Native Graph | 452.27 ms | 2,571.8 | 6,042.4 | 1.6s |
| **FalkorDB Cloud** | GraphBLAS Sparse Linear Algebra (C) | 447.63 ms | 2,904.6 | 6,424.7 | 1.47s |
| **ArangoDB Oasis** | Multi-Model RocksDB (AQL Graph) | 459.13 ms | 1,391.5 | 3,824.9 | 2.74s |

### ⚡ Query Latency Profile (Percentiles in Milliseconds)

| Database | Point Lookup (p50 / p95) | 1-Hop Traversal (p50 / p95) | 2-Hop Traversal (p50 / p95) | 3-Hop Traversal (p50 / p95) | Degree Aggregation (p50) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **CognoDB Cloud** | 266.87 / 270.63 | 266.35 / 267.81 | 265.91 / 267.2 | 320.1 / 1175.02 | 275.58 ms |
| **Neo4j AuraDB** | 229.12 / 237.42 | 228.04 / 229.42 | 227.83 / 847.99 | 227.91 / 229.69 | 228.43 ms |
| **Memgraph Cloud** | 225.07 / 226.54 | 225.61 / 597.45 | 226.28 / 336.98 | 225.25 / 227.14 | 225.87 ms |
| **FalkorDB Cloud** | 225.45 / 567.35 | 226.13 / 228.34 | 224.92 / 232.24 | 225.48 / 227.18 | 227.43 ms |
| **ArangoDB Oasis** | 230.27 / 231.38 | 229.33 / 276.4 | 231.18 / 243.49 | 229.91 / 256.84 | 231.92 ms |

### 📈 Concurrency & Scalability Matrix (Mixed 80% Read / 20% Write)

| Database | 1 Client (QPS / p95) | 10 Clients (QPS / p95) | 40 Clients (QPS / p95) | Scalability Factor (40x / 1x) |
|:---|:---:|:---:|:---:|:---:|
| **CognoDB Cloud** | 0.84 QPS (1575.54ms) | 8.55 QPS (2056.67ms) | 30.52 QPS (2199.39ms) | **36.3x** |
| **Neo4j AuraDB** | 0.88 QPS (2057.79ms) | 9.42 QPS (1863.4ms) | 33.96 QPS (2144.82ms) | **38.6x** |
| **Memgraph Cloud** | 1.1 QPS (914.09ms) | 9.42 QPS (1773.32ms) | 40.68 QPS (922.96ms) | **37.0x** |
| **FalkorDB Cloud** | 2.19 QPS (463.77ms) | 17.39 QPS (666.63ms) | 66.01 QPS (459.49ms) | **30.1x** |
| **ArangoDB Oasis** | 4.19 QPS (259.76ms) | 15.32 QPS (1120.29ms) | 1.36 QPS (39279.37ms) | **0.3x** |

### 🌐 Network RTT vs Server-Side Net Compute Time (p50)

| Database | Baseline Network RTT | 1-Hop p50 (Gross) | 1-Hop Net Compute | 2-Hop Net Compute | 3-Hop Net Compute |
|:---|:---:|:---:|:---:|:---:|:---:|
| **CognoDB Cloud** | 264.65 ms | 266.35 ms | **1.70 ms** | **1.26 ms** | **55.45 ms** |
| **Neo4j AuraDB** | 230.72 ms | 228.04 ms | **0.00 ms** | **0.00 ms** | **0.00 ms** |
| **Memgraph Cloud** | 225.29 ms | 225.61 ms | **0.32 ms** | **0.99 ms** | **0.00 ms** |
| **FalkorDB Cloud** | 225.85 ms | 226.13 ms | **0.28 ms** | **0.00 ms** | **0.00 ms** |
| **ArangoDB Oasis** | 227.61 ms | 229.33 ms | **1.72 ms** | **3.57 ms** | **2.30 ms** |