### 📊 Ingestion & Indexing Performance

| Database | Paradigm | Index Build (ms) | Node Ingest (n/s) | Edge Ingest (e/s) | Wall-Clock (s) |
|:---|:---|:---:|:---:|:---:|:---:|
| **Neo4j AuraDB** | JVM Labeled Property Graph (LPG) | 684.77 ms | 7,541.5 | 9,437.5 | 56.79s |
| **Memgraph Cloud** | In-Memory C++ Native Graph | 9.09 ms | 32,261.5 | 37,930.3 | 13.83s |
| **FalkorDB Cloud** | GraphBLAS Sparse Linear Algebra (C) | 3.45 ms | 41,924.5 | 10,190.7 | 37.89s |
| **ArangoDB Oasis** | Multi-Model RocksDB (AQL Graph) | 94.27 ms | 27,189.0 | 21,465.1 | 21.77s |
| **KùzuDB** | Columnar In-Process / Microservice Graph Engine | 219.78 ms | 191.5 | 149.3 | 3120.86s |
| **JanusGraph** | TinkerPop Gremlin Framework (HTTP Server) | 88.74 ms | 853.8 | 1,266.3 | 51.2s |
| **ArcadeDB** | Multi-Model Document + Graph Engine (openCypher / HTTP) | 408.87 ms | 3,023.7 | 381.2 | 134.47s |

### ⚡ Query Latency Profile (Percentiles in Milliseconds)

| Database | Point Lookup (p50 / p95) | 1-Hop Traversal (p50 / p95) | 2-Hop Traversal (p50 / p95) | 3-Hop Traversal (p50 / p95) | Degree Aggregation (p50) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Neo4j AuraDB** | 3.96 / 65.75 | 3.92 / 66.85 | 3.94 / 68.21 | 3.63 / 76.42 | 316.18 ms |
| **Memgraph Cloud** | 1.82 / 3.13 | 1.42 / 2.12 | 1.49 / 2.54 | 1.68 / 6.77 | 149.77 ms |
| **FalkorDB Cloud** | 1.12 / 1.63 | 1.09 / 1.56 | 1.05 / 1.55 | 1.08 / 1.79 | 297.63 ms |
| **ArangoDB Oasis** | 46.97 / 47.88 | 43.71 / 47.08 | 43.75 / 47.71 | 43.75 / 48.28 | 167.33 ms |
| **KùzuDB** | 51.03 / 52.24 | 51.74 / 65.46 | 52.13 / 55.86 | 55.09 / 58.28 | 83.97 ms |
| **JanusGraph** | 88.34 / 99.84 | 55.33 / 94.07 | 80.21 / 97.91 | 52.68 / 94.29 | 504.39 ms |
| **ArcadeDB** | 87.16 / 100.45 | 51.9 / 119.46 | 76.26 / 155.87 | 60.81 / 169.88 | 52.82 ms |

### 📈 Concurrency & Scalability Matrix (Mixed 80% Read / 20% Write)

| Database | 1 Client (QPS / p95) | 10 Clients (QPS / p95) | 40 Clients (QPS / p95) | Scalability Factor (40x / 1x) |
|:---|:---:|:---:|:---:|:---:|
| **Neo4j AuraDB** | 57.38 QPS (59.55ms) | 66.94 QPS (200.9ms) | 119.95 QPS (404.7ms) | **2.1x** |
| **Memgraph Cloud** | 147.47 QPS (53.64ms) | 149.34 QPS (100.26ms) | 183.15 QPS (300.24ms) | **1.2x** |
| **FalkorDB Cloud** | 528.47 QPS (2.52ms) | 722.09 QPS (73.76ms) | 766.87 QPS (95.92ms) | **1.5x** |
| **ArangoDB Oasis** | 22.03 QPS (44.33ms) | 203.77 QPS (51.55ms) | 463.97 QPS (117.05ms) | **21.1x** |
| **KùzuDB** | 9.34 QPS (108.22ms) | 37.35 QPS (303.07ms) | 34.83 QPS (1522.16ms) | **3.7x** |
| **JanusGraph** | 19.98 QPS (53.81ms) | 143.69 QPS (101.6ms) | 172.86 QPS (306.22ms) | **8.7x** |
| **ArcadeDB** | 4.7 QPS (280.44ms) | 3.39 QPS (3913.43ms) | 2.54 QPS (18555.32ms) | **0.5x** |

### 🌐 Network RTT vs Server-Side Net Compute Time (p50)

| Database | Baseline Network RTT | 1-Hop p50 (Gross) | 1-Hop Net Compute | 2-Hop Net Compute | 3-Hop Net Compute |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Neo4j AuraDB** | 6.85 ms | 3.92 ms | **0.00 ms** | **0.00 ms** | **0.00 ms** |
| **Memgraph Cloud** | 2.12 ms | 1.42 ms | **0.00 ms** | **0.00 ms** | **0.00 ms** |
| **FalkorDB Cloud** | 1.69 ms | 1.09 ms | **0.00 ms** | **0.00 ms** | **0.00 ms** |
| **ArangoDB Oasis** | 45.94 ms | 43.71 ms | **0.00 ms** | **0.00 ms** | **0.00 ms** |
| **KùzuDB** | 7.05 ms | 51.74 ms | **44.69 ms** | **45.08 ms** | **48.04 ms** |
| **JanusGraph** | 50.78 ms | 55.33 ms | **4.55 ms** | **29.43 ms** | **1.90 ms** |
| **ArcadeDB** | 4.92 ms | 51.90 ms | **46.98 ms** | **71.34 ms** | **55.89 ms** |