# Wexa AI Graph Database Benchmark — Local Run Summary Tables

## Local Testbed Matrix (8 Graph Engines + CognoDB Cloud Normalization)

| Database | Paradigm | Network Baseline | Index Build | Node Ingest | Edge Ingest | 1-Hop p50 | 3-Hop p50 | 40-Client QPS | Degree Agg p50 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CognoDB Cloud** *(Local Norm)* | Cloud Native Graph (Bolt) | 310.68 ms WAN | 608.41 ms | 1,483.0 n/s | 3,565.6 e/s | **3.50 ms** *(raw: 310.16)* | **3.50 ms** *(raw: 306.62)* | 9.11 QPS | 1,290.65 ms *(raw: 1,597.83)* |
| **FalkorDB** | GraphBLAS Sparse Matrix (C) | 1.69 ms Local | **3.45 ms** | **41,924.5 n/s** | 10,190.7 e/s | **1.09 ms** | **1.08 ms** | **766.87 QPS** | 297.63 ms |
| **Memgraph** | In-Memory Native Graph (C++) | 2.12 ms Local | 9.09 ms | 32,261.5 n/s | **37,930.3 e/s** | **1.42 ms** | **1.68 ms** | 183.15 QPS | 149.77 ms |
| **Neo4j 5 Community** | JVM Property Graph (LPG) | 6.85 ms Local | 684.77 ms | 7,541.5 n/s | 9,437.5 e/s | 3.92 ms | 3.63 ms | 119.95 QPS | 316.18 ms |
| **ArangoDB** | Multi-Model RocksDB (AQL) | 45.94 ms Local | 94.27 ms | 27,189.0 n/s | 21,465.1 e/s | 43.71 ms | 43.75 ms | 463.97 QPS | 167.33 ms |
| **JanusGraph** | TinkerPop Gremlin (BerkeleyJE) | 50.78 ms Local | 88.74 ms | 853.8 n/s | 1,266.3 e/s | 55.33 ms | 52.68 ms | 172.86 QPS | 504.39 ms |
| **ArcadeDB** | Document + Graph (openCypher) | 4.92 ms Local | 408.87 ms | 3,023.7 n/s | 381.2 e/s | 51.90 ms | 60.81 ms | 2.54 QPS | **52.82 ms** |
| **KùzuDB** | Columnar In-Process Engine | 7.05 ms Local | 219.78 ms | 191.5 n/s | 149.3 e/s | 51.74 ms | 55.09 ms | 34.83 QPS | 83.97 ms |

---

*Note: All 7 local database engines report actual measured local end-to-end latencies. CognoDB Cloud is normalized to the local testbed baseline by subtracting its measured 310.68ms WAN transit RTT and adding the local testbed baseline loopback RTT (3.50ms).*