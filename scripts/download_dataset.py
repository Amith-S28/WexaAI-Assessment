import os
import sys
import gzip
import json
import hashlib
import time
import requests
from pathlib import Path
from tqdm import tqdm
from rich.console import Console
from rich.table import Table

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

console = Console(force_terminal=True, legacy_windows=False)

DATA_DIR = Path("d:/Projects/WEXA/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

SNAP_POKEC_URL = "https://snap.stanford.edu/data/soc-pokec-relationships.txt.gz"
RAW_FILE = DATA_DIR / "soc-pokec-relationships.txt.gz"
NODES_CSV = DATA_DIR / "nodes.csv"
EDGES_CSV = DATA_DIR / "edges.csv"
METADATA_JSON = DATA_DIR / "metadata.json"

TARGET_RELATIONSHIPS = 350_000

def download_file(url: str, dest_path: Path):
    if dest_path.exists() and dest_path.stat().st_size > 10_000_000:
        console.print(f"[green]Raw archive already exists at {dest_path} ({dest_path.stat().st_size / 1e6:.1f} MB). Skipping download.[/green]")
        return
    
    console.print(f"[bold cyan]Downloading SNAP soc-Pokec dataset from {url}...[/bold cyan]")
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()
    total_size = int(response.headers.get("content-length", 0))
    
    with open(dest_path, "wb") as f, tqdm(
        total=total_size, unit="B", unit_scale=True, desc="Downloading"
    ) as pbar:
        for chunk in response.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)
                pbar.update(len(chunk))
    console.print(f"[bold green]Downloaded successfully to {dest_path}[/bold green]")

def process_dataset(raw_gz_path: Path, target_edges: int = 350_000):
    console.print(f"[bold cyan]Parsing and sampling {target_edges:,} relationships...[/bold cyan]")
    
    edges = []
    unique_nodes = set()
    node_degrees = {}
    
    # Read gzipped text file line by line
    with gzip.open(raw_gz_path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                parts = line.split()
            if len(parts) >= 2:
                try:
                    src = int(parts[0])
                    dst = int(parts[1])
                    if src == dst:
                        continue # skip self loops
                    
                    edges.append((src, dst))
                    unique_nodes.add(src)
                    unique_nodes.add(dst)
                    
                    node_degrees[src] = node_degrees.get(src, 0) + 1
                    node_degrees[dst] = node_degrees.get(dst, 0) + 1
                    
                    if len(edges) >= target_edges:
                        break
                except ValueError:
                    continue
                    
    console.print(f"[bold green]Extracted {len(edges):,} relationships across {len(unique_nodes):,} unique nodes.[/bold green]")
    
    # Write normalized nodes.csv
    console.print("[cyan]Writing nodes.csv...[/cyan]")
    sorted_nodes = sorted(unique_nodes)
    with open(NODES_CSV, "w", encoding="utf-8", newline="") as f:
        f.write("id,name,category\n")
        for node_id in sorted_nodes:
            # Deterministic category assigned based on ID hash for indexed filtering workloads
            category = f"Group_{(node_id % 10) + 1}"
            f.write(f"{node_id},User_{node_id},{category}\n")
            
    # Write normalized edges.csv
    console.print("[cyan]Writing edges.csv...[/cyan]")
    with open(EDGES_CSV, "w", encoding="utf-8", newline="") as f:
        f.write("source_id,target_id,type,weight\n")
        for i, (src, dst) in enumerate(edges):
            weight = round(((src + dst) % 100) / 10.0 + 1.0, 2)
            f.write(f"{src},{dst},FOLLOWS,{weight}\n")
            
    # Calculate checksums & metadata
    def get_md5(path):
        hasher = hashlib.md5()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    nodes_md5 = get_md5(NODES_CSV)
    edges_md5 = get_md5(EDGES_CSV)
    
    degrees = list(node_degrees.values())
    avg_degree = sum(degrees) / len(degrees) if degrees else 0
    max_degree = max(degrees) if degrees else 0
    
    metadata = {
        "dataset_name": "SNAP soc-Pokec Social Network Sample",
        "source_url": SNAP_POKEC_URL,
        "calibrated_relationship_count": len(edges),
        "unique_node_count": len(unique_nodes),
        "relationship_type": "FOLLOWS",
        "average_node_degree": round(avg_degree, 2),
        "max_node_degree": max_degree,
        "nodes_file": "data/nodes.csv",
        "nodes_file_md5": nodes_md5,
        "edges_file": "data/edges.csv",
        "edges_file_md5": edges_md5,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    
    with open(METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    return metadata

def main():
    console.print("[bold magenta]============================================================[/bold magenta]")
    console.print("[bold magenta]         SNAP GRAPH DATASET DOWNLOADER & NORMALIZER         [/bold magenta]")
    console.print("[bold magenta]============================================================[/bold magenta]\n")
    
    download_file(SNAP_POKEC_URL, RAW_FILE)
    meta = process_dataset(RAW_FILE, TARGET_RELATIONSHIPS)
    
    table = Table(title="Normalized Dataset Summary")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="bold green")
    
    table.add_row("Dataset Name", meta["dataset_name"])
    table.add_row("Relationship Count", f"{meta['calibrated_relationship_count']:,}")
    table.add_row("Node Count", f"{meta['unique_node_count']:,}")
    table.add_row("Average Node Degree", str(meta["average_node_degree"]))
    table.add_row("Max Node Degree", str(meta["max_node_degree"]))
    table.add_row("Nodes CSV", f"{meta['nodes_file']} ({NODES_CSV.stat().st_size / 1e6:.2f} MB)")
    table.add_row("Edges CSV", f"{meta['edges_file']} ({EDGES_CSV.stat().st_size / 1e6:.2f} MB)")
    table.add_row("Nodes MD5", meta["nodes_file_md5"])
    table.add_row("Edges MD5", meta["edges_file_md5"])
    
    console.print("\n")
    console.print(table)

if __name__ == "__main__":
    main()
