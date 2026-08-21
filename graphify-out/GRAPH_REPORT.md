# Graph Report - WEXA  (2026-08-21)

## Corpus Check
- Large corpus: 104 files · ~657,438 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 315 nodes · 552 edges · 22 communities (19 shown, 3 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Module: benchmarks_adapters_cognodb_cognodbadapter, benchmarks_adapters_cognodb_cognodbadapter_init, benchmarks_adapters_cognodb_rationale_9
- Module: benchmarks_stats, benchmarks_stats_compute_distribution_metrics, benchmarks_stats_latencystats
- Module: benchmarks_adapters_arcadedb_arcadedbadapter, benchmarks_adapters_arcadedb_arcadedbadapter_aggregate_degree_distribution, benchmarks_adapters_arcadedb_arcadedbadapter_bulk_insert_edges
- Module: benchmarks_adapters_base_basegraphadapter, benchmarks_adapters_base_basegraphadapter_close, benchmarks_adapters_base_basegraphadapter_connect
- Module: benchmarks_adapters_bolt_base_boltgraphadapter, benchmarks_adapters_bolt_base_boltgraphadapter_aggregate_degree_distribution, benchmarks_adapters_bolt_base_boltgraphadapter_bulk_insert_edges
- Module: benchmarks_adapters_janusgraph_janusgraphadapter, benchmarks_adapters_janusgraph_janusgraphadapter_aggregate_degree_distribution, benchmarks_adapters_janusgraph_janusgraphadapter_bulk_insert_edges
- Module: benchmarks_adapters_arangodb_arangodbadapter, benchmarks_adapters_arangodb_arangodbadapter_aggregate_degree_distribution, benchmarks_adapters_arangodb_arangodbadapter_bulk_insert_edges
- Module: benchmarks_adapters_kuzu_kuzudbadapter, benchmarks_adapters_kuzu_kuzudbadapter_aggregate_degree_distribution, benchmarks_adapters_kuzu_kuzudbadapter_bulk_insert_edges
- Module: scripts_generate_all_diagrams_and_reports, scripts_generate_all_diagrams_and_reports_clean_key_name, scripts_generate_all_diagrams_and_reports_masterreportgenerator
- Module: benchmarks_adapters_falkordb_falkordbadapter, benchmarks_adapters_falkordb_falkordbadapter_aggregate_degree_distribution, benchmarks_adapters_falkordb_falkordbadapter_bulk_insert_edges
- Module: benchmarks_report_generator, benchmarks_report_generator_py_any, benchmarks_report_generator_py_path
- Module: abc, benchmarks_adapters_arangodb, benchmarks_adapters_arcadedb
- Module: benchmarks_adapters_base_basegraphadapter_aggregate_degree_distribution, benchmarks_adapters_base_basegraphadapter_bulk_insert_edges, benchmarks_adapters_base_basegraphadapter_bulk_insert_nodes
- Module: benchmarks_adapters_bolt_base, benchmarks_adapters_bolt_base_rationale_1, benchmarks_adapters_cognodb
- Module: scripts_generate_final_report_suite, scripts_generate_final_report_suite_build_executive_html, scripts_generate_final_report_suite_generate_cloud_charts
- Module: scripts_embed_charts_in_dashboards, scripts_embed_charts_in_dashboards_build_self_contained_dashboards, scripts_embed_charts_in_dashboards_get_base64_image
- Module: scripts_run_graphify_pipeline, scripts_run_graphify_pipeline_py_path, scripts_run_graphify_pipeline_rationale_1
- Module: scripts_verify_regions, scripts_verify_regions_extract_hostname, scripts_verify_regions_lookup_geo
- Module: scripts_build_interactive_dashboard, scripts_build_interactive_dashboard_generate_dashboard, scripts_build_interactive_dashboard_rationale_1
- Module: scripts_download_dataset_fast, scripts_download_dataset_fast_main, scripts_download_dataset_fast_stream_and_parse_snap
- Module: benchmarks_init, benchmarks_init_rationale_1

## God Nodes (most connected - your core abstractions)
1. `BaseGraphAdapter` - 36 edges
2. `ArangoDBAdapter` - 27 edges
3. `ArcadeDBAdapter` - 26 edges
4. `BoltGraphAdapter` - 26 edges
5. `FalkorDBAdapter` - 26 edges
6. `JanusGraphAdapter` - 26 edges
7. `KuzuDBAdapter` - 25 edges
8. `MasterReportGenerator` - 15 edges
9. `ReportGenerator` - 14 edges
10. `WorkloadRunner` - 14 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `ArangoDBAdapter`  [EXTRACTED]
  scripts/test_adapters.py → benchmarks/adapters/arangodb.py
- `get_adapter()` --calls--> `ArangoDBAdapter`  [EXTRACTED]
  scripts/test_individual_adapter.py → benchmarks/adapters/arangodb.py
- `get_adapter()` --calls--> `ArcadeDBAdapter`  [EXTRACTED]
  scripts/test_individual_adapter.py → benchmarks/adapters/arcadedb.py
- `main()` --calls--> `FalkorDBAdapter`  [EXTRACTED]
  scripts/test_adapters.py → benchmarks/adapters/falkordb.py
- `get_adapter()` --calls--> `FalkorDBAdapter`  [EXTRACTED]
  scripts/test_individual_adapter.py → benchmarks/adapters/falkordb.py

## Import Cycles
- None detected.

## Communities (22 total, 3 thin omitted)

### Community 0 - "Module: benchmarks_adapters_cognodb_cognodbadapter, benchmarks_adapters_cognodb_cognodbadapter_init, benchmarks_adapters_cognodb_rationale_9"
Cohesion: 0.11
Nodes (20): CognoDBAdapter, Adapter for CognoDB Cloud managed graph database., MemgraphAdapter, Memgraph specific index syntax., Adapter for Memgraph Cloud in-memory instance., Neo4jAdapter, Adapter for Neo4j AuraDB Free / Professional Cloud instance., BenchmarkOrchestrator (+12 more)

### Community 1 - "Module: benchmarks_stats, benchmarks_stats_compute_distribution_metrics, benchmarks_stats_latencystats"
Cohesion: 0.10
Nodes (16): compute_distribution_metrics(), LatencyStats, Any, Statistical Engine for Graph Database Cloud Benchmarking. Computes high-…, Computes and formats latency distributions and throughput metrics., Presentation-time dynamic statistical computer for raw telemetry arrays., Any, Workload 2: Untracked warmup queries to prime memory and query planners. (+8 more)

### Community 2 - "Module: benchmarks_adapters_arcadedb_arcadedbadapter, benchmarks_adapters_arcadedb_arcadedbadapter_aggregate_degree_distribution, benchmarks_adapters_arcadedb_arcadedbadapter_bulk_insert_edges"
Cohesion: 0.20
Nodes (3): ArcadeDBAdapter, Any, Adapter for ArcadeDB multi-model graph engine.

### Community 3 - "Module: benchmarks_adapters_base_basegraphadapter, benchmarks_adapters_base_basegraphadapter_close, benchmarks_adapters_base_basegraphadapter_connect"
Cohesion: 0.10
Nodes (10): BaseGraphAdapter, Abstract base class for all benchmarked graph database adapters., Establish connection to the database. Returns True if successful., Close connections and release driver resources., Clear existing benchmark data (nodes, edges, indexes) for a fresh run., Create indexes on User.id and User.category. Returns elapsed time in ms., 1-hop traversal (immediate neighbors). Returns (latency_ms, neighbor_count)., 2-hop traversal (distinct friends-of-friends). Returns (latency_ms,… (+2 more)

### Community 4 - "Module: benchmarks_adapters_bolt_base_boltgraphadapter, benchmarks_adapters_bolt_base_boltgraphadapter_aggregate_degree_distribution, benchmarks_adapters_bolt_base_boltgraphadapter_bulk_insert_edges"
Cohesion: 0.13
Nodes (5): BoltGraphAdapter, Any, Unified Cypher + Bolt Protocol Adapter with robust connection pooling., Atomic read-then-write query., Inspect storage where platform exposes it.

### Community 5 - "Module: benchmarks_adapters_janusgraph_janusgraphadapter, benchmarks_adapters_janusgraph_janusgraphadapter_aggregate_degree_distribution, benchmarks_adapters_janusgraph_janusgraphadapter_bulk_insert_edges"
Cohesion: 0.22
Nodes (3): JanusGraphAdapter, Any, Adapter for JanusGraph distributed graph database via TinkerPop Gremlin HTTP…

### Community 6 - "Module: benchmarks_adapters_arangodb_arangodbadapter, benchmarks_adapters_arangodb_arangodbadapter_aggregate_degree_distribution, benchmarks_adapters_arangodb_arangodbadapter_bulk_insert_edges"
Cohesion: 0.15
Nodes (3): ArangoDBAdapter, Any, Adapter for ArangoDB Oasis Cloud multi-model graph engine.

### Community 7 - "Module: benchmarks_adapters_kuzu_kuzudbadapter, benchmarks_adapters_kuzu_kuzudbadapter_aggregate_degree_distribution, benchmarks_adapters_kuzu_kuzudbadapter_bulk_insert_edges"
Cohesion: 0.21
Nodes (3): KuzuDBAdapter, Any, Adapter for KùzuDB columnar graph database engine.

### Community 8 - "Module: scripts_generate_all_diagrams_and_reports, scripts_generate_all_diagrams_and_reports_clean_key_name, scripts_generate_all_diagrams_and_reports_masterreportgenerator"
Cohesion: 0.18
Nodes (6): clean_key_name(), MasterReportGenerator, Any, Path, Master Diagram and Benchmark Report Generator. Merges Cloud Run CognoDB…, run()

### Community 9 - "Module: benchmarks_adapters_falkordb_falkordbadapter, benchmarks_adapters_falkordb_falkordbadapter_aggregate_degree_distribution, benchmarks_adapters_falkordb_falkordbadapter_bulk_insert_edges"
Cohesion: 0.15
Nodes (3): FalkorDBAdapter, Any, Adapter for FalkorDB Cloud GraphBLAS sparse matrix engine.

### Community 10 - "Module: benchmarks_report_generator, benchmarks_report_generator_py_any, benchmarks_report_generator_py_path"
Cohesion: 0.15
Nodes (8): Any, Path, Publication-Grade Visual Report Generator. Generates publication-quality charts…, Multi-metric summary matrix bar chart., Format results into clean GitHub markdown tables., Renders charts and compiles Markdown report tables., Generate all publication-grade benchmark visualization charts., ReportGenerator

### Community 11 - "Module: abc, benchmarks_adapters_arangodb, benchmarks_adapters_arcadedb"
Cohesion: 0.17
Nodes (8): ABC, ArcadeDB Adapter. Implements BaseGraphAdapter for ArcadeDB Multi-Model Graph…, Base Graph Database Adapter Interface. Defines the standard contract for all…, FalkorDB Cloud Adapter. Implements BaseGraphAdapter for FalkorDB's GraphBLAS…, Database Adapters Package., JanusGraph Adapter. Implements BaseGraphAdapter for JanusGraph (Apache…, KùzuDB Adapter. Implements BaseGraphAdapter for KùzuDB (In-Process / Columnar…, Workload Execution Engine. Executes standard benchmark workloads across…

### Community 12 - "Module: benchmarks_adapters_base_basegraphadapter_aggregate_degree_distribution, benchmarks_adapters_base_basegraphadapter_bulk_insert_edges, benchmarks_adapters_base_basegraphadapter_bulk_insert_nodes"
Cohesion: 0.13
Nodes (8): Any, Ingest node records in batches. Returns dict with: total_nodes, elapsed_sec,…, Ingest edge records in batches. Returns dict with: total_edges, elapsed_sec,…, Lookup node by ID. Returns (latency_ms, record_dict)., Filter nodes by category. Returns (latency_ms, list_of_records)., Aggregate top-N nodes by out-degree. Returns (latency_ms, list_of_top_nodes)., Execute a mixed read/write transaction. Returns (latency_ms, success)., Inspect storage/memory footprint where observable.

### Community 13 - "Module: benchmarks_adapters_bolt_base, benchmarks_adapters_bolt_base_rationale_1, benchmarks_adapters_cognodb"
Cohesion: 0.20
Nodes (6): Bolt-based Base Adapter for Cypher-compatible graph databases: - CognoDB Cloud…, CognoDB Cloud Adapter. Implements BoltGraphAdapter for Wexa AI's CognoDB Cloud…, Memgraph Cloud Adapter. Implements BoltGraphAdapter for Memgraph in-memory C++…, Neo4j AuraDB Adapter. Implements BoltGraphAdapter for Neo4j AuraDB Cloud., main(), test_bolt_connection()

### Community 14 - "Module: scripts_generate_final_report_suite, scripts_generate_final_report_suite_build_executive_html, scripts_generate_final_report_suite_generate_cloud_charts"
Cohesion: 0.47
Nodes (9): build_executive_html(), generate_cloud_charts(), generate_local_charts(), generate_markdown_report(), get_color(), load_data(), main(), Path (+1 more)

### Community 15 - "Module: scripts_embed_charts_in_dashboards, scripts_embed_charts_in_dashboards_build_self_contained_dashboards, scripts_embed_charts_in_dashboards_get_base64_image"
Cohesion: 0.60
Nodes (4): build_self_contained_dashboards(), get_base64_image(), Path, Embeds all benchmark visualization charts directly as base64 data URIs into all…

### Community 16 - "Module: scripts_run_graphify_pipeline, scripts_run_graphify_pipeline_py_path, scripts_run_graphify_pipeline_rationale_1"
Cohesion: 0.50
Nodes (3): Path, Graphify Pipeline Execution Harness Executes graphify Steps 1-5 on the…, run_pipeline()

### Community 17 - "Module: scripts_verify_regions, scripts_verify_regions_extract_hostname, scripts_verify_regions_lookup_geo"
Cohesion: 0.83
Nodes (3): extract_hostname(), lookup_geo(), main()

## Knowledge Gaps
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BaseGraphAdapter` connect `Module: benchmarks_adapters_base_basegraphadapter, benchmarks_adapters_base_basegraphadapter_close, benchmarks_adapters_base_basegraphadapter_connect` to `Module: benchmarks_stats, benchmarks_stats_compute_distribution_metrics, benchmarks_stats_latencystats`, `Module: benchmarks_adapters_arcadedb_arcadedbadapter, benchmarks_adapters_arcadedb_arcadedbadapter_aggregate_degree_distribution, benchmarks_adapters_arcadedb_arcadedbadapter_bulk_insert_edges`, `Module: benchmarks_adapters_bolt_base_boltgraphadapter, benchmarks_adapters_bolt_base_boltgraphadapter_aggregate_degree_distribution, benchmarks_adapters_bolt_base_boltgraphadapter_bulk_insert_edges`, `Module: benchmarks_adapters_janusgraph_janusgraphadapter, benchmarks_adapters_janusgraph_janusgraphadapter_aggregate_degree_distribution, benchmarks_adapters_janusgraph_janusgraphadapter_bulk_insert_edges`, `Module: benchmarks_adapters_arangodb_arangodbadapter, benchmarks_adapters_arangodb_arangodbadapter_aggregate_degree_distribution, benchmarks_adapters_arangodb_arangodbadapter_bulk_insert_edges`, `Module: benchmarks_adapters_kuzu_kuzudbadapter, benchmarks_adapters_kuzu_kuzudbadapter_aggregate_degree_distribution, benchmarks_adapters_kuzu_kuzudbadapter_bulk_insert_edges`, `Module: benchmarks_adapters_falkordb_falkordbadapter, benchmarks_adapters_falkordb_falkordbadapter_aggregate_degree_distribution, benchmarks_adapters_falkordb_falkordbadapter_bulk_insert_edges`, `Module: abc, benchmarks_adapters_arangodb, benchmarks_adapters_arcadedb`, `Module: benchmarks_adapters_base_basegraphadapter_aggregate_degree_distribution, benchmarks_adapters_base_basegraphadapter_bulk_insert_edges, benchmarks_adapters_base_basegraphadapter_bulk_insert_nodes`, `Module: benchmarks_adapters_bolt_base, benchmarks_adapters_bolt_base_rationale_1, benchmarks_adapters_cognodb`?**
  _High betweenness centrality (0.255) - this node is a cross-community bridge._
- **Why does `BoltGraphAdapter` connect `Module: benchmarks_adapters_bolt_base_boltgraphadapter, benchmarks_adapters_bolt_base_boltgraphadapter_aggregate_degree_distribution, benchmarks_adapters_bolt_base_boltgraphadapter_bulk_insert_edges` to `Module: benchmarks_adapters_cognodb_cognodbadapter, benchmarks_adapters_cognodb_cognodbadapter_init, benchmarks_adapters_cognodb_rationale_9`, `Module: abc, benchmarks_adapters_arangodb, benchmarks_adapters_arcadedb`, `Module: benchmarks_adapters_base_basegraphadapter, benchmarks_adapters_base_basegraphadapter_close, benchmarks_adapters_base_basegraphadapter_connect`, `Module: benchmarks_adapters_bolt_base, benchmarks_adapters_bolt_base_rationale_1, benchmarks_adapters_cognodb`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Why does `ArcadeDBAdapter` connect `Module: benchmarks_adapters_arcadedb_arcadedbadapter, benchmarks_adapters_arcadedb_arcadedbadapter_aggregate_degree_distribution, benchmarks_adapters_arcadedb_arcadedbadapter_bulk_insert_edges` to `Module: benchmarks_adapters_base_basegraphadapter, benchmarks_adapters_base_basegraphadapter_close, benchmarks_adapters_base_basegraphadapter_connect`, `Module: benchmarks_adapters_cognodb_cognodbadapter, benchmarks_adapters_cognodb_cognodbadapter_init, benchmarks_adapters_cognodb_rationale_9`, `Module: abc, benchmarks_adapters_arangodb, benchmarks_adapters_arcadedb`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Should `Module: benchmarks_adapters_cognodb_cognodbadapter, benchmarks_adapters_cognodb_cognodbadapter_init, benchmarks_adapters_cognodb_rationale_9` be split into smaller, more focused modules?**
  _Cohesion score 0.10752688172043011 - nodes in this community are weakly interconnected._
- **Should `Module: benchmarks_stats, benchmarks_stats_compute_distribution_metrics, benchmarks_stats_latencystats` be split into smaller, more focused modules?**
  _Cohesion score 0.10052910052910052 - nodes in this community are weakly interconnected._
- **Should `Module: benchmarks_adapters_base_basegraphadapter, benchmarks_adapters_base_basegraphadapter_close, benchmarks_adapters_base_basegraphadapter_connect` be split into smaller, more focused modules?**
  _Cohesion score 0.10476190476190476 - nodes in this community are weakly interconnected._
- **Should `Module: benchmarks_adapters_bolt_base_boltgraphadapter, benchmarks_adapters_bolt_base_boltgraphadapter_aggregate_degree_distribution, benchmarks_adapters_bolt_base_boltgraphadapter_bulk_insert_edges` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._