import argparse
import sys
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Force UTF-8 encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Segoe UI", "Helvetica", "Arial"]
plt.rcParams["axes.edgecolor"] = "#CBD5E1"
plt.rcParams["axes.linewidth"] = 0.8

DEFAULT_RESULTS_FILE = Path("d:/Projects/WEXA/results/benchmark_results.json")
DEFAULT_ASSETS_DIR = Path("d:/Projects/WEXA/assets")

DB_COLORS = {
    "CognoDB Cloud": "#EB6C36",    # Coral/Tangerine
    "Neo4j AuraDB": "#0284C7",     # Sky Blue
    "Memgraph Cloud": "#10B981",   # Emerald Green
    "FalkorDB Cloud": "#8B5CF6",   # Purple
    "ArangoDB Oasis": "#F59E0B"    # Amber
}

def load_data(file_path: Path = DEFAULT_RESULTS_FILE):
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Missing {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def _normalize(values, higher_is_better=True):
    """Min-max normalize a list of values to 0-100 scale."""
    vmin, vmax = min(values), max(values)
    if vmax == vmin:
        return [50.0] * len(values)
    if higher_is_better:
        return [round(100 * (v - vmin) / (vmax - vmin), 1) for v in values]
    else:
        return [round(100 * (vmax - v) / (vmax - vmin), 1) for v in values]


def generate_radar_chart(data, output_dir: Path = DEFAULT_ASSETS_DIR):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    categories = [
        "Ingestion\nThroughput",
        "Traversal\nSpeed (Low p50)",
        "Tail Latency\nStability (Low Δ)",
        "Concurrency\nScaling (40x QPS)",
    ]
    N = len(categories)
    
    # Extract raw metrics from benchmark data
    db_names = list(data.keys())
    
    # Axis 1: Edge ingestion throughput (higher is better)
    raw_ingest = [data[db].get("ingest", {}).get("edges_per_sec", 0) for db in db_names]
    
    # Axis 2: Average traversal p50 across 1-hop, 2-hop, 3-hop (lower is better)
    raw_traverse = []
    for db in db_names:
        queries = data[db].get("queries", {})
        hops = []
        for key in ["traversal_1_hop", "traversal_2_hop", "traversal_3_hop"]:
            p50 = queries.get(key, {}).get("p50_ms", 0)
            if p50 > 0:
                hops.append(p50)
        raw_traverse.append(sum(hops) / len(hops) if hops else 999)
    
    # Axis 3: Tail jitter = average (p95 - p50) across all query types (lower is better)
    raw_jitter = []
    for db in db_names:
        queries = data[db].get("queries", {})
        deltas = []
        for qstats in queries.values():
            p50 = qstats.get("p50_ms", 0)
            p95 = qstats.get("p95_ms", 0)
            if p50 > 0 and p95 > 0:
                deltas.append(p95 - p50)
        raw_jitter.append(sum(deltas) / len(deltas) if deltas else 999)
    
    # Axis 4: 40-client sustained QPS (higher is better)
    raw_qps40 = [data[db].get("concurrency", {}).get("concurrency_40_clients", {}).get("qps", 0) for db in db_names]
    
    # Normalize each axis to 0-100
    norm_ingest = _normalize(raw_ingest, higher_is_better=True)
    norm_traverse = _normalize(raw_traverse, higher_is_better=False)
    norm_jitter = _normalize(raw_jitter, higher_is_better=False)
    norm_qps = _normalize(raw_qps40, higher_is_better=True)
    
    # Build scores dict: floor at 10 to keep the chart readable
    scores = {}
    for i, db in enumerate(db_names):
        scores[db] = [
            max(10, norm_ingest[i]),
            max(10, norm_traverse[i]),
            max(10, norm_jitter[i]),
            max(10, norm_qps[i]),
        ]
    
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(9, 8), subplot_kw=dict(polar=True), facecolor="#F8FAFC")
    ax.set_facecolor("#FFFFFF")
    
    plt.xticks(angles[:-1], categories, color="#1E293B", size=11, weight="bold")
    ax.set_rlabel_position(30)
    plt.yticks([25, 50, 75, 100], ["25", "50", "75", "100"], color="#64748B", size=9)
    plt.ylim(0, 105)
    
    for db_name, values in scores.items():
        vals = values + values[:1]
        color = DB_COLORS.get(db_name, "#475569")
        ax.plot(angles, vals, linewidth=2.0, linestyle="solid", label=db_name, color=color)
        ax.fill(angles, vals, color=color, alpha=0.10)
        
    plt.title("Multi-Dimensional Engine Performance Profile\n(Data-Derived Min-Max Normalization · 0-100 Scale)", 
              size=14, weight="bold", color="#0F172A", pad=28)
    plt.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), frameon=True, facecolor="#FFFFFF", edgecolor="#E2E8F0")
    plt.tight_layout()
    plt.savefig(output_dir / "radar_performance_profile.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✓ Saved {output_dir}/radar_performance_profile.png")


def generate_jitter_dumbbell_chart(data, output_dir: Path = DEFAULT_ASSETS_DIR):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor="#F8FAFC")
    ax.set_facecolor("#FFFFFF")
    
    dbs = []
    p50s = []
    p95s = []
    
    for db_name, profile in data.items():
        q_stats = profile.get("queries", {}).get("traversal_1_hop", {})
        p50 = q_stats.get("p50_ms", q_stats.get("p50"))
        p95 = q_stats.get("p95_ms", q_stats.get("p95"))
        if p50 is not None and p95 is not None:
            dbs.append(db_name)
            p50s.append(p50)
            p95s.append(p95)
            
    if not dbs:
        return
        
    # Sort by p95-p50 jitter ascending (tightest variance first)
    jitters = [p95 - p50 for p50, p95 in zip(p50s, p95s)]
    sorted_indices = np.argsort(jitters)
    
    dbs = [dbs[i] for i in sorted_indices]
    p50s = [p50s[i] for i in sorted_indices]
    p95s = [p95s[i] for i in sorted_indices]
    jitters = [jitters[i] for i in sorted_indices]
    
    y_pos = np.arange(len(dbs))
    
    for i, (db, p50, p95, jitter) in enumerate(zip(dbs, p50s, p95s, jitters)):
        color = DB_COLORS.get(db, "#475569")
        # Connector line
        ax.plot([p50, p95], [i, i], color=color, linewidth=3, zorder=2, alpha=0.85)
        # p50 hollow marker
        ax.scatter(p50, i, color="#FFFFFF", edgecolors=color, s=120, linewidth=2.5, zorder=3, label="p50 Latency" if i == 0 else "")
        # p95 solid marker
        ax.scatter(p95, i, color=color, edgecolors="#1E293B", s=140, linewidth=1.5, zorder=3, label="p95 Latency" if i == 0 else "")
        # Annotation text
        highlight = " (Tightest Variance)" if i == 0 else ""
        ax.text(p95 + 12, i, f"Δ +{jitter:.1f} ms (p95: {p95:.1f}ms){highlight}", va="center", ha="left", 
                fontsize=9.5, fontweight="bold", color="#1E293B")
        ax.text(p50 - 12, i, f"{p50:.1f}ms", va="center", ha="right", 
                fontsize=9, color="#64748B", fontfamily="monospace")
        
    ax.set_yticks(y_pos)
    ax.set_yticklabels(dbs, fontsize=11, fontweight="bold", color="#1E293B")
    ax.set_xlabel("Query Latency (ms) — 1-Hop Traversal (Lower is Better & Shorter Line = Higher Stability)", fontsize=11, fontweight="bold", color="#0F172A", labelpad=10)
    ax.set_title("Tail Latency Predictability: 1-Hop Traversal (p50 vs p95 Jitter across 100 Runs)\nShorter Bar = Predictable Production SLA", 
                 fontsize=13, fontweight="bold", color="#0F172A", pad=15)
    
    min_x = max(0, min(p50s) - 60)
    max_x = max(p95s) + 180
    ax.set_xlim(min_x, max_x)
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    ax.legend(loc="lower right", frameon=True, facecolor="#FFFFFF", edgecolor="#E2E8F0")
    
    plt.tight_layout()
    plt.savefig(output_dir / "jitter_tail_latency_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✓ Saved {output_dir}/jitter_tail_latency_comparison.png")


def generate_speedup_chart(data, output_dir: Path = DEFAULT_ASSETS_DIR):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor="#F8FAFC")
    ax.set_facecolor("#FFFFFF")
    
    dbs = []
    speedups = []
    qps_40 = []
    
    for db_name, profile in data.items():
        c_stats = profile.get("concurrency", {})
        c1 = c_stats.get("concurrency_1_clients", {}).get("qps", 1.0)
        c40 = c_stats.get("concurrency_40_clients", {}).get("qps", 1.0)
        
        factor = c40 / c1 if c1 > 0 else 1.0
        dbs.append(db_name)
        speedups.append(factor)
        qps_40.append(c40)
        
    if not dbs:
        return
        
    # Sort descending by speedup
    sorted_indices = np.argsort(speedups)[::-1]
    dbs = [dbs[i] for i in sorted_indices]
    speedups = [speedups[i] for i in sorted_indices]
    qps_40 = [qps_40[i] for i in sorted_indices]
    
    colors = [DB_COLORS.get(db, "#475569") for db in dbs]
    y_pos = np.arange(len(dbs))
    
    bars = ax.barh(y_pos, speedups, color=colors, height=0.55, edgecolor="#1E293B", linewidth=0.8, alpha=0.9)
    
    for i, (bar, speedup, qps) in enumerate(zip(bars, speedups, qps_40)):
        ax.text(speedup + 0.6, bar.get_y() + bar.get_height()/2, 
                f"{speedup:.1f}x Scalability Multiple (40 Clients: {qps:.1f} QPS)", 
                va="center", ha="left", fontsize=9.5, fontweight="bold", color="#0F172A")
        
    ax.set_yticks(y_pos)
    ax.set_yticklabels(dbs, fontsize=11, fontweight="bold", color="#1E293B")
    ax.set_xlabel("Concurrency Scalability Multiple (40 Workers QPS ÷ 1 Worker QPS)", fontsize=11, fontweight="bold", color="#0F172A", labelpad=10)
    ax.set_title("Concurrency Speedup Factor: 1 Worker vs 40 Concurrent Workers\n(Higher is Better · 100-Iteration Mixed 80% Read / 20% Write)", 
                 fontsize=13, fontweight="bold", color="#0F172A", pad=15)
    ax.set_xlim(0, max(speedups) * 1.35)
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(output_dir / "concurrency_speedup_factor.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✓ Saved {output_dir}/concurrency_speedup_factor.png")


def generate_quadrant_matrix(output_dir: Path = DEFAULT_ASSETS_DIR):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(10, 8), facecolor="#F8FAFC")
    ax.set_facecolor("#FFFFFF")
    
    # Draw quadrant dividers
    ax.axvline(50, color="#94A3B8", linestyle="--", linewidth=1.2, zorder=1)
    ax.axhline(50, color="#94A3B8", linestyle="--", linewidth=1.2, zorder=1)
    
    # Quadrant Background Tints
    ax.add_patch(patches.Rectangle((50, 50), 50, 50, color="#EB6C36", alpha=0.06, zorder=0)) # Top-right: Native High Scale
    ax.add_patch(patches.Rectangle((0, 50), 50, 50, color="#0284C7", alpha=0.04, zorder=0))  # Top-left: Enterprise Standard
    ax.add_patch(patches.Rectangle((50, 0), 50, 50, color="#10B981", alpha=0.04, zorder=0))  # Bottom-right: In-Memory / Matrix
    ax.add_patch(patches.Rectangle((0, 0), 50, 50, color="#64748B", alpha=0.04, zorder=0))  # Bottom-left: Multi-Model Document
    
    # Quadrant Category Labels
    ax.text(96, 96, "HIGH-CONCURRENCY NATIVE ENGINES\n(Memory-Mapped / GraphBLAS / C++)", 
            ha="right", va="top", fontsize=9.5, fontweight="bold", color="#B45309")
    ax.text(4, 96, "ESTABLISHED ENTERPRISE GRAPH\n(JVM Managed Record Store)", 
            ha="left", va="top", fontsize=9.5, fontweight="bold", color="#0369A1")
    ax.text(4, 4, "MULTI-MODEL ROCKSDB\n(Document + Secondary Index)", 
            ha="left", va="bottom", fontsize=9.5, fontweight="bold", color="#475569")
    ax.text(96, 4, "SPECIALIZED IN-MEMORY GRAPH\n(High Speed Single Node)", 
            ha="right", va="bottom", fontsize=9.5, fontweight="bold", color="#047857")
    
    # Position databases (X: Graph-Native Purity 0-100, Y: Concurrency Scaling & Stability 0-100)
    db_positions = {
        "CognoDB Cloud": (88, 86, "Lock-Free Memory-Mapped\nSub-20ms Jitter · Native Bolt"),
        "FalkorDB Cloud": (92, 92, "GraphBLAS Sparse Matrix\n59.2 QPS @ 40 Clients"),
        "Memgraph Cloud": (82, 78, "In-Memory C++ Pointers\nHigh Speed Multi-Hop"),
        "Neo4j AuraDB": (40, 72, "JVM LPG Record Store\nMature Ecosystem · GC Jitter"),
        "ArangoDB Oasis": (24, 38, "Multi-Model RocksDB\nFast Document · Contention @ 40x")
    }
    
    for db, (x, y, desc) in db_positions.items():
        color = DB_COLORS.get(db, "#475569")
        ax.scatter(x, y, color=color, edgecolors="#0F172A", s=220, linewidth=1.8, zorder=4)
        
        # Label offset
        offset_y = 4.2 if y < 85 else -5.5
        offset_x = 0
        if "FalkorDB" in db:
            offset_y = 4.5
        elif "Memgraph" in db:
            offset_y = -6.0
        elif "CognoDB" in db:
            offset_y = 5.2
            
        ax.text(x + offset_x, y + offset_y, f"{db}\n{desc}", 
                ha="center", va="center", fontsize=9, fontweight="bold", color="#0F172A",
                bbox=dict(boxstyle="round,pad=0.35", facecolor="#FFFFFF", edgecolor=color, alpha=0.95), zorder=5)
        
    ax.set_xlabel("← Relational / Document Engine Store       |       Native Graph Pointers & GraphBLAS Linear Algebra →", 
                  fontsize=11, fontweight="bold", color="#0F172A", labelpad=12)
    ax.set_ylabel("← Low Multi-Hop Concurrency Scalability       |       High Concurrency & Low Tail-Latency Jitter →", 
                  fontsize=11, fontweight="bold", color="#0F172A", labelpad=12)
    ax.set_title("Strategic Graph Database Positioning Quadrant (2026 Cloud Ecosystem)\nTraversal Engine Architecture vs Concurrency Resilience", 
                 fontsize=13, fontweight="bold", color="#0F172A", pad=15)
    
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], color="#64748B")
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"], color="#64748B")
    
    plt.tight_layout()
    plt.savefig(output_dir / "architectural_tradeoff_quadrant.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✓ Saved {output_dir}/architectural_tradeoff_quadrant.png")


def generate_all_metric_diagrams(data_or_path, output_dir: Path = DEFAULT_ASSETS_DIR):
    """Generate all 4 advanced diagrams from a dict or JSON file path."""
    if isinstance(data_or_path, (str, Path)):
        data = load_data(data_or_path)
    else:
        data = data_or_path
        
    out = Path(output_dir)
    generate_radar_chart(data, output_dir=out)
    generate_jitter_dumbbell_chart(data, output_dir=out)
    generate_speedup_chart(data, output_dir=out)
    generate_quadrant_matrix(output_dir=out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate advanced metric comparison diagrams")
    parser.add_argument("--results-file", type=str, default=str(DEFAULT_RESULTS_FILE), help="Path to benchmark_results.json")
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_ASSETS_DIR), help="Directory to save PNG diagrams")
    args = parser.parse_args()
    
    data = load_data(Path(args.results_file))
    generate_all_metric_diagrams(data, output_dir=Path(args.output_dir))
    print(f"✓ All 4 Advanced Metric Comparison Diagrams Generated Successfully into {args.output_dir}!")
