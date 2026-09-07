# Wexa AI — Graph Database Benchmarking & Application Engineering Suite

This repository encompasses the end-to-end engineering deliverables for the Wexa AI Systems Assessment, covering both empirical graph engine benchmarking and a fullstack knowledge graph application built on CognoDB Cloud.

---

## 📂 Assessment Overview

```text
WEXA/
├── Assessment 1/                    # Empirical Graph Database Benchmark Suite
│   ├── index.html                   # Interactive Executive Benchmark Dashboard (29 diagrams)
│   ├── Final Report/                # Whitepaper, latency matrices, and summary tables
│   ├── benchmarks/                  # Benchmark orchestrator and workload drivers
│   ├── run_benchmark.py             # CLI execution harness
│   └── README.md                    # In-depth benchmark taxonomy and empirical findings
│
└── Application_Assessment/          # PaperFlow: Research Paper Knowledge Graph Application
    ├── backend/                     # FastAPI async backend with Bolt openCypher queries
    ├── frontend/                    # React 19, Vite, Tailwind CSS, Cytoscape graph canvas
    ├── docs/                        # Architectural diagrams & PaperFlow Technical Report
    ├── docker-compose.yml           # Hermetic containerized deployment
    └── README.md                    # Cypher algorithms, triadic gap detection & setup
```

---

## 1. Assessment 1: Graph Database Empirical Benchmark Suite (`/Assessment 1`)

An exhaustive, publication-grade empirical performance evaluation comparing **CognoDB Cloud** against 7 industry-standard graph database engines:
- **Engines Tested**: CognoDB Cloud, FalkorDB, Memgraph, Neo4j 5 Community, ArangoDB, KùzuDB, JanusGraph, and ArcadeDB.
- **Workloads Evaluated**:
  1. *Bulk Ingestion & Topology Construction*: High-concurrency node and edge insertion scaling.
  2. *Multi-Hop Traversal Latency*: 1-hop, 2-hop, and 3-hop pointer-chasing vs index scans.
  3. *Pathfinding & Shortest Path*: Breadth-First Search (BFS) and Dijkstra traversals.
  4. *Analytical Aggregations*: Degree centrality, clustering coefficients, and community detection.
  5. *Concurrency & Tail Jitter*: p50, p95, and p99 latency distributions under load.
- **Interactive Dashboard**: Double-click [`Assessment 1/index.html`](Assessment%201/index.html) to explore interactive charts, zoomable diagrams, and comparative latency profiles.
- **Full Documentation**: See [`Assessment 1/README.md`](Assessment%201/README.md).

---

## 2. Assessment 2: PaperFlow Application (`/Application_Assessment`)

A production-grade, containerized research paper citation network and gap-finding platform:
- **Hosted Application**: [https://paperflow-28th.onrender.com/](https://paperflow-28th.onrender.com/)
- **Core Database**: CognoDB Cloud (openCypher over Bolt protocol).
- **Key Graph Algorithms**:
  1. *Multi-Hop Citation Lineage*: Tracing foundational ancestors 1 to 4 hops upstream from modern papers.
  2. *Triadic Concept Gap Discovery*: Identifying concept pairs with shared citation roots but zero joint literature.
  3. *Co-Citation Graph Analysis*: Finding frequently co-cited papers without direct citation edges.
  4. *Interdisciplinary Bridge Detection*: Shortest-path betweenness isolating bottleneck papers between scientific disciplines.
- **Full Documentation**: See [`Application_Assessment/README.md`](Application_Assessment/README.md).

---

## 🚀 Quick Reference

- To run the **Benchmark Suite**, navigate to `Assessment 1/` and follow its instructions.
- To run the **PaperFlow Application**, navigate to `Application_Assessment/` and execute `docker compose up`.
