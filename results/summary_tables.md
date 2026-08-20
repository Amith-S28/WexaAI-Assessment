### 📊 Ingestion & Indexing Performance

| Database | Paradigm | Index Build (ms) | Node Ingest (n/s) | Edge Ingest (e/s) | Wall-Clock (s) |
|:---|:---|:---:|:---:|:---:|:---:|
| **CognoDB Cloud** | Cloud Managed Native Graph (Bolt Protocol) | 602.19 ms | 2,158.3 | 3,067.7 | 2.56s |
| **Neo4j AuraDB** | JVM Labeled Property Graph (LPG) | 540.56 ms | 2,274.8 | 2,883.0 | 2.61s |
| **Memgraph Cloud** | In-Memory C++ Native Graph | 525.41 ms | 2,350.8 | 3,249.2 | 2.39s |
| **FalkorDB Cloud** | GraphBLAS Sparse Linear Algebra (C) | 525.1 ms | 2,383.7 | 4,992.0 | 1.84s |
| **ArangoDB Oasis** | Multi-Model RocksDB (AQL Graph) | 704.03 ms | 22.5 | 56.6 | 0.8s |

### ⚡ Query Latency Profile (Percentiles in Milliseconds)

| Database | Point Lookup (p50 / p95) | 1-Hop Traversal (p50 / p95) | 2-Hop Traversal (p50 / p95) | 3-Hop Traversal (p50 / p95) | Degree Aggregation (p50) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **CognoDB Cloud** | 293.9 / 310.21 | 293.32 / 310.66 | 293.28 / 309.56 | 290.17 / 308.8 | 296.12 ms |
| **Neo4j AuraDB** | 262.25 / 279.86 | 273.93 / 279.86 | 270.82 / 280.2 | 263.9 / 280.44 | 267.28 ms |
| **Memgraph Cloud** | 263.98 / 279.85 | 263.84 / 311.31 | 263.84 / 278.98 | 262.03 / 278.2 | 263.52 ms |
| **FalkorDB Cloud** | 265.13 / 280.41 | 275.37 / 279.48 | 263.34 / 279.2 | 264.35 / 279.6 | 262.03 ms |
| **ArangoDB Oasis** | 278.61 / 299.73 | 279.0 / 333.28 | 292.59 / 295.67 | 322.28 / 419.51 | 403.84 ms |

### 📈 Concurrency & Scalability Matrix (Mixed 80% Read / 20% Write)

| Database | 1 Client (QPS / p95) | 10 Clients (QPS / p95) | 40 Clients (QPS / p95) | Scalability Factor (40x / 1x) |
|:---|:---:|:---:|:---:|:---:|
| **CognoDB Cloud** | 0.84 QPS (1225.97ms) | 7.25 QPS (2428.69ms) | 29.44 QPS (2374.84ms) | **35.0x** |
| **Neo4j AuraDB** | 0.9 QPS (1542.67ms) | 7.46 QPS (2314.3ms) | 33.92 QPS (2092.11ms) | **37.7x** |
| **Memgraph Cloud** | 0.93 QPS (1097.78ms) | 8.78 QPS (2092.54ms) | 34.76 QPS (1872.06ms) | **37.4x** |
| **FalkorDB Cloud** | 1.8 QPS (558.9ms) | 15.56 QPS (574.03ms) | 54.91 QPS (559.6ms) | **30.5x** |
| **ArangoDB Oasis** | 3.22 QPS (450.48ms) | 30.56 QPS (467.1ms) | 33.82 QPS (2333.29ms) | **10.5x** |