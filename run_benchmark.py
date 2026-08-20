"""
Root CLI Runner for Wexa AI Graph Database Cloud Benchmarks.
Usage:
    python run_benchmark.py --all
    python run_benchmark.py --db cognodb,neo4j,memgraph
    python run_benchmark.py --nodes 10000 --edges 50000 --iterations 50
"""

import sys
import argparse
import warnings
import urllib3
from pathlib import Path

# Suppress library deprecation and unverified HTTPS warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from benchmarks.orchestrator import BenchmarkOrchestrator

def main():
    parser = argparse.ArgumentParser(description="Wexa AI Graph Database Cloud Benchmark Runner")
    parser.add_argument("--all", action="store_true", help="Run benchmark across all databases")
    parser.add_argument("--db", type=str, default="all", help="Comma-separated DBs: cognodb,neo4j,memgraph,falkordb,arangodb,kuzu,arcadedb,janusgraph or 'all'")
    parser.add_argument("--nodes", type=int, default=None, help="Limit number of nodes to ingest (default: all ~148k)")
    parser.add_argument("--edges", type=int, default=None, help="Limit number of edges to ingest (default: all 350k)")
    parser.add_argument("--iterations", type=int, default=100, help="Number of query repetitions for percentile stats (default: 100)")
    parser.add_argument("--output-dir", type=str, default="results", help="Directory to save raw telemetry JSON and summary tables (default: results)")
    parser.add_argument("--assets-dir", type=str, default="assets", help="Directory to save generated charts (default: assets)")
    parser.add_argument("--clean", action="store_true", help="Start fresh without loading residual results from target directory")
    parser.add_argument("--env-file", type=str, default=None, help="Path to custom .env file (e.g. .env.local)")
    
    args = parser.parse_args()
    
    if args.all or args.db.lower() == "all":
        selected = ["cognodb", "neo4j", "memgraph", "falkordb", "arangodb", "kuzu", "arcadedb", "janusgraph"]
    else:
        selected = [d.strip() for d in args.db.split(",")]
        
    orchestrator = BenchmarkOrchestrator(
        selected_dbs=selected,
        iterations=args.iterations,
        node_limit=args.nodes,
        edge_limit=args.edges,
        results_dir=Path(args.output_dir),
        assets_dir=Path(args.assets_dir),
        clean=args.clean,
        env_file=args.env_file
    )
    orchestrator.run()

if __name__ == "__main__":
    main()
