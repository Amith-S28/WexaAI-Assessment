"""
Workload Execution Engine.
Executes standard benchmark workloads across database adapters and collects raw percentile statistics.
"""

import time
import random
import csv
import statistics
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from .stats import LatencyStats
from .adapters.base import BaseGraphAdapter

console = Console(force_terminal=True, legacy_windows=False)

DATA_DIR = Path("d:/Projects/WEXA/data")
NODES_CSV = DATA_DIR / "nodes.csv"
EDGES_CSV = DATA_DIR / "edges.csv"

class WorkloadRunner:
    """Executes the full benchmark workload suite on a single graph database adapter."""
    
    def __init__(self, adapter: BaseGraphAdapter, iterations: int = 100, concurrency_levels: List[int] = None):
        self.adapter = adapter
        self.iterations = iterations
        self.concurrency_levels = concurrency_levels or [1, 10, 40]
        
        # Load dataset sample IDs for random query generation
        self.node_ids: List[int] = []
        self.categories: List[str] = [f"Group_{i}" for i in range(1, 11)]
        self._load_sample_ids()

    def _load_sample_ids(self, sample_size: int = 1000):
        """Extract a random pool of existing node IDs for deterministic randomized queries."""
        if NODES_CSV.exists():
            with open(NODES_CSV, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                all_ids = [int(row["id"]) for row in reader]
                random.seed(42) # Deterministic seed across all DBs
                self.node_ids = random.sample(all_ids, min(sample_size, len(all_ids)))
        else:
            self.node_ids = list(range(100, 1100))

    def load_dataset(self, node_limit: Optional[int] = None, edge_limit: Optional[int] = None) -> Tuple[List[Dict], List[Dict]]:
        """Load nodes and edges from normalized CSV files."""
        nodes = []
        with open(NODES_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if node_limit and i >= node_limit:
                    break
                nodes.append({
                    "id": int(row["id"]),
                    "name": row["name"],
                    "category": row["category"]
                })
                
        edges = []
        with open(EDGES_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if edge_limit and i >= edge_limit:
                    break
                edges.append({
                    "source_id": int(row["source_id"]),
                    "target_id": int(row["target_id"]),
                    "weight": float(row["weight"])
                })
                
        return nodes, edges

    def run_ingest_workload(self, nodes: List[Dict], edges: List[Dict], batch_size: int = 2000) -> Dict[str, Any]:
        """Workload 1: Schema creation, Node ingest, and Edge ingest."""
        console.print(f"[bold cyan]▶ [{self.adapter.name}] Executing Ingestion Workload ({len(nodes):,} nodes, {len(edges):,} edges)...[/bold cyan]")
        
        # 1. Reset
        self.adapter.reset_database()
        
        # 2. Schema / Indexing
        t_idx = self.adapter.create_schema_and_indexes()
        
        # 3. Ingest Nodes
        res_nodes = self.adapter.bulk_insert_nodes(nodes, batch_size=batch_size)
        
        # 4. Ingest Edges
        res_edges = self.adapter.bulk_insert_edges(edges, batch_size=batch_size)
        
        total_wall_clock = round(res_nodes["elapsed_sec"] + res_edges["elapsed_sec"], 2)
        
        results = {
            "index_build_time_ms": round(t_idx, 2),
            "nodes_ingested": res_nodes["total_nodes"],
            "nodes_elapsed_sec": res_nodes["elapsed_sec"],
            "nodes_per_sec": res_nodes["throughput_nodes_sec"],
            "edges_ingested": res_edges["total_edges"],
            "edges_elapsed_sec": res_edges["elapsed_sec"],
            "edges_per_sec": res_edges["throughput_edges_sec"],
            "total_ingest_wall_clock_sec": total_wall_clock
        }
        console.print(f"  [green]✓ Ingestion Complete: {res_nodes['throughput_nodes_sec']} nodes/s | {res_edges['throughput_edges_sec']} rels/s (Total: {total_wall_clock}s)[/green]")
        return results

    def run_warmup(self, warmup_runs: int = 20):
        """Workload 2: Untracked warmup queries to prime memory and query planners."""
        console.print(f"[dim]  ⚡ Warming up cache with {warmup_runs} untracked queries...[/dim]")
        for _ in range(warmup_runs):
            nid = random.choice(self.node_ids)
            try:
                self.adapter.point_lookup(nid)
                self.adapter.traverse_1_hop(nid)
            except Exception:
                pass

    def run_read_workloads(self) -> Dict[str, Any]:
        """Workload 3 & 4: Point Lookups, Indexed Filters, 1/2/3-Hop Traversals, Aggregations."""
        console.print(f"[bold cyan]▶ [{self.adapter.name}] Executing Query Latency Workloads ({self.iterations} iterations per query type)...[/bold cyan]")
        
        results = {}
        query_generators = [
            ("point_lookup", "Point Lookup (by ID)", lambda: self.adapter.point_lookup(random.choice(self.node_ids))),
            ("indexed_lookup", "Indexed Category Filter", lambda: self.adapter.indexed_filter_lookup(random.choice(self.categories), limit=20)),
            ("traversal_1_hop", "1-Hop Traversal", lambda: self.adapter.traverse_1_hop(random.choice(self.node_ids))),
            ("traversal_2_hop", "2-Hop Traversal", lambda: self.adapter.traverse_2_hop(random.choice(self.node_ids))),
            ("traversal_3_hop", "3-Hop Traversal", lambda: self.adapter.traverse_3_hop(random.choice(self.node_ids))),
            ("aggregation", "Degree Distribution Aggregation", lambda: self.adapter.aggregate_degree_distribution(limit=10)),
        ]
        
        for key, label, func in query_generators:
            latencies = []
            cold_latency = None
            
            t_start = time.perf_counter()
            
            # Real-time progress bar for iterations
            with tqdm(total=self.iterations, desc=f"  {label:30}", unit="query", ncols=90, leave=True) as pbar:
                for i in range(self.iterations):
                    lat_ms, _ = func()
                    if i == 0:
                        cold_latency = lat_ms
                    latencies.append(lat_ms)
                    current_p50 = statistics.median(latencies) if len(latencies) > 0 else lat_ms
                    pbar.set_postfix({"last": f"{lat_ms:.1f}ms", "p50": f"{current_p50:.1f}ms"})
                    pbar.update(1)
                    
            t_total = time.perf_counter() - t_start
            
            stats = LatencyStats(latencies, total_duration_sec=t_total, cold_latency_ms=cold_latency)
            results[key] = stats.to_dict()
            console.print(f"  [green]✓ {label:32}: {stats.summary_str()}[/green]")
            
        return results

    def run_concurrency_sweeps(self, duration_per_level_sec: int = 15) -> Dict[str, Any]:
        """Workload 5: Concurrency Sweeps (1, 10, 40 workers) under 80% Read / 20% Write load."""
        console.print(f"[bold cyan]▶ [{self.adapter.name}] Executing Concurrency Sweeps ({self.concurrency_levels} workers, {duration_per_level_sec}s per level)...[/bold cyan]")
        
        results = {}
        
        for concurrency in self.concurrency_levels:
            stop_time = time.time() + duration_per_level_sec
            tx_latencies = []
            success_count = 0
            fail_count = 0
            
            def worker_loop(worker_id: int):
                nonlocal success_count, fail_count
                local_lats = []
                while time.time() < stop_time:
                    read_id = random.choice(self.node_ids)
                    write_node = {
                        "id": 900_000 + random.randint(1, 100_000),
                        "name": f"Concurrent_User_{worker_id}",
                        "category": random.choice(self.categories)
                    }
                    lat_ms, ok = self.adapter.execute_mixed_transaction(read_id, write_node)
                    local_lats.append(lat_ms)
                    if ok:
                        success_count += 1
                    else:
                        fail_count += 1
                return local_lats

            t0 = time.perf_counter()
            
            # Visual progress bar for countdown duration
            with tqdm(total=duration_per_level_sec, desc=f"  Concurrency [{concurrency:2} Workers]    ", unit="s", ncols=90, leave=True) as pbar:
                with ThreadPoolExecutor(max_workers=concurrency) as pool:
                    futures = [pool.submit(worker_loop, w) for w in range(concurrency)]
                    start_sweep = time.time()
                    last_elapsed = 0
                    while any(not f.done() for f in futures):
                        time.sleep(0.5)
                        elapsed = min(int(time.time() - start_sweep), duration_per_level_sec)
                        inc = elapsed - last_elapsed
                        if inc > 0:
                            pbar.update(inc)
                            last_elapsed = elapsed
                        curr_tx = success_count + fail_count
                        curr_qps = curr_tx / max(1, (time.time() - start_sweep))
                        pbar.set_postfix({"TXs": curr_tx, "QPS": f"{curr_qps:.1f}"})
                        
                    for f in as_completed(futures):
                        tx_latencies.extend(f.result())
                # Ensure 100% full bar
                if pbar.n < duration_per_level_sec:
                    pbar.update(duration_per_level_sec - pbar.n)
                    
            total_duration = time.perf_counter() - t0
            
            stats = LatencyStats(tx_latencies, total_duration_sec=total_duration)
            level_dict = stats.to_dict()
            level_dict["concurrency"] = concurrency
            level_dict["success_count"] = success_count
            level_dict["fail_count"] = fail_count
            
            results[f"concurrency_{concurrency}_clients"] = level_dict
            console.print(f"  [green]✓ {concurrency:2} Clients: Sustained QPS: {stats.qps:6.2f} | p50: {stats.p50:6.2f}ms | p95: {stats.p95:6.2f}ms | (Success: {success_count:,}, Fails: {fail_count})[/green]")
            
        return results

    def run_full_suite(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, Any]:
        """Executes the complete benchmark suite for this adapter."""
        console.print(f"\n[bold magenta]{'='*80}[/bold magenta]")
        console.print(f"[bold magenta]     BENCHMARKING: {self.adapter.name} ({self.adapter.paradigm})[/bold magenta]")
        console.print(f"[bold magenta]{'='*80}[/bold magenta]\n")
        
        # 1. Baseline RTT Ping
        rtt_ms = self.adapter.ping_rtt()
        console.print(f"[bold cyan]Baseline Network RTT (Ping): {rtt_ms:.2f} ms[/bold cyan]")
        
        # 2. Ingest
        ingest_res = self.run_ingest_workload(nodes, edges)
        
        # 3. Warmup
        self.run_warmup(warmup_runs=20)
        
        # 4. Read Latencies
        read_res = self.run_read_workloads()
        
        # 5. Concurrency Sweeps
        concurrency_res = self.run_concurrency_sweeps()
        
        # 6. Footprint
        footprint_res = self.adapter.get_footprint()
        
        full_results = {
            "adapter_name": self.adapter.name,
            "database_type": self.adapter.db_type,
            "paradigm": self.adapter.paradigm,
            "baseline_rtt_ms": round(rtt_ms, 2),
            "ingest": ingest_res,
            "queries": read_res,
            "concurrency": concurrency_res,
            "footprint": footprint_res,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        return full_results
