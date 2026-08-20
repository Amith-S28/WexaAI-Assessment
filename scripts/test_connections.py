import os
import sys
import time

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from neo4j import GraphDatabase
from rich.console import Console
from rich.table import Table

console = Console(force_terminal=True, legacy_windows=False)

def test_bolt_connection(name, uri, user, password):
    console.print(f"[bold cyan]Testing {name}...[/bold cyan]")
    if not uri or "your-instance" in uri:
        console.print(f"[yellow][!] {name}: URI not configured in .env[/yellow]")
        return False, "Not configured"
    
    t0 = time.perf_counter_ns()
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("RETURN 1 AS ping")
            record = result.single()
            val = record["ping"]
        t1 = time.perf_counter_ns()
        rtt_ms = (t1 - t0) / 1_000_000
        driver.close()
        
        console.print(f"[bold green][OK] {name} connected successfully! RTT + Ping: {rtt_ms:.2f} ms (Result: {val})[/bold green]")
        return True, f"{rtt_ms:.2f} ms"
    except Exception as e:
        console.print(f"[bold red][FAIL] {name} connection failed: {e}[/bold red]")
        return False, str(e)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Test Database Connectivity")
    parser.add_argument("--env-file", type=str, default=None, help="Path to custom env file (e.g. .env.local)")
    args = parser.parse_args()
    
    if args.env_file:
        load_dotenv(args.env_file, override=True)
    else:
        load_dotenv(override=True)
        
    console.print("[bold magenta]====================================================[/bold magenta]")
    console.print("[bold magenta]       PRE-FLIGHT DATABASE CONNECTIVITY PROBE       [/bold magenta]")
    console.print("[bold magenta]====================================================[/bold magenta]\n")
    
    results = []
    
    # 1. CognoDB Cloud
    cognoDB_uri = os.getenv("COGNODB_URI")
    cognoDB_user = os.getenv("COGNODB_USER", "cognodb")
    cognoDB_pwd = os.getenv("COGNODB_PASSWORD")
    ok1, msg1 = test_bolt_connection("CognoDB Cloud", cognoDB_uri, cognoDB_user, cognoDB_pwd)
    results.append(("CognoDB Cloud", cognoDB_uri, "Connected" if ok1 else "Failed", msg1))
    
    # 2. Neo4j AuraDB Free
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_pwd = os.getenv("NEO4J_PASSWORD")
    ok2, msg2 = test_bolt_connection("Neo4j AuraDB Free", neo4j_uri, neo4j_user, neo4j_pwd)
    results.append(("Neo4j AuraDB Free", neo4j_uri, "Connected" if ok2 else "Failed", msg2))
    
    # 3. Memgraph Cloud
    memgraph_uri = os.getenv("MEMGRAPH_URI")
    memgraph_user = os.getenv("MEMGRAPH_USER")
    memgraph_pwd = os.getenv("MEMGRAPH_PASSWORD")
    ok3, msg3 = test_bolt_connection("Memgraph Cloud", memgraph_uri, memgraph_user, memgraph_pwd)
    results.append(("Memgraph Cloud", memgraph_uri, "Connected" if ok3 else "Failed", msg3))
    
    # 4. FalkorDB Cloud
    falkor_host = os.getenv("FALKORDB_HOST")
    falkor_port = int(os.getenv("FALKORDB_PORT", "6379"))
    falkor_user = os.getenv("FALKORDB_USER", "falkordb")
    falkor_pwd = os.getenv("FALKORDB_PASSWORD")
    
    console.print(f"[bold cyan]Testing FalkorDB ({falkor_host}:{falkor_port})...[/bold cyan]")
    if falkor_host:
        try:
            from falkordb import FalkorDB
            t0 = time.perf_counter_ns()
            client = FalkorDB(host=falkor_host, port=falkor_port, username=falkor_user or None, password=falkor_pwd or None)
            g = client.select_graph("benchmark_test")
            res = g.query("RETURN 1 AS ping")
            t1 = time.perf_counter_ns()
            rtt_ms = (t1 - t0) / 1_000_000
            val = res.result_set[0][0]
            console.print(f"[bold green][OK] FalkorDB connected successfully! RTT: {rtt_ms:.2f} ms (Result: {val})[/bold green]")
            results.append(("FalkorDB", f"{falkor_host}:{falkor_port}", "Connected", f"{rtt_ms:.2f} ms"))
        except Exception as e:
            console.print(f"[bold red][FAIL] FalkorDB connection failed: {e}[/bold red]")
            results.append(("FalkorDB", f"{falkor_host}:{falkor_port}", "Failed", str(e)))
    else:
        results.append(("FalkorDB", "Not configured", "Failed", "Missing FALKORDB_HOST"))

    # 5. ArangoDB Oasis Cloud
    arango_url = os.getenv("ARANGODB_URL")
    arango_user = os.getenv("ARANGODB_USER", "root")
    arango_pwd = os.getenv("ARANGODB_PASSWORD")
    
    console.print(f"[bold cyan]Testing ArangoDB ({arango_url})...[/bold cyan]")
    if arango_url:
        try:
            from arango import ArangoClient
            t0 = time.perf_counter_ns()
            client = ArangoClient(hosts=arango_url, verify_override=False)
            sys_db = client.db("_system", username=arango_user, password=arango_pwd)
            ver = sys_db.version()
            t1 = time.perf_counter_ns()
            rtt_ms = (t1 - t0) / 1_000_000
            console.print(f"[bold green][OK] ArangoDB connected successfully! RTT: {rtt_ms:.2f} ms (Version: {ver})[/bold green]")
            results.append(("ArangoDB", arango_url, "Connected", f"{rtt_ms:.2f} ms (v{ver})"))
        except Exception as e:
            console.print(f"[bold red][FAIL] ArangoDB connection failed: {e}[/bold red]")
            results.append(("ArangoDB", arango_url, "Failed", str(e)))
    else:
        results.append(("ArangoDB", "Not configured", "Failed", "Missing ARANGODB_URL"))
    
    # 6. KuzuDB
    kuzu_ep = os.getenv("KUZU_ENDPOINT", "http://localhost:8000")
    console.print(f"[bold cyan]Testing KuzuDB ({kuzu_ep})...[/bold cyan]")
    if kuzu_ep:
        try:
            import requests
            t0 = time.perf_counter_ns()
            r = requests.post(f"{kuzu_ep}/api/cypher", json={"query": "RETURN 1 AS ping"}, timeout=5)
            t1 = time.perf_counter_ns()
            if r.status_code == 200:
                rtt_ms = (t1 - t0) / 1_000_000
                console.print(f"[bold green][OK] KùzuDB connected successfully! RTT: {rtt_ms:.2f} ms[/bold green]")
                results.append(("KùzuDB", kuzu_ep, "Connected", f"{rtt_ms:.2f} ms"))
            else:
                results.append(("KùzuDB", kuzu_ep, "Failed", f"HTTP {r.status_code}"))
        except Exception as e:
            console.print(f"[bold red][FAIL] KùzuDB connection failed: {e}[/bold red]")
            results.append(("KùzuDB", kuzu_ep, "Failed", str(e)))

    # 7. ArcadeDB
    arcade_url = os.getenv("ARCADEDB_URL", "http://localhost:2480")
    arcade_user = os.getenv("ARCADEDB_USER", "root")
    arcade_pwd = os.getenv("ARCADEDB_PASSWORD", "benchmarkpassword")
    console.print(f"[bold cyan]Testing ArcadeDB ({arcade_url})...[/bold cyan]")
    if arcade_url:
        try:
            import requests
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(arcade_user, arcade_pwd)
            t0 = time.perf_counter_ns()
            # Ensure database exists
            try:
                requests.post(f"{arcade_url}/api/v1/server", auth=auth, json={"command": "create database benchmark"}, timeout=3)
            except Exception:
                pass
            r = requests.post(f"{arcade_url}/api/v1/command/benchmark", auth=auth, json={"language": "cypher", "command": "RETURN 1 AS ping"}, timeout=5)
            t1 = time.perf_counter_ns()
            if r.status_code == 200:
                rtt_ms = (t1 - t0) / 1_000_000
                console.print(f"[bold green][OK] ArcadeDB connected successfully! RTT: {rtt_ms:.2f} ms[/bold green]")
                results.append(("ArcadeDB", arcade_url, "Connected", f"{rtt_ms:.2f} ms"))
            else:
                results.append(("ArcadeDB", arcade_url, "Failed", f"HTTP {r.status_code}"))
        except Exception as e:
            console.print(f"[bold red][FAIL] ArcadeDB connection failed: {e}[/bold red]")
            results.append(("ArcadeDB", arcade_url, "Failed", str(e)))

    # 8. JanusGraph
    janus_ep = os.getenv("JANUSGRAPH_ENDPOINT", "http://localhost:8182")
    console.print(f"[bold cyan]Testing JanusGraph ({janus_ep})...[/bold cyan]")
    if janus_ep:
        try:
            import requests
            t0 = time.perf_counter_ns()
            r = requests.post(janus_ep, json={"gremlin": "1 + 1"}, timeout=5)
            t1 = time.perf_counter_ns()
            if r.status_code == 200:
                rtt_ms = (t1 - t0) / 1_000_000
                console.print(f"[bold green][OK] JanusGraph connected successfully! RTT: {rtt_ms:.2f} ms[/bold green]")
                results.append(("JanusGraph", janus_ep, "Connected", f"{rtt_ms:.2f} ms"))
            else:
                results.append(("JanusGraph", janus_ep, "Failed", f"HTTP {r.status_code}"))
        except Exception as e:
            console.print(f"[bold red][FAIL] JanusGraph connection failed: {e}[/bold red]")
            results.append(("JanusGraph", janus_ep, "Failed", str(e)))

    console.print("\n")
    table = Table(title="Database Connectivity Summary")
    table.add_column("Database", style="cyan", no_wrap=True)
    table.add_column("URI Endpoint", style="magenta")
    table.add_column("Status", style="bold green")
    table.add_column("Latency / Info", style="yellow")
    
    for db, uri, status, info in results:
        status_style = "[bold green]ONLINE[/bold green]" if status == "Connected" else "[bold red]OFFLINE[/bold red]"
        table.add_row(db, uri, status_style, info)
        
    console.print(table)

if __name__ == "__main__":
    main()
