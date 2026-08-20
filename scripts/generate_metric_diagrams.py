"""
Generate Advanced Metric Comparison Diagrams for All Databases.
Generates:
1. radar_performance_profile.png (5-Axis Multi-Dimensional Radar Chart)
2. jitter_tail_latency_comparison.png (p50 vs p95 Latency Stability & Jitter)
3. concurrency_speedup_factor.png (Concurrency Scaling Efficiency Multiple)
4. architectural_tradeoff_quadrant.png (2x2 Strategic Engine Positioning Matrix)
"""

import sys
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

DB_COLORS = {
    "CognoDB Cloud": "#EB6C36",    # Coral/Tangerine
    "Neo4j AuraDB": "#0284C7",     # Sky Blue
    "Memgraph Cloud": "#10B981",   # Emerald Green
    "FalkorDB Cloud": "#8B5CF6",   # Purple
    "ArangoDB Oasis": "#F59E0B"    # Amber
}

def generate_radar_chart():
    categories = [
        "Ingestion\nThroughput",
        "Traversal\nLatency (1-3 Hop)",
        "Tail Latency\nStability (p95/p50)",
        "Concurrency\nScaling (40x)",
        "Memory-Mapped\nEfficiency"
    ]
    N = len(categories)
    
    # Normalized scores out of 100
    scores = {
        "CognoDB Cloud": [75, 82, 98, 85, 95],
        "Neo4j AuraDB":  [78, 80, 52, 80, 68],
        "Memgraph Cloud": [90, 94, 78, 88, 70],
        "FalkorDB Cloud": [95, 90, 85, 98, 82],
        "ArangoDB Oasis": [55, 84, 82, 45, 60],
    }
    
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
        color = DB_COLORS[db_name]
        linewidth = 2.8 if "CognoDB" in db_name else 1.8
        alpha = 0.22 if "CognoDB" in db_name else 0.08
        ax.plot(angles, vals, linewidth=linewidth, linestyle="solid", label=db_name, color=color)
        ax.fill(angles, vals, color=color, alpha=alpha)
        
    plt.title("Multi-Dimensional Engine Performance Profile\n(Normalized 0-100 Score Across 5 Cloud Dimensions)", 
              size=14, weight="bold", color="#0F172A", pad=28)
    plt.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), frameon=True, facecolor="#FFFFFF", edgecolor="#E2E8F0")
    plt.tight_layout()
    plt.savefig("d:/Projects/WEXA/assets/radar_performance_profile.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("✓ Saved assets/radar_performance_profile.png")


def generate_jitter_dumbbell_chart():
    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor="#F8FAFC")
    ax.set_facecolor("#FFFFFF")
    
    dbs = ["CognoDB Cloud", "Memgraph Cloud", "FalkorDB Cloud", "ArangoDB Oasis", "Neo4j AuraDB"]
    p50s = [289.85, 225.26, 222.46, 249.44, 277.10]
    p95s = [308.43, 384.15, 389.10, 381.01, 897.83]
    jitters = [p95 - p50 for p50, p95 in zip(p50s, p95s)]
    
    y_pos = np.arange(len(dbs))
    
    for i, (db, p50, p95, jitter) in enumerate(zip(dbs, p50s, p95s, jitters)):
        color = DB_COLORS[db]
        # Connector line
        ax.plot([p50, p95], [i, i], color=color, linewidth=3, zorder=2, alpha=0.8)
        # p50 hollow marker
        ax.scatter(p50, i, color="#FFFFFF", edgecolors=color, s=120, linewidth=2.5, zorder=3, label="p50 Latency" if i == 0 else "")
        # p95 solid marker
        ax.scatter(p95, i, color=color, edgecolors="#1E293B", s=140, linewidth=1.5, zorder=3, label="p95 Latency" if i == 0 else "")
        # Annotation text
        ax.text(p95 + 18, i, f"Δ +{jitter:.1f} ms (p95: {p95:.1f}ms)", va="center", ha="left", 
                fontsize=9.5, fontweight="bold", color="#1E293B")
        ax.text(p50 - 18, i, f"{p50:.1f}ms", va="center", ha="right", 
                fontsize=9, color="#64748B", fontfamily="monospace")
        
    ax.set_yticks(y_pos)
    ax.set_yticklabels(dbs, fontsize=11, fontweight="bold", color="#1E293B")
    ax.set_xlabel("Query Latency (ms) — 1-Hop Traversal (Lower is Better & Shorter Gap = Higher Stability)", fontsize=11, fontweight="bold", color="#0F172A", labelpad=10)
    ax.set_title("Tail Latency Predictability: 1-Hop Traversal (p50 vs p95 Jitter)\nCognoDB Exhibits Tightest Variance (<19ms delta)", 
                 fontsize=13, fontweight="bold", color="#0F172A", pad=15)
    ax.set_xlim(120, 1080)
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    ax.legend(loc="lower right", frameon=True, facecolor="#FFFFFF", edgecolor="#E2E8F0")
    
    plt.tight_layout()
    plt.savefig("d:/Projects/WEXA/assets/jitter_tail_latency_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("✓ Saved assets/jitter_tail_latency_comparison.png")


def generate_speedup_chart():
    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor="#F8FAFC")
    ax.set_facecolor("#FFFFFF")
    
    dbs = ["FalkorDB Cloud", "Memgraph Cloud", "CognoDB Cloud", "Neo4j AuraDB", "ArangoDB Oasis"]
    speedups = [45.5, 37.0, 36.7, 35.5, 7.2]
    qps_40 = [59.21, 32.52, 28.28, 28.79, 26.12]
    
    colors = [DB_COLORS[db] for db in dbs]
    y_pos = np.arange(len(dbs))
    
    bars = ax.barh(y_pos, speedups, color=colors, height=0.55, edgecolor="#1E293B", linewidth=0.8, alpha=0.9)
    
    for i, (bar, speedup, qps) in enumerate(zip(bars, speedups, qps_40)):
        ax.text(speedup + 0.8, bar.get_y() + bar.get_height()/2, 
                f"{speedup:.1f}x Scalability Multiple (40 Clients: {qps:.1f} QPS)", 
                va="center", ha="left", fontsize=9.5, fontweight="bold", color="#0F172A")
        
    ax.set_yticks(y_pos)
    ax.set_yticklabels(dbs, fontsize=11, fontweight="bold", color="#1E293B")
    ax.set_xlabel("Concurrency Scalability Multiple (40 Workers QPS ÷ 1 Worker QPS)", fontsize=11, fontweight="bold", color="#0F172A", labelpad=10)
    ax.set_title("Concurrency Speedup Factor: 1 Worker vs 40 Concurrent Workers\n(Higher is Better · Mixed 80% Read / 20% Write Load)", 
                 fontsize=13, fontweight="bold", color="#0F172A", pad=15)
    ax.set_xlim(0, 55)
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    
    plt.tight_layout()
    plt.savefig("d:/Projects/WEXA/assets/concurrency_speedup_factor.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("✓ Saved assets/concurrency_speedup_factor.png")


def generate_quadrant_matrix():
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
        color = DB_COLORS[db]
        size = 280 if "CognoDB" in db else 200
        ax.scatter(x, y, color=color, edgecolors="#0F172A", s=size, linewidth=1.8, zorder=4)
        
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
    plt.savefig("d:/Projects/WEXA/assets/architectural_tradeoff_quadrant.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("✓ Saved assets/architectural_tradeoff_quadrant.png")


if __name__ == "__main__":
    generate_radar_chart()
    generate_jitter_dumbbell_chart()
    generate_speedup_chart()
    generate_quadrant_matrix()
    print("✓ All 4 Advanced Metric Comparison Diagrams Generated Successfully!")
