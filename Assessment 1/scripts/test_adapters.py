import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

console = Console(force_terminal=True, legacy_windows=False)
load_dotenv()

from benchmarks.adapters import (
    CognoDBAdapter,
    Neo4jAdapter,
    MemgraphAdapter,
    FalkorDBAdapter,
    ArangoDBAdapter
)

def test_adapter(adapter):
    console.print(f"\n[bold cyan]─── Testing Adapter: {adapter.name} ({adapter.paradigm}) ───[/bold cyan]")
    try:
        # 1. Connect
        adapter.connect()
        rtt = adapter.ping_rtt()
        console.print(f"  [green]✓ Connected! RTT: {rtt:.2f} ms[/green]")
        
        # 2. Test schema
        idx_time = adapter.create_schema_and_indexes()
        console.print(f"  [green]✓ Schema & Index creation: {idx_time:.2f} ms[/green]")
        
        # 3. Test insert sample node
        test_nodes = [{"id": 999999, "name": "User_999999", "category": "Group_1"}]
        res_nodes = adapter.bulk_insert_nodes(test_nodes, batch_size=1)
        console.print(f"  [green]✓ Ingest sample node: {res_nodes['throughput_nodes_sec']} nodes/s[/green]")
        
        # 4. Test point lookup
        lat_point, rec = adapter.point_lookup(999999)
        console.print(f"  [green]✓ Point lookup latency: {lat_point:.2f} ms (Found: {rec is not None})[/green]")
        
        # 5. Test 1-hop traversal
        lat_hop, cnt = adapter.traverse_1_hop(999999)
        console.print(f"  [green]✓ 1-Hop traversal query: {lat_hop:.2f} ms (Neighbors: {cnt})[/green]")
        
        # 6. Test mixed transaction
        lat_mix, ok_mix = adapter.execute_mixed_transaction(999999, {"id": 999998, "name": "User_999998", "category": "Group_2"})
        console.print(f"  [green]✓ Mixed Read/Write transaction: {lat_mix:.2f} ms (Success: {ok_mix})[/green]")
        
        adapter.close()
        return True, "All Adapter Methods Verified"
    except Exception as e:
        console.print(f"  [bold red]✗ Failed on {adapter.name}: {e}[/bold red]")
        adapter.close()
        return False, str(e)

def main():
    console.print("[bold magenta]============================================================[/bold magenta]")
    console.print("[bold magenta]             5-DATABASE ADAPTER CONTRACT VERIFICATION       [/bold magenta]")
    console.print("[bold magenta]============================================================[/bold magenta]")
    
    adapters = [
        CognoDBAdapter(
            uri=os.getenv("COGNODB_URI"),
            user=os.getenv("COGNODB_USER", "cognodb"),
            password=os.getenv("COGNODB_PASSWORD")
        ),
        Neo4jAdapter(
            uri=os.getenv("NEO4J_URI"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD")
        ),
        MemgraphAdapter(
            uri=os.getenv("MEMGRAPH_URI"),
            user=os.getenv("MEMGRAPH_USER"),
            password=os.getenv("MEMGRAPH_PASSWORD")
        ),
        FalkorDBAdapter(
            host=os.getenv("FALKORDB_HOST"),
            port=int(os.getenv("FALKORDB_PORT", "6379")),
            user=os.getenv("FALKORDB_USER", "falkordb"),
            password=os.getenv("FALKORDB_PASSWORD")
        ),
        ArangoDBAdapter(
            url=os.getenv("ARANGODB_URL"),
            user=os.getenv("ARANGODB_USER", "root"),
            password=os.getenv("ARANGODB_PASSWORD")
        )
    ]
    
    summary = []
    for ad in adapters:
        ok, msg = test_adapter(ad)
        summary.append((ad.name, ad.paradigm, "PASS" if ok else "FAIL", msg))
        
    console.print("\n")
    table = Table(title="Adapter Contract & Functional Readiness Matrix")
    table.add_column("Database Adapter", style="cyan", no_wrap=True)
    table.add_column("Architecture Paradigm", style="dim")
    table.add_column("Status", style="bold green")
    table.add_column("Details", style="yellow")
    
    for name, paradigm, status, details in summary:
        s_style = "[bold green]PASS[/bold green]" if status == "PASS" else "[bold red]FAIL[/bold red]"
        table.add_row(name, paradigm, s_style, details)
        
    console.print(table)

if __name__ == "__main__":
    main()
