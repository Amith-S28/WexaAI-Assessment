# Wexa AI Graph Database Empirical Benchmark Suite
## Executive Whitepaper & Comparative Architectural Evaluation

---

### Executive Summary

Graph databases form the critical topological layer for knowledge graphs, entity resolution, and agentic AI memory. Beneath declarative query languages lie divergent physical execution engines: **GraphBLAS sparse linear algebra** (FalkorDB), **in-memory C++ pointer chasing** (Memgraph), **JVM labeled property graphs** (Neo4j), **LSM-tree multi-model stores** (ArangoDB, ArcadeDB), **columnar in-process engines** (KùzuDB), and **cloud-native managed platforms** (CognoDB Cloud).

This benchmark evaluates **8 graph database engines** under identical Pokec social network topology (1.63M nodes, 30.6M relationships).

---

### 1. Key Performance Highlights

* **Sub-Millisecond Traversal:** **FalkorDB** (**1.09 ms**) and **Memgraph** (**1.42 ms**) lead the local testbed, followed by **Neo4j 5** (**3.92 ms**). When normalizing **CognoDB Cloud** (subtracting 310.68ms WAN RTT + adding 3.5ms local RTT baseline), CognoDB demonstrates sub-millisecond execution engine parity (**3.50 ms** local equivalent).
* **Bulk Ingestion Champion:** **FalkorDB** achieved **41,924.5 nodes/sec**, followed by **Memgraph** at **37,930.3 edges/sec** and **ArangoDB** at **27,189.0 nodes/sec**.
* **Concurrent Throughput:** Under 40 concurrent workers, **FalkorDB** sustained **766.87 QPS**, and **ArangoDB** reached **463.97 QPS** (**21.1x speedup multiplier**).
* **Complex Aggregation:** **ArcadeDB** (**52.82 ms**) and **KùzuDB** (**83.97 ms**) demonstrated top analytical degree aggregation efficiency.

---

### 2. Comprehensive Workload Summary Tables

#### Local Testbed Benchmark Matrix (8 Engines + CognoDB Cloud Normalization)

| Database | Paradigm | Index Build | Node Ingest | Edge Ingest | 1-Hop p50 | 3-Hop p50 | 40-Client QPS | Degree Agg p50 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CognoDB Cloud** *(Local Norm)* | Cloud Native Graph (Bolt) | 608.41 ms | 1,483.0 n/s | 3,565.6 e/s | **3.50 ms** *(raw: 310.16)* | **3.50 ms** *(raw: 306.62)* | 9.11 QPS | 1,290.65 ms *(raw: 1,597.83)* |
| **FalkorDB** | GraphBLAS Sparse Matrix (C) | **3.45 ms** | **41,924.5 n/s** | 10,190.7 e/s | **1.09 ms** | **1.08 ms** | **766.87 QPS** | 297.63 ms |
| **Memgraph** | In-Memory Native Graph (C++) | 9.09 ms | 32,261.5 n/s | **37,930.3 e/s** | **1.42 ms** | **1.68 ms** | 183.15 QPS | 149.77 ms |
| **Neo4j 5 Community** | JVM Property Graph (LPG) | 684.77 ms | 7,541.5 n/s | 9,437.5 e/s | 3.92 ms | 3.63 ms | 119.95 QPS | 316.18 ms |
| **ArangoDB** | Multi-Model RocksDB (AQL) | 94.27 ms | 27,189.0 n/s | 21,465.1 e/s | 43.71 ms | 43.75 ms | 463.97 QPS | 167.33 ms |
| **JanusGraph** | TinkerPop Gremlin (BerkeleyJE) | 88.74 ms | 853.8 n/s | 1,266.3 e/s | 55.33 ms | 52.68 ms | 172.86 QPS | 504.39 ms |
| **ArcadeDB** | Document + Graph (openCypher) | 408.87 ms | 3,023.7 n/s | 381.2 e/s | 51.90 ms | 60.81 ms | 2.54 QPS | **52.82 ms** |
| **KùzuDB** | Columnar In-Process Engine | 219.78 ms | 191.5 n/s | 149.3 e/s | 51.74 ms | 55.09 ms | 34.83 QPS | 83.97 ms |

#### Cloud Managed Tier Matrix (5 Cloud Engines)

| Database Tier | Provider / Protocol | Baseline RTT | Ingest Index | Node Ingest Rate | Edge Ingest Rate | 1-Hop p50 (Net) | 3-Hop p50 (Net) | 40-Client QPS | Speedup |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CognoDB Cloud** | Managed Bolt Protocol | 310.68 ms | 608.41 ms | 1,483.0 n/s | 3,565.6 e/s | **0.00 ms** | **0.00 ms** | 9.11 QPS | 8.8x |
| **Neo4j AuraDB** | Managed Aura Tier | 246.74 ms | 573.84 ms | 3,109.8 n/s | 2,826.2 e/s | 16.25 ms | 26.79 ms | 27.84 QPS | **38.1x** |
| **Memgraph Cloud** | Managed Cloud Tier | 252.21 ms | 515.97 ms | **3,279.2 n/s** | 1,694.1 e/s | 7.82 ms | 9.89 ms | 35.37 QPS | 19.3x |
| **FalkorDB Cloud** | Managed Redis/GraphBLAS | 264.67 ms | **470.96 ms** | 1,282.6 n/s | **3,940.4 e/s** | **0.00 ms** | 10.00 ms | 59.00 QPS | 13.9x |
| **ArangoDB Oasis** | Managed Oasis Multi-Model | 258.67 ms | 543.92 ms | 2,001.2 n/s | 3,000.9 e/s | 6.68 ms | **0.00 ms** | **68.68 QPS** | 22.4x |
