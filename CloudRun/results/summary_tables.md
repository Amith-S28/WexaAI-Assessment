### 📊 Ingestion & Indexing Performance

| Database | Paradigm | Index Build (ms) | Node Ingest (n/s) | Edge Ingest (e/s) | Wall-Clock (s) |
|:---|:---|:---:|:---:|:---:|:---:|
| **CognoDB Cloud** | Cloud Managed Native Graph (Bolt Protocol) | 608.41 ms | 1,483.0 | 3,565.6 | 198.35s |
| **Neo4j AuraDB** | JVM Labeled Property Graph (LPG) | 573.84 ms | 3,109.8 | 2,826.2 | 171.62s |
| **Memgraph Cloud** | In-Memory C++ Native Graph | 515.97 ms | 3,279.2 | 1,694.1 | 251.91s |
| **FalkorDB Cloud** | GraphBLAS Sparse Linear Algebra (C) | 470.96 ms | 1,282.6 | 3,940.4 | 204.67s |
| **ArangoDB Oasis** | Multi-Model RocksDB (AQL Graph) | 543.92 ms | 2,001.2 | 3,000.9 | 190.88s |

### ⚡ Query Latency Profile (Percentiles in Milliseconds)

| Database | Point Lookup (p50 / p95) | 1-Hop Traversal (p50 / p95) | 2-Hop Traversal (p50 / p95) | 3-Hop Traversal (p50 / p95) | Degree Aggregation (p50) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **CognoDB Cloud** | 309.0 / 472.42 | 310.16 / 445.86 | 295.39 / 320.34 | 306.62 / 370.98 | 1597.83 ms |
| **Neo4j AuraDB** | 263.48 / 292.97 | 262.99 / 280.23 | 264.1 / 289.94 | 273.53 / 283.73 | 339.39 ms |
| **Memgraph Cloud** | 251.03 / 267.35 | 260.03 / 278.2 | 234.14 / 265.26 | 262.1 / 275.52 | 359.07 ms |
| **FalkorDB Cloud** | 275.85 / 279.94 | 261.28 / 279.57 | 275.38 / 279.91 | 274.67 / 280.28 | 557.93 ms |
| **ArangoDB Oasis** | 263.05 / 295.11 | 265.35 / 422.01 | 226.33 / 238.38 | 225.63 / 523.26 | 510.46 ms |

### 📈 Concurrency & Scalability Matrix (Mixed 80% Read / 20% Write)

| Database | 1 Client (QPS / p95) | 10 Clients (QPS / p95) | 40 Clients (QPS / p95) | Scalability Factor (40x / 1x) |
|:---|:---:|:---:|:---:|:---:|
| **CognoDB Cloud** | 0.62 QPS (2347.15ms) | 4.81 QPS (4018.68ms) | 9.11 QPS (4605.79ms) | **14.7x** |
| **Neo4j AuraDB** | 0.73 QPS (2340.53ms) | 8.78 QPS (1917.2ms) | 27.84 QPS (2373.32ms) | **38.1x** |
| **Memgraph Cloud** | 1.0 QPS (1065.59ms) | 8.9 QPS (2070.29ms) | 35.37 QPS (2092.84ms) | **35.4x** |
| **FalkorDB Cloud** | 1.87 QPS (558.86ms) | 16.01 QPS (569.56ms) | 59.0 QPS (555.86ms) | **31.6x** |
| **ArangoDB Oasis** | 3.8 QPS (288.72ms) | 32.58 QPS (298.93ms) | 68.68 QPS (1347.16ms) | **18.1x** |

### 🌐 Network RTT vs Server-Side Net Compute Time (p50)

| Database | Baseline Network RTT | 1-Hop p50 (Gross) | 1-Hop Net Compute | 2-Hop Net Compute | 3-Hop Net Compute |
|:---|:---:|:---:|:---:|:---:|:---:|
| **CognoDB Cloud** | 310.68 ms | 310.16 ms | **0.00 ms** | **0.00 ms** | **0.00 ms** |
| **Neo4j AuraDB** | 246.74 ms | 262.99 ms | **16.25 ms** | **17.36 ms** | **26.79 ms** |
| **Memgraph Cloud** | 252.21 ms | 260.03 ms | **7.82 ms** | **0.00 ms** | **9.89 ms** |
| **FalkorDB Cloud** | 264.67 ms | 261.28 ms | **0.00 ms** | **10.71 ms** | **10.00 ms** |
| **ArangoDB Oasis** | 258.67 ms | 265.35 ms | **6.68 ms** | **0.00 ms** | **0.00 ms** |