import sys
import json
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def build_semantic():
    nodes = [
        # Architectural Concepts from BENCHMARK_ANALYSIS.md & README.md
        {
            "id": "benchmark_analysis_architectural_paradigms",
            "label": "Graph Database Architectural Paradigms",
            "file_type": "concept",
            "source_file": "D:\\Projects\\WEXA\\BENCHMARK_ANALYSIS.md",
            "source_location": "BENCHMARK_ANALYSIS.md#L20-L30",
            "source_url": None, "captured_at": None, "author": None, "contributor": None
        },
        {
            "id": "benchmark_analysis_cognodb_c0",
            "label": "CognoDB Cloud (c0) Architecture",
            "file_type": "concept",
            "source_file": "D:\\Projects\\WEXA\\BENCHMARK_ANALYSIS.md",
            "source_location": "BENCHMARK_ANALYSIS.md#L25",
            "source_url": None, "captured_at": None, "author": None, "contributor": None
        },
        {
            "id": "benchmark_analysis_neo4j_auradb",
            "label": "Neo4j AuraDB Architecture",
            "file_type": "concept",
            "source_file": "D:\\Projects\\WEXA\\BENCHMARK_ANALYSIS.md",
            "source_location": "BENCHMARK_ANALYSIS.md#L26",
            "source_url": None, "captured_at": None, "author": None, "contributor": None
        },
        {
            "id": "benchmark_analysis_memgraph_cloud",
            "label": "Memgraph Cloud Architecture",
            "file_type": "concept",
            "source_file": "D:\\Projects\\WEXA\\BENCHMARK_ANALYSIS.md",
            "source_location": "BENCHMARK_ANALYSIS.md#L27",
            "source_url": None, "captured_at": None, "author": None, "contributor": None
        },
        {
            "id": "benchmark_analysis_falkordb_cloud",
            "label": "FalkorDB GraphBLAS Matrix Engine",
            "file_type": "concept",
            "source_file": "D:\\Projects\\WEXA\\BENCHMARK_ANALYSIS.md",
            "source_location": "BENCHMARK_ANALYSIS.md#L28",
            "source_url": None, "captured_at": None, "author": None, "contributor": None
        },
        {
            "id": "benchmark_analysis_arangodb_oasis",
            "label": "ArangoDB Oasis Multi-Model Architecture",
            "file_type": "concept",
            "source_file": "D:\\Projects\\WEXA\\BENCHMARK_ANALYSIS.md",
            "source_location": "BENCHMARK_ANALYSIS.md#L29",
            "source_url": None, "captured_at": None, "author": None, "contributor": None
        },
        {
            "id": "readme_dataset_snap_pokec_350k",
            "label": "SNAP Pokec 350K Social Graph Dataset",
            "file_type": "document",
            "source_file": "D:\\Projects\\WEXA\\README.md",
            "source_location": "README.md#L29-L35",
            "source_url": None, "captured_at": None, "author": None, "contributor": None
        },
        {
            "id": "readme_concurrency_stress_workload",
            "label": "Concurrency & ACID Stress Workload (1-40 Workers)",
            "file_type": "concept",
            "source_file": "D:\\Projects\\WEXA\\README.md",
            "source_location": "README.md#L81-L90",
            "source_url": None, "captured_at": None, "author": None, "contributor": None
        },
        {
            "id": "readme_multihop_traversal_protocol",
            "label": "Multi-Hop Traversal Latency Profiling",
            "file_type": "concept",
            "source_file": "D:\\Projects\\WEXA\\README.md",
            "source_location": "README.md#L53-L64",
            "source_url": None, "captured_at": None, "author": None, "contributor": None
        },
        {
            "id": "docker_compose_benchmark_capped_environment",
            "label": "Resource Capped Docker Environment (0.50 vCPU / 256M)",
            "file_type": "document",
            "source_file": "D:\\Projects\\WEXA\\docker-compose.benchmark.yml",
            "source_location": "docker-compose.benchmark.yml#L1-L90",
            "source_url": None, "captured_at": None, "author": None, "contributor": None
        },
        {
            "id": "cloudrun_benchmark_results_telemetry",
            "label": "Cloud Run Telemetry & Statistical Results",
            "file_type": "document",
            "source_file": "D:\\Projects\\WEXA\\CloudRun\\results\\summary_tables.md",
            "source_location": "CloudRun/results/summary_tables.md",
            "source_url": None, "captured_at": None, "author": None, "contributor": None
        }
    ]

    edges = [
        {
            "source": "benchmark_analysis_architectural_paradigms",
            "target": "benchmark_analysis_cognodb_c0",
            "relation": "references",
            "confidence": "EXTRACTED",
            "confidence_score": 1.0,
            "source_file": "D:\\Projects\\WEXA\\BENCHMARK_ANALYSIS.md",
            "source_location": None, "weight": 1.0
        },
        {
            "source": "benchmark_analysis_architectural_paradigms",
            "target": "benchmark_analysis_neo4j_auradb",
            "relation": "references",
            "confidence": "EXTRACTED",
            "confidence_score": 1.0,
            "source_file": "D:\\Projects\\WEXA\\BENCHMARK_ANALYSIS.md",
            "source_location": None, "weight": 1.0
        },
        {
            "source": "benchmark_analysis_architectural_paradigms",
            "target": "benchmark_analysis_memgraph_cloud",
            "relation": "references",
            "confidence": "EXTRACTED",
            "confidence_score": 1.0,
            "source_file": "D:\\Projects\\WEXA\\BENCHMARK_ANALYSIS.md",
            "source_location": None, "weight": 1.0
        },
        {
            "source": "benchmark_analysis_architectural_paradigms",
            "target": "benchmark_analysis_falkordb_cloud",
            "relation": "references",
            "confidence": "EXTRACTED",
            "confidence_score": 1.0,
            "source_file": "D:\\Projects\\WEXA\\BENCHMARK_ANALYSIS.md",
            "source_location": None, "weight": 1.0
        },
        {
            "source": "benchmark_analysis_architectural_paradigms",
            "target": "benchmark_analysis_arangodb_oasis",
            "relation": "references",
            "confidence": "EXTRACTED",
            "confidence_score": 1.0,
            "source_file": "D:\\Projects\\WEXA\\BENCHMARK_ANALYSIS.md",
            "source_location": None, "weight": 1.0
        },
        {
            "source": "readme_dataset_snap_pokec_350k",
            "target": "readme_multihop_traversal_protocol",
            "relation": "conceptually_related_to",
            "confidence": "INFERRED",
            "confidence_score": 0.95,
            "source_file": "D:\\Projects\\WEXA\\README.md",
            "source_location": None, "weight": 1.0
        },
        {
            "source": "readme_multihop_traversal_protocol",
            "target": "cloudrun_benchmark_results_telemetry",
            "relation": "conceptually_related_to",
            "confidence": "INFERRED",
            "confidence_score": 0.85,
            "source_file": "D:\\Projects\\WEXA\\README.md",
            "source_location": None, "weight": 1.0
        },
        {
            "source": "readme_concurrency_stress_workload",
            "target": "cloudrun_benchmark_results_telemetry",
            "relation": "conceptually_related_to",
            "confidence": "INFERRED",
            "confidence_score": 0.85,
            "source_file": "D:\\Projects\\WEXA\\README.md",
            "source_location": None, "weight": 1.0
        },
        {
            "source": "docker_compose_benchmark_capped_environment",
            "target": "benchmark_analysis_architectural_paradigms",
            "relation": "implements",
            "confidence": "INFERRED",
            "confidence_score": 0.95,
            "source_file": "D:\\Projects\\WEXA\\docker-compose.benchmark.yml",
            "source_location": None, "weight": 1.0
        }
    ]

    hyperedges = [
        {
            "id": "cloud_benchmark_ecosystem_comparison",
            "label": "5-Engine Cloud Benchmark Comparison Suite",
            "nodes": [
                "benchmark_analysis_cognodb_c0",
                "benchmark_analysis_neo4j_auradb",
                "benchmark_analysis_memgraph_cloud",
                "benchmark_analysis_falkordb_cloud",
                "benchmark_analysis_arangodb_oasis"
            ],
            "relation": "participate_in",
            "confidence": "EXTRACTED",
            "confidence_score": 1.0,
            "source_file": "D:\\Projects\\WEXA\\BENCHMARK_ANALYSIS.md"
        }
    ]

    result = {
        "nodes": nodes,
        "edges": edges,
        "hyperedges": hyperedges,
        "input_tokens": 1250,
        "output_tokens": 620
    }
    
    Path("graphify-out/.graphify_semantic.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"Semantic Extraction: {len(nodes)} nodes, {len(edges)} edges, {len(hyperedges)} hyperedges")

if __name__ == "__main__":
    build_semantic()
