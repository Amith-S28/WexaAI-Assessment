import os
import sys
import zlib
import json
import hashlib
import time
import requests
from pathlib import Path
from rich.console import Console
from rich.table import Table

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

console = Console(force_terminal=True, legacy_windows=False)

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SNAP_POKEC_URL = "https://snap.stanford.edu/data/soc-pokec-relationships.txt.gz"
NODES_CSV = DATA_DIR / "nodes.csv"
EDGES_CSV = DATA_DIR / "edges.csv"
METADATA_JSON = DATA_DIR / "metadata.json"

TARGET_RELATIONSHIPS = 350_000

def stream_and_parse_snap(url: str, target_edges: int = 350_000):
    console.print(f"[bold cyan]Streaming & decompressing SNAP soc-Pokec dataset on-the-fly...[/bold cyan]")
    
    t0 = time.perf_counter()
    edges = []
    unique_nodes = set()
    node_degrees = {}
    
    # HTTP stream with gzip decompressor
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()
    
    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
    buffer = ""
    downloaded_bytes = 0
    
    for chunk in response.iter_content(chunk_size=65536):
        if not chunk:
            continue
        downloaded_bytes += len(chunk)
        try:
            decompressed = d.decompress(chunk)
            buffer += decompressed.decode("utf-8", errors="ignore")
        except Exception:
            continue
            
        lines = buffer.split("\n")
        buffer = lines.pop() # keep incomplete last line in buffer
        
        for line in lines:
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
                        continue
                    
                    edges.append((src, dst))
                    unique_nodes.add(src)
                    unique_nodes.add(dst)
                    
                    node_degrees[src] = node_degrees.get(src, 0) + 1
                    node_degrees[dst] = node_degrees.get(dst, 0) + 1
                    
                    if len(edges) >= target_edges:
                        break
                except ValueError:
                    continue
                    
        if len(edges) % 50_000 == 0 or len(edges) >= target_edges:
            console.print(f"  [cyan]-> Parsed {len(edges):,} / {target_edges:,} relationships ({downloaded_bytes / 1e6:.2f} MB streamed)...[/cyan]")
            
        if len(edges) >= target_edges:
            break
            
    response.close()
    t1 = time.perf_counter()
    console.print(f"[bold green]Extracted {len(edges):,} relationships across {len(unique_nodes):,} unique nodes in {t1 - t0:.2f} seconds![/bold green]")
    
    # 1. Write nodes.csv
    console.print("[cyan]Generating normalized nodes.csv...[/cyan]")
    sorted_nodes = sorted(unique_nodes)
    with open(NODES_CSV, "w", encoding="utf-8", newline="") as f:
        f.write("id,name,category\n")
        for node_id in sorted_nodes:
            category = f"Group_{(node_id % 10) + 1}"
            f.write(f"{node_id},User_{node_id},{category}\n")
            
    # 2. Write edges.csv
    console.print("[cyan]Generating normalized edges.csv...[/cyan]")
    with open(EDGES_CSV, "w", encoding="utf-8", newline="") as f:
        f.write("source_id,target_id,type,weight\n")
        for src, dst in edges:
            weight = round(((src + dst) % 100) / 10.0 + 1.0, 2)
            f.write(f"{src},{dst},FOLLOWS,{weight}\n")
            
    # 3. MD5 Checksums & Metadata
    def get_md5(path):
        hasher = hashlib.md5()
        with open(path, "rb") as f:
            while c := f.read(65536):
                hasher.update(c)
        return hasher.hexdigest()

    nodes_md5 = get_md5(NODES_CSV)
    edges_md5 = get_md5(EDGES_CSV)
    
    degrees = list(node_degrees.values())
    avg_degree = sum(degrees) / len(degrees) if degrees else 0
    max_degree = max(degrees) if degrees else 0
    
    metadata = {
        "dataset_name": "SNAP soc-Pokec Social Network (Calibrated 350K Sample)",
        "source_url": SNAP_POKEC_URL,
        "calibrated_relationship_count": len(edges),
        "unique_node_count": len(unique_nodes),
        "relationship_type": "FOLLOWS",
        "average_node_degree": round(avg_degree, 2),
        "max_node_degree": max_degree,
        "nodes_file": "data/nodes.csv",
        "nodes_file_size_mb": round(NODES_CSV.stat().st_size / 1e6, 2),
        "nodes_file_md5": nodes_md5,
        "edges_file": "data/edges.csv",
        "edges_file_size_mb": round(EDGES_CSV.stat().st_size / 1e6, 2),
        "edges_file_md5": edges_md5,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    
    with open(METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    return metadata

def main():
    console.print("[bold magenta]============================================================[/bold magenta]")
    console.print("[bold magenta]    FAST STREAMING SNAP GRAPH DOWNLOADER & NORMALIZER       [/bold magenta]")
    console.print("[bold magenta]============================================================[/bold magenta]\n")
    
    meta = stream_and_parse_snap(SNAP_POKEC_URL, TARGET_RELATIONSHIPS)
    
    table = Table(title="350K Dataset Verification Summary")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="bold green")
    
    table.add_row("Dataset Name", meta["dataset_name"])
    table.add_row("Relationship Count", f"{meta['calibrated_relationship_count']:,}")
    table.add_row("Node Count", f"{meta['unique_node_count']:,}")
    table.add_row("Average Node Degree", str(meta["average_node_degree"]))
    table.add_row("Max Node Degree", str(meta["max_node_degree"]))
    table.add_row("Nodes CSV", f"{meta['nodes_file']} ({meta['nodes_file_size_mb']} MB)")
    table.add_row("Edges CSV", f"{meta['edges_file']} ({meta['edges_file_size_mb']} MB)")
    table.add_row("Nodes MD5 Checksum", meta["nodes_file_md5"])
    table.add_row("Edges MD5 Checksum", meta["edges_file_md5"])
    
    console.print("\n")
    console.print(table)

if __name__ == "__main__":
    main()
