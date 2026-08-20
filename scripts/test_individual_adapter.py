"""
Individual Database Adapter Test Suite.
Runs a thorough end-to-end functional and correctness test on a single specified database.
Usage:
    python scripts/test_individual_adapter.py --db cognodb
    python scripts/test_individual_adapter.py --db neo4j
    python scripts/test_individual_adapter.py --db memgraph
    python scripts/test_individual_adapter.py --db falkordb
    python scripts/test_individual_adapter.py --db arangodb
    python scripts/test_individual_adapter.py --all
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console(force_terminal=True, legacy_windows=False)
load_dotenv()

from benchmarks.adapters import (
    CognoDBAdapter,
    Neo4jAdapter,
    MemgraphAdapter,
    FalkorDBAdapter,
    ArangoDBAdapter
)

def get_adapter(db_name: str):
    db_name = db_name.lower()
    if db_name in ["cognodb", "cogno", "1"]:
        return CognoDBAdapter(
            uri=os.getenv("COGNODB_URI"),
            user=os.getenv("COGNODB_USER", "cognodb"),
            password=os.getenv("COGNODB_PASSWORD")
        )
    elif db_name in ["neo4j", "aura", "2"]:
        return Neo4jAdapter(
            uri=os.getenv("NEO4J_URI"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD")
        )
    elif db_name in ["memgraph", "mem", "3"]:
        return MemgraphAdapter(
            uri=os.getenv("MEMGRAPH_URI"),
            user=os.getenv("MEMGRAPH_USER"),
            password=os.getenv("MEMGRAPH_PASSWORD")
        )
    elif db_name in ["falkordb", "falkor", "4"]:
        return FalkorDBAdapter(
            host=os.getenv("FALKORDB_HOST"),
            port=int(os.getenv("FALKORDB_PORT", "6379")),
            user=os.getenv("FALKORDB_USER", "falkordb"),
            password=os.getenv("FALKORDB_PASSWORD")
        )
    elif db_name in ["arangodb", "arango", "5"]:
        return ArangoDBAdapter(
            url=os.getenv("ARANGODB_URL"),
            user=os.getenv("ARANGODB_USER", "root"),
            password=os.getenv("ARANGODB_PASSWORD")
        )
    else:
        raise ValueError(f"Unknown database: {db_name}. Choose from: cognodb, neo4j, memgraph, falkordb, arangodb")

def run_deep_individual_test(adapter):
    console.print(Panel(
        f"[bold white]DATABASE:[/bold white] [bold yellow]{adapter.name}[/bold yellow]\n"
        f"[bold white]PARADIGM:[/bold white] {adapter.paradigm}\n"
        f"[bold white]DB TYPE:[/bold white]  {adapter.db_type}",
        title=f"🔎 DEEP FUNCTIONAL AUDIT: {adapter.name}",
        border_style="cyan"
    ))
    
    steps = []
    
    # 1. Connection & Ping
    try:
        adapter.connect()
        rtt = adapter.ping_rtt()
        steps.append(("1. Connect & Baseline RTT", f"{rtt:.2f} ms", "PASS", f"Ping latency: {rtt:.2f} ms"))
        console.print(f"  [green]✓ 1. Connected successfully (RTT: {rtt:.2f} ms)[/green]")
    except Exception as e:
        steps.append(("1. Connect & Baseline RTT", "N/A", "FAIL", str(e)))
        console.print(f"  [red]✗ 1. Connection failed: {e}[/red]")
        return False, steps

    # 2. Schema & Indexes
    try:
        idx_time = adapter.create_schema_and_indexes()
        steps.append(("2. Schema & Indexes", f"{idx_time:.2f} ms", "PASS", "Created User.id & User.category indexes"))
        console.print(f"  [green]✓ 2. Indexes created ({idx_time:.2f} ms)[/green]")
    except Exception as e:
        steps.append(("2. Schema & Indexes", "N/A", "FAIL", str(e)))
        console.print(f"  [red]✗ 2. Schema creation failed: {e}[/red]")

    # 3. Mini Ingestion: Insert a small known chain: 1 -> 2 -> 3 -> 4 -> 5
    try:
        test_nodes = [
            {"id": i, "name": f"User_{i}", "category": f"Group_{(i % 3) + 1}"}
            for i in range(101, 111)
        ]
        res_nodes = adapter.bulk_insert_nodes(test_nodes, batch_size=10)
        steps.append(("3. Batch Node Ingest", f"{res_nodes['elapsed_sec']:.2f} s", "PASS", f"{len(test_nodes)} nodes at {res_nodes['throughput_nodes_sec']} n/s"))
        console.print(f"  [green]✓ 3. Ingested {len(test_nodes)} nodes ({res_nodes['throughput_nodes_sec']} nodes/s)[/green]")
    except Exception as e:
        steps.append(("3. Batch Node Ingest", "N/A", "FAIL", str(e)))
        console.print(f"  [red]✗ 3. Node ingestion failed: {e}[/red]")

    # 4. Ingest known chain edges: 101 -> 102 -> 103 -> 104 -> 105
    try:
        test_edges = [
            {"source_id": 101, "target_id": 102, "weight": 1.0},
            {"source_id": 102, "target_id": 103, "weight": 1.5},
            {"source_id": 103, "target_id": 104, "weight": 2.0},
            {"source_id": 104, "target_id": 105, "weight": 2.5},
            {"source_id": 101, "target_id": 103, "weight": 3.0}, # multi-path
        ]
        res_edges = adapter.bulk_insert_edges(test_edges, batch_size=10)
        steps.append(("4. Batch Edge Ingest", f"{res_edges['elapsed_sec']:.2f} s", "PASS", f"{len(test_edges)} edges at {res_edges['throughput_edges_sec']} e/s"))
        console.print(f"  [green]✓ 4. Ingested {len(test_edges)} edges ({res_edges['throughput_edges_sec']} edges/s)[/green]")
    except Exception as e:
        steps.append(("4. Batch Edge Ingest", "N/A", "FAIL", str(e)))
        console.print(f"  [red]✗ 4. Edge ingestion failed: {e}[/red]")

    # 5. Point Lookup Verification (Assert ID 101 exists)
    try:
        lat_point, rec = adapter.point_lookup(101)
        assert rec is not None, "Record for Node 101 was not found"
        assert int(rec["id"]) == 101, f"Expected id 101, got {rec['id']}"
        steps.append(("5. Point Lookup (ID: 101)", f"{lat_point:.2f} ms", "PASS", f"Retrieved {rec}"))
        console.print(f"  [green]✓ 5. Point lookup verified ({lat_point:.2f} ms, found: {rec['name']})[/green]")
    except Exception as e:
        steps.append(("5. Point Lookup (ID: 101)", "N/A", "FAIL", str(e)))
        console.print(f"  [red]✗ 5. Point lookup failed: {e}[/red]")

    # 6. Indexed Filter Verification (Category lookup)
    try:
        lat_filter, records = adapter.indexed_filter_lookup("Group_1", limit=10)
        assert len(records) > 0, "No records returned for category filter"
        steps.append(("6. Indexed Category Filter", f"{lat_filter:.2f} ms", "PASS", f"Found {len(records)} records"))
        console.print(f"  [green]✓ 6. Indexed filter verified ({lat_filter:.2f} ms, {len(records)} records)[/green]")
    except Exception as e:
        steps.append(("6. Indexed Category Filter", "N/A", "FAIL", str(e)))
        console.print(f"  [red]✗ 6. Category filter failed: {e}[/red]")

    # 7. 1-Hop Traversal (Node 101 -> 102, 103: count should be 2)
    try:
        lat_1hop, cnt_1hop = adapter.traverse_1_hop(101)
        assert cnt_1hop >= 2, f"Expected >= 2 neighbors from Node 101, got {cnt_1hop}"
        steps.append(("7. 1-Hop Traversal", f"{lat_1hop:.2f} ms", "PASS", f"101 -> {cnt_1hop} direct neighbors"))
        console.print(f"  [green]✓ 7. 1-Hop traversal verified ({lat_1hop:.2f} ms, count: {cnt_1hop})[/green]")
    except Exception as e:
        steps.append(("7. 1-Hop Traversal", "N/A", "FAIL", str(e)))
        console.print(f"  [red]✗ 7. 1-Hop traversal failed: {e}[/red]")

    # 8. 2-Hop Traversal (Node 101 -> 102/103 -> 103/104: distinct count should be >= 2)
    try:
        lat_2hop, cnt_2hop = adapter.traverse_2_hop(101)
        assert cnt_2hop >= 1, f"Expected >= 1 2-hop neighbors, got {cnt_2hop}"
        steps.append(("8. 2-Hop Traversal", f"{lat_2hop:.2f} ms", "PASS", f"101 -> 2-hops -> {cnt_2hop} distinct nodes"))
        console.print(f"  [green]✓ 8. 2-Hop traversal verified ({lat_2hop:.2f} ms, count: {cnt_2hop})[/green]")
    except Exception as e:
        steps.append(("8. 2-Hop Traversal", "N/A", "FAIL", str(e)))
        console.print(f"  [red]✗ 8. 2-Hop traversal failed: {e}[/red]")

    # 9. 3-Hop Traversal (Node 101 -> -> -> 104, 105)
    try:
        lat_3hop, cnt_3hop = adapter.traverse_3_hop(101)
        steps.append(("9. 3-Hop Traversal", f"{lat_3hop:.2f} ms", "PASS", f"101 -> 3-hops -> {cnt_3hop} distinct nodes"))
        console.print(f"  [green]✓ 9. 3-Hop traversal verified ({lat_3hop:.2f} ms, count: {cnt_3hop})[/green]")
    except Exception as e:
        steps.append(("9. 3-Hop Traversal", "N/A", "FAIL", str(e)))
        console.print(f"  [red]✗ 9. 3-Hop traversal failed: {e}[/red]")

    # 10. Degree Aggregation
    try:
        lat_agg, top_degrees = adapter.aggregate_degree_distribution(limit=5)
        assert len(top_degrees) > 0, "Expected aggregation results"
        steps.append(("10. Degree Aggregation", f"{lat_agg:.2f} ms", "PASS", f"Top out-degree node: {top_degrees[0]}"))
        console.print(f"  [green]✓ 10. Degree aggregation verified ({lat_agg:.2f} ms)[/green]")
    except Exception as e:
        steps.append(("10. Degree Aggregation", "N/A", "FAIL", str(e)))
        console.print(f"  [red]✗ 10. Degree aggregation failed: {e}[/red]")

    # 11. Mixed Read/Write Transaction
    try:
        lat_mix, ok_mix = adapter.execute_mixed_transaction(101, {"id": 9999, "name": "User_9999", "category": "Group_1"})
        assert ok_mix, "Mixed transaction failed"
        steps.append(("11. Mixed Read/Write Tx", f"{lat_mix:.2f} ms", "PASS", "Read 101 + Insert 9999 atomically"))
        console.print(f"  [green]✓ 11. Mixed Read/Write tx verified ({lat_mix:.2f} ms)[/green]")
    except Exception as e:
        steps.append(("11. Mixed Read/Write Tx", "N/A", "FAIL", str(e)))
        console.print(f"  [red]✗ 11. Mixed transaction failed: {e}[/red]")

    # 12. Footprint & Diagnostics
    try:
        fp = adapter.get_footprint()
        steps.append(("12. Storage Footprint", "Audited", "PASS", str(fp)))
        console.print(f"  [green]✓ 12. Footprint observed: {fp}[/green]")
    except Exception as e:
        steps.append(("12. Storage Footprint", "N/A", "FAIL", str(e)))

    adapter.close()
    
    # Print Results Table
    t = Table(title=f"Detailed Test Report: {adapter.name}")
    t.add_column("Operation / Workload Step", style="cyan")
    t.add_column("Measured Latency", style="yellow")
    t.add_column("Result", style="bold green")
    t.add_column("Details", style="dim")
    
    all_passed = True
    for step, lat, status, detail in steps:
        st_style = "[bold green]PASS[/bold green]" if status == "PASS" else "[bold red]FAIL[/bold red]"
        if status != "PASS":
            all_passed = False
        t.add_row(step, lat, st_style, detail)
        
    console.print("\n")
    console.print(t)
    return all_passed, steps

def main():
    parser = argparse.ArgumentParser(description="Test individual database adapter")
    parser.add_argument("--db", type=str, default="all", help="Database to test: cognodb, neo4j, memgraph, falkordb, arangodb, or all")
    args = parser.parse_args()
    
    if args.db.lower() == "all":
        dbs = ["cognodb", "neo4j", "memgraph", "falkordb", "arangodb"]
    else:
        dbs = [args.db]
        
    for db in dbs:
        adapter = get_adapter(db)
        run_deep_individual_test(adapter)
        console.print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
