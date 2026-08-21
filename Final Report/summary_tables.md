# Wexa AI Graph Database Benchmark — Workload Summary Tables

## Local Testbed Matrix (8 Graph Engines + CognoDB Cloud Baseline)

| Database | Paradigm | Baseline RTT | Index Build | Node Ingest | Edge Ingest | 1-Hop p50 (Net) | 3-Hop p50 (Net) | 40-Client QPS | Degree Agg (Net) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CognoDB Cloud** | Cloud Native Graph (Bolt) | 310.68 ms | 608.41 ms | 1,483.0 n/s | 3,565.6 e/s | **0.00 ms** *(raw: 310.16)* | **0.00 ms** *(raw: 306.62)* | 9.11 QPS | 1,287.15 ms |
| **FalkorDB** | GraphBLAS Sparse Matrix (C) | 1.69 ms | **3.45 ms** | **41,924.5 n/s** | 10,190.7 e/s | **0.00 ms** *(raw: 1.09)* | **0.00 ms** *(raw: 1.08)* | **766.87 QPS** | 295.94 ms |
| **Memgraph** | In-Memory Native Graph (C++) | 2.12 ms | 9.09 ms | 32,261.5 n/s | **37,930.3 e/s** | **0.00 ms** *(raw: 1.42)* | **0.00 ms** *(raw: 1.68)* | 183.15 QPS | 147.65 ms |
| **Neo4j 5 Community** | JVM Property Graph (LPG) | 6.85 ms | 684.77 ms | 7,541.5 n/s | 9,437.5 e/s | **0.00 ms** *(raw: 3.92)* | **0.00 ms** *(raw: 3.63)* | 119.95 QPS | 309.33 ms |
| **ArangoDB** | Multi-Model RocksDB (AQL) | 45.94 ms | 94.27 ms | 27,189.0 n/s | 21,465.1 e/s | **0.00 ms** *(raw: 43.71)* | **0.00 ms** *(raw: 43.75)* | 463.97 QPS | 121.39 ms |
| **JanusGraph** | TinkerPop Gremlin (BerkeleyJE) | 50.78 ms | 88.74 ms | 853.8 n/s | 1,266.3 e/s | 4.55 ms *(raw: 55.33)* | 1.90 ms *(raw: 52.68)* | 172.86 QPS | 453.61 ms |
| **ArcadeDB** | Document + Graph (openCypher) | 4.92 ms | 408.87 ms | 3,023.7 n/s | 381.2 e/s | 46.98 ms *(raw: 51.90)* | 55.89 ms *(raw: 60.81)* | 2.54 QPS | **47.90 ms** |
| **KùzuDB** | Columnar In-Process Engine | 7.05 ms | 219.78 ms | 191.5 n/s | 149.3 e/s | 44.69 ms *(raw: 51.74)* | 48.04 ms *(raw: 55.09)* | 34.83 QPS | 76.92 ms |

---

## Cloud Managed Tier Matrix (5 Cloud Engines)

| Database Tier | Provider / Protocol | Baseline RTT | Ingest Index | Node Ingest Rate | Edge Ingest Rate | 1-Hop p50 (Net) | 3-Hop p50 (Net) | 40-Client QPS | Speedup |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CognoDB Cloud** | Managed Bolt Protocol | 310.68 ms | 608.41 ms | 1,483.0 n/s | 3,565.6 e/s | **0.00 ms** | **0.00 ms** | 9.11 QPS | 8.8x |
| **Neo4j AuraDB** | Managed Aura Tier | 246.74 ms | 573.84 ms | 3,109.8 n/s | 2,826.2 e/s | 16.25 ms | 26.79 ms | 27.84 QPS | **38.1x** |
| **Memgraph Cloud** | Managed Cloud Tier | 252.21 ms | 515.97 ms | **3,279.2 n/s** | 1,694.1 e/s | 7.82 ms | 9.89 ms | 35.37 QPS | 19.3x |
| **FalkorDB Cloud** | Managed Redis/GraphBLAS | 264.67 ms | **470.96 ms** | 1,282.6 n/s | **3,940.4 e/s** | **0.00 ms** | 10.00 ms | 59.00 QPS | 13.9x |
| **ArangoDB Oasis** | Managed Oasis Multi-Model | 258.67 ms | 543.92 ms | 2,001.2 n/s | 3,000.9 e/s | 6.68 ms | **0.00 ms** | **68.68 QPS** | 22.4x |
