"""
Benchmark Suite Orchestrator.
Coordinates loading dataset, running workloads across database adapters, saving raw telemetry, and generating visual reports.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmarks.adapters import (
    CognoDBAdapter,
    Neo4jAdapter,
    MemgraphAdapter,
    FalkorDBAdapter,
    ArangoDBAdapter
)
from benchmarks.workload_runner import WorkloadRunner
from benchmarks.report_generator import ReportGenerator

console = Console(force_terminal=True, legacy_windows=False)
load_dotenv()

RESULTS_DIR = Path("d:/Projects/WEXA/results")
ASSETS_DIR = Path("d:/Projects/WEXA/assets")

class BenchmarkOrchestrator:
    """Orchestrates benchmark runs across multiple graph databases."""
    
    def __init__(
        self, 
        selected_dbs: List[str] = None, 
        iterations: int = 100, 
        node_limit: Optional[int] = None, 
        edge_limit: Optional[int] = None,
        results_dir: Optional[Path] = None,
        assets_dir: Optional[Path] = None,
        clean: bool = False,
        env_file: Optional[str] = None
    ):
        if env_file:
            load_dotenv(env_file, override=True)
        else:
            load_dotenv(override=True)
            
        self.selected_dbs = [db.lower() for db in (selected_dbs or ["cognodb", "neo4j", "memgraph", "falkordb", "arangodb"])]
        self.iterations = iterations
        self.node_limit = node_limit
        self.edge_limit = edge_limit
        self.results_dir = Path(results_dir) if results_dir else RESULTS_DIR
        self.assets_dir = Path(assets_dir) if assets_dir else ASSETS_DIR
        self.clean = clean
        
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)

    def _get_adapters(self) -> List[Any]:
        adapters = []
        if "cognodb" in self.selected_dbs:
            adapters.append(CognoDBAdapter(
                uri=os.getenv("COGNODB_URI"),
                user=os.getenv("COGNODB_USER", "cognodb"),
                password=os.getenv("COGNODB_PASSWORD")
            ))
        if "neo4j" in self.selected_dbs:
            adapters.append(Neo4jAdapter(
                uri=os.getenv("NEO4J_URI"),
                user=os.getenv("NEO4J_USER", "neo4j"),
                password=os.getenv("NEO4J_PASSWORD")
            ))
        if "memgraph" in self.selected_dbs:
            adapters.append(MemgraphAdapter(
                uri=os.getenv("MEMGRAPH_URI"),
                user=os.getenv("MEMGRAPH_USER"),
                password=os.getenv("MEMGRAPH_PASSWORD")
            ))
        if "falkordb" in self.selected_dbs:
            adapters.append(FalkorDBAdapter(
                host=os.getenv("FALKORDB_HOST"),
                port=int(os.getenv("FALKORDB_PORT", "6379")),
                user=os.getenv("FALKORDB_USER", "falkordb"),
                password=os.getenv("FALKORDB_PASSWORD")
            ))
        if "arangodb" in self.selected_dbs:
            adapters.append(ArangoDBAdapter(
                url=os.getenv("ARANGODB_URL"),
                user=os.getenv("ARANGODB_USER", "root"),
                password=os.getenv("ARANGODB_PASSWORD")
            ))
        return adapters

    def run(self) -> Dict[str, Any]:
        console.print("[bold cyan]========================================================================[/bold cyan]")
        console.print("[bold cyan]       WEXA AI GRAPH DATABASE CLOUD BENCHMARK ORCHESTRATOR              [/bold cyan]")
        console.print("[bold cyan]========================================================================[/bold cyan]")
        console.print(f"[dim]Results Target: {self.results_dir} | Assets Target: {self.assets_dir} | Clean Slate: {self.clean}[/dim]\n")
        
        adapters = self._get_adapters()
        if not adapters:
            console.print("[bold red]No valid database adapters selected![/bold red]")
            return {}
            
        # Load normalized dataset once
        console.print(f"[bold yellow]Loading normalized Pokec dataset from CSV...[/bold yellow]")
        dummy_runner = WorkloadRunner(adapters[0])
        nodes, edges = dummy_runner.load_dataset(node_limit=self.node_limit, edge_limit=self.edge_limit)
        console.print(f"[bold green]✓ Loaded {len(nodes):,} Nodes and {len(edges):,} Edges into memory[/bold green]\n")
        
        all_results = {}
        total_dbs = len(adapters)
        
        for idx, adapter in enumerate(adapters, start=1):
            pct = int(((idx - 1) / total_dbs) * 100)
            console.print(f"\n[bold yellow]╔{'═'*78}╗[/bold yellow]")
            console.print(f"[bold yellow]║  DATABASE {idx}/{total_dbs} ({pct}% Total Progress): {adapter.name.upper():<44} ║[/bold yellow]")
            console.print(f"[bold yellow]╚{'═'*78}╝[/bold yellow]")
            try:
                adapter.connect()
                runner = WorkloadRunner(adapter, iterations=self.iterations)
                res = runner.run_full_suite(nodes, edges)
                all_results[adapter.name] = res
            except Exception as e:
                console.print(f"[bold red]✗ Benchmark failed for {adapter.name}: {e}[/bold red]")
            finally:
                adapter.close()
                
        # Load existing results if present to merge, unless clean slate requested
        raw_json_path = self.results_dir / "benchmark_results.json"
        existing_results = {}
        if not self.clean and raw_json_path.exists():
            try:
                with open(raw_json_path, "r", encoding="utf-8") as f:
                    existing_results = json.load(f)
            except Exception:
                pass
                
        existing_results.update(all_results)
        
        # Save merged raw results JSON
        with open(raw_json_path, "w", encoding="utf-8") as f:
            json.dump(existing_results, f, indent=2)
        console.print(f"\n[bold green]✓ Saved raw telemetry JSON to {raw_json_path}[/bold green]")
        
        # Generate Visual Charts and Tables with full merged suite
        if existing_results:
            console.print("[bold cyan]▶ Generating publication-grade visualization charts...[/bold cyan]")
            report_gen = ReportGenerator(existing_results, output_dir=self.assets_dir)
            report_gen.generate_all_charts()
            console.print(f"[bold green]✓ Base charts generated in {self.assets_dir}/[/bold green]")
            
            # Also generate advanced metric diagrams (radar, dumbbell, speedup, quadrant)
            try:
                from scripts.generate_metric_diagrams import generate_all_metric_diagrams
                generate_all_metric_diagrams(existing_results, output_dir=self.assets_dir)
                console.print(f"[bold green]✓ Advanced diagrams generated in {self.assets_dir}/[/bold green]")
            except Exception as e:
                console.print(f"[dim]Advanced diagram generator notice: {e}[/dim]")
                
            markdown_tables = report_gen.generate_markdown_tables()
            md_path = self.results_dir / "summary_tables.md"
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(markdown_tables)
            console.print(f"[bold green]✓ Saved Markdown summary tables to {md_path}[/bold green]")
            
        return existing_results
