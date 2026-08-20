# Graph Report - .  (2026-08-21)

## Corpus Check
- 59 files · ~201,627 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 237 nodes · 366 edges · 17 communities (15 shown, 2 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 13 edges (avg confidence: 0.62)
- Token cost: 1,250 input · 620 output

## Community Hubs (Navigation)
- Database Adapters & Wire Protocols
- Database Adapters & Wire Protocols
- Statistical Analysis & Visual Reporting
- Database Adapters & Wire Protocols
- Database Adapters & Wire Protocols
- Database Adapters & Wire Protocols
- Statistical Analysis & Visual Reporting
- Statistical Analysis & Visual Reporting
- Database Adapters & Wire Protocols
- Database Adapters & Wire Protocols
- Environment Architecture & Datasets
- Database Adapters & Wire Protocols
- Pre-Flight Validation & Infrastructure Probes
- Environment Architecture & Datasets
- Database Adapters & Wire Protocols

## God Nodes (most connected - your core abstractions)
1. `BaseGraphAdapter` - 30 edges
2. `ArangoDBAdapter` - 27 edges
3. `BoltGraphAdapter` - 26 edges
4. `FalkorDBAdapter` - 26 edges
5. `ReportGenerator` - 14 edges
6. `WorkloadRunner` - 14 edges
7. `MemgraphAdapter` - 12 edges
8. `CognoDBAdapter` - 11 edges
9. `Neo4jAdapter` - 11 edges
10. `generate_all_metric_diagrams()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `Resource Capped Docker Environment (0.50 vCPU / 256M)` --implements--> `Graph Database Architectural Paradigms`  [INFERRED]
  docker-compose.benchmark.yml → BENCHMARK_ANALYSIS.md
- `main()` --calls--> `ArangoDBAdapter`  [EXTRACTED]
  scripts/test_adapters.py → benchmarks/adapters/arangodb.py
- `get_adapter()` --calls--> `ArangoDBAdapter`  [EXTRACTED]
  scripts/test_individual_adapter.py → benchmarks/adapters/arangodb.py
- `main()` --calls--> `FalkorDBAdapter`  [EXTRACTED]
  scripts/test_adapters.py → benchmarks/adapters/falkordb.py
- `get_adapter()` --calls--> `FalkorDBAdapter`  [EXTRACTED]
  scripts/test_individual_adapter.py → benchmarks/adapters/falkordb.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **5-Engine Cloud Benchmark Comparison Suite** — benchmark_analysis_cognodb_c0, benchmark_analysis_neo4j_auradb, benchmark_analysis_memgraph_cloud, benchmark_analysis_falkordb_cloud, benchmark_analysis_arangodb_oasis [EXTRACTED 1.00]

## Communities (17 total, 2 thin omitted)

### Community 0 - "Database Adapters & Wire Protocols"
Cohesion: 0.05
Nodes (26): ABC, BaseGraphAdapter, Any, Base Graph Database Adapter Interface. Defines the standard contract for all dat, Abstract base class for all benchmarked graph database adapters., Establish connection to the database. Returns True if successful., Close connections and release driver resources., Clear existing benchmark data (nodes, edges, indexes) for a fresh run. (+18 more)

### Community 1 - "Database Adapters & Wire Protocols"
Cohesion: 0.11
Nodes (20): CognoDBAdapter, Adapter for CognoDB Cloud managed graph database., MemgraphAdapter, Memgraph specific index syntax., Adapter for Memgraph Cloud in-memory instance., Neo4jAdapter, Adapter for Neo4j AuraDB Free / Professional Cloud instance., BenchmarkOrchestrator (+12 more)

### Community 2 - "Statistical Analysis & Visual Reporting"
Cohesion: 0.10
Nodes (16): compute_distribution_metrics(), LatencyStats, Any, Statistical Engine for Graph Database Cloud Benchmarking. Computes high-resoluti, Computes and formats latency distributions and throughput metrics., Presentation-time dynamic statistical computer for raw telemetry arrays., Any, Workload 2: Untracked warmup queries to prime memory and query planners. (+8 more)

### Community 3 - "Database Adapters & Wire Protocols"
Cohesion: 0.12
Nodes (6): BoltGraphAdapter, Any, Unified Cypher + Bolt Protocol Adapter with robust connection pooling., Atomic read-then-write query., Inspect storage where platform exposes it., Drop existing nodes and relationships in batches to prevent memory OOM.

### Community 4 - "Database Adapters & Wire Protocols"
Cohesion: 0.15
Nodes (3): ArangoDBAdapter, Any, Adapter for ArangoDB Oasis Cloud multi-model graph engine.

### Community 5 - "Database Adapters & Wire Protocols"
Cohesion: 0.15
Nodes (3): FalkorDBAdapter, Any, Adapter for FalkorDB Cloud GraphBLAS sparse matrix engine.

### Community 6 - "Statistical Analysis & Visual Reporting"
Cohesion: 0.15
Nodes (8): Any, Path, Publication-Grade Visual Report Generator. Generates publication-quality charts, Multi-metric summary matrix bar chart., Format results into clean GitHub markdown tables., Renders charts and compiles Markdown report tables., Generate all publication-grade benchmark visualization charts., ReportGenerator

### Community 7 - "Statistical Analysis & Visual Reporting"
Cohesion: 0.38
Nodes (10): generate_all_metric_diagrams(), generate_jitter_dumbbell_chart(), generate_quadrant_matrix(), generate_radar_chart(), generate_speedup_chart(), load_data(), _normalize(), Path (+2 more)

### Community 8 - "Database Adapters & Wire Protocols"
Cohesion: 0.29
Nodes (7): ArangoDB Oasis Multi-Model Architecture, Graph Database Architectural Paradigms, CognoDB Cloud (c0) Architecture, FalkorDB GraphBLAS Matrix Engine, Memgraph Cloud Architecture, Neo4j AuraDB Architecture, Resource Capped Docker Environment (0.50 vCPU / 256M)

### Community 9 - "Database Adapters & Wire Protocols"
Cohesion: 0.33
Nodes (3): Neo4j AuraDB Adapter. Implements BoltGraphAdapter for Neo4j AuraDB Cloud., main(), test_bolt_connection()

### Community 10 - "Environment Architecture & Datasets"
Cohesion: 0.70
Nodes (4): download_file(), main(), process_dataset(), Path

### Community 11 - "Database Adapters & Wire Protocols"
Cohesion: 0.50
Nodes (4): Cloud Run Telemetry & Statistical Results, Concurrency & ACID Stress Workload (1-40 Workers), SNAP Pokec 350K Social Graph Dataset, Multi-Hop Traversal Latency Profiling

### Community 12 - "Pre-Flight Validation & Infrastructure Probes"
Cohesion: 0.83
Nodes (3): extract_hostname(), lookup_geo(), main()

## Knowledge Gaps
- **8 isolated node(s):** `CognoDB Cloud (c0) Architecture`, `Neo4j AuraDB Architecture`, `Memgraph Cloud Architecture`, `FalkorDB GraphBLAS Matrix Engine`, `ArangoDB Oasis Multi-Model Architecture` (+3 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BaseGraphAdapter` connect `Database Adapters & Wire Protocols` to `Statistical Analysis & Visual Reporting`, `Database Adapters & Wire Protocols`, `Database Adapters & Wire Protocols`, `Database Adapters & Wire Protocols`?**
  _High betweenness centrality (0.300) - this node is a cross-community bridge._
- **Why does `ArangoDBAdapter` connect `Database Adapters & Wire Protocols` to `Database Adapters & Wire Protocols`, `Database Adapters & Wire Protocols`?**
  _High betweenness centrality (0.166) - this node is a cross-community bridge._
- **Why does `BoltGraphAdapter` connect `Database Adapters & Wire Protocols` to `Database Adapters & Wire Protocols`, `Database Adapters & Wire Protocols`, `Database Adapters & Wire Protocols`?**
  _High betweenness centrality (0.164) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `BaseGraphAdapter` (e.g. with `ArangoDBAdapter` and `BoltGraphAdapter`) actually correct?**
  _`BaseGraphAdapter` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `BoltGraphAdapter` (e.g. with `BaseGraphAdapter` and `CognoDBAdapter`) actually correct?**
  _`BoltGraphAdapter` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `CognoDB Cloud (c0) Architecture`, `Neo4j AuraDB Architecture`, `Memgraph Cloud Architecture` to the rest of the system?**
  _8 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Database Adapters & Wire Protocols` be split into smaller, more focused modules?**
  _Cohesion score 0.05279034690799397 - nodes in this community are weakly interconnected._