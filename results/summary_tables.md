### 📊 Ingestion & Indexing Performance

| Database | Paradigm | Index Build (ms) | Node Ingest (n/s) | Edge Ingest (e/s) | Wall-Clock (s) |
|:---|:---|:---:|:---:|:---:|:---:|
| **CognoDB Cloud** | Cloud Managed Native Graph (Bolt Protocol) | 816.3 ms | 1,799.7 | 2,914.4 | 2.83s |
| **Neo4j AuraDB** | JVM Labeled Property Graph (LPG) | 681.34 ms | 2,090.6 | 3,094.6 | 2.57s |
| **Memgraph Cloud** | In-Memory C++ Native Graph | 743.36 ms | 2,438.1 | 3,707.1 | 2.17s |
| **FalkorDB Cloud** | GraphBLAS Sparse Linear Algebra (C) | 446.36 ms | 1,825.5 | 4,190.3 | 2.29s |
| **ArangoDB Oasis** | Multi-Model RocksDB (AQL Graph) | 479.59 ms | 460.5 | 2,096.0 | 6.73s |

### ⚡ Query Latency Profile (Percentiles in Milliseconds)

| Database | Point Lookup (p50 / p95) | 1-Hop Traversal (p50 / p95) | 2-Hop Traversal (p50 / p95) | 3-Hop Traversal (p50 / p95) | Degree Aggregation (p50) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **CognoDB Cloud** | 293.74 / 309.99 | 289.85 / 308.43 | 294.03 / 311.1 | 298.13 / 408.52 | 282.39 ms |
| **Neo4j AuraDB** | 224.01 / 683.21 | 277.1 / 897.83 | 269.65 / 394.06 | 276.56 / 386.65 | 265.82 ms |
| **Memgraph Cloud** | 277.74 / 280.93 | 225.26 / 384.15 | 226.87 / 376.16 | 226.0 / 374.45 | 229.12 ms |
| **FalkorDB Cloud** | 227.63 / 322.8 | 222.46 / 389.1 | 263.32 / 329.26 | 262.73 / 361.15 | 248.07 ms |
| **ArangoDB Oasis** | 261.69 / 387.58 | 249.44 / 381.01 | 263.43 / 376.12 | 263.16 / 369.19 | 221.31 ms |

### 📈 Concurrency & Scalability Matrix (Mixed 80% Read / 20% Write)

| Database | 1 Client (QPS / p95) | 10 Clients (QPS / p95) | 40 Clients (QPS / p95) | Scalability Factor (40x / 1x) |
|:---|:---:|:---:|:---:|:---:|
| **CognoDB Cloud** | 0.77 QPS (1820.77ms) | 7.45 QPS (2693.75ms) | 28.28 QPS (2616.94ms) | **36.7x** |
| **Neo4j AuraDB** | 0.81 QPS (1825.55ms) | 7.14 QPS (3717.27ms) | 28.79 QPS (2416.11ms) | **35.5x** |
| **Memgraph Cloud** | 0.88 QPS (1361.81ms) | 7.56 QPS (2406.36ms) | 32.52 QPS (2555.03ms) | **37.0x** |
| **FalkorDB Cloud** | 1.3 QPS (1874.43ms) | 16.51 QPS (745.36ms) | 59.21 QPS (681.68ms) | **45.5x** |
| **ArangoDB Oasis** | 3.63 QPS (386.18ms) | 33.46 QPS (391.88ms) | 26.12 QPS (2978.25ms) | **7.2x** |