"""
Master Diagram and Benchmark Report Generator.
Merges Cloud Run CognoDB baseline into Local Run telemetry and generates
publication-grade visual diagrams and interactive HTML dashboards.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set dark editorial styling for publication-grade graphs
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8

PALETTE = {
    "CognoDB Cloud": "#6366F1",       # Indigo (Cloud Baseline)
    "Neo4j AuraDB": "#008CC1",        # Neo4j Cyan
    "Memgraph Cloud": "#F97316",      # Orange
    "FalkorDB Cloud": "#EF4444",      # Red
    "ArangoDB Oasis": "#10B981",      # Emerald
    "KùzuDB": "#EC4899",              # Pink
    "JanusGraph": "#8B5CF6",          # Purple
    "ArcadeDB": "#EAB308"             # Yellow/Gold
}

def clean_key_name(k: str) -> str:
    if "kuzu" in k.lower() or "kzu" in k.lower() or "k\ufffdzu" in k.lower():
        return "KùzuDB"
    return k

class MasterReportGenerator:
    def __init__(self, data: Dict[str, Any], output_dir: Path, title_suffix: str = ""):
        self.raw_data = data
        # Clean keys
        self.data = {clean_key_name(k): v for k, v in data.items()}
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.title_suffix = title_suffix
        self.db_names = list(self.data.keys())

    def generate_all(self):
        self.plot_ingest_throughput()
        self.plot_traversal_latencies()
        self.plot_concurrency_qps()
        self.plot_concurrency_p95()
        self.plot_concurrency_speedup()
        self.plot_cold_vs_warm()
        self.plot_radar_profile()
        self.plot_tail_jitter()
        self.plot_architectural_quadrant()
        self.plot_comprehensive_matrix()
        self.generate_summary_markdown()

    def plot_ingest_throughput(self):
        fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
        x = np.arange(len(self.db_names))
        width = 0.38
        
        node_tps = [self.data[db].get("ingest", {}).get("nodes_per_sec", 0) for db in self.db_names]
        edge_tps = [self.data[db].get("ingest", {}).get("edges_per_sec", 0) for db in self.db_names]
        
        r1 = ax.bar(x - width/2, node_tps, width, label='Node Ingestion (nodes/s)', color='#4F46E5', alpha=0.9)
        r2 = ax.bar(x + width/2, edge_tps, width, label='Edge Ingestion (rels/s)', color='#06B6D4', alpha=0.9)
        
        ax.set_title(f'Bulk Ingestion Throughput {self.title_suffix}', fontsize=14, fontweight='bold', pad=15)
        ax.set_ylabel('Throughput (Records / sec)', fontsize=11, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(self.db_names, fontsize=10, fontweight='bold', rotation=15, ha='right')
        ax.legend(frameon=True, facecolor='white', framealpha=0.9)
        
        for r in [r1, r2]:
            for bar in r:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'{int(height):,}',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3), textcoords="offset points",
                                ha='center', va='bottom', fontsize=8, fontweight='bold')
                                
        plt.tight_layout()
        fig.savefig(self.output_dir / "ingestion_throughput.png")
        plt.close(fig)

    def plot_traversal_latencies(self):
        fig, ax = plt.subplots(figsize=(13, 6), dpi=300)
        x = np.arange(len(self.db_names))
        width = 0.25
        
        hop1 = [self.data[db].get("queries", {}).get("traversal_1_hop", {}).get("p50_ms", 0) for db in self.db_names]
        hop2 = [self.data[db].get("queries", {}).get("traversal_2_hop", {}).get("p50_ms", 0) for db in self.db_names]
        hop3 = [self.data[db].get("queries", {}).get("traversal_3_hop", {}).get("p50_ms", 0) for db in self.db_names]
        
        r1 = ax.bar(x - width, hop1, width, label='1-Hop Traversal (p50)', color='#10B981', alpha=0.9)
        r2 = ax.bar(x, hop2, width, label='2-Hop Traversal (p50)', color='#F59E0B', alpha=0.9)
        r3 = ax.bar(x + width, hop3, width, label='3-Hop Traversal (p50)', color='#EF4444', alpha=0.9)
        
        ax.set_title(f'Multi-Hop Traversal Latency (p50 ms - Lower is Better) {self.title_suffix}', fontsize=14, fontweight='bold', pad=15)
        ax.set_ylabel('Latency (Milliseconds)', fontsize=11, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(self.db_names, fontsize=10, fontweight='bold', rotation=15, ha='right')
        ax.legend(frameon=True, facecolor='white', framealpha=0.9)
        
        for r in [r1, r2, r3]:
            for bar in r:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'{height:.1f}ms',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3), textcoords="offset points",
                                ha='center', va='bottom', fontsize=8, fontweight='bold')
                                
        plt.tight_layout()
        fig.savefig(self.output_dir / "traversal_latency_comparison.png")
        plt.close(fig)

    def plot_concurrency_qps(self):
        fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
        clients = [1, 10, 40]
        
        for db in self.db_names:
            concur = self.data[db].get("concurrency", {})
            qps_vals = [
                concur.get("concurrency_1_clients", {}).get("qps", 0),
                concur.get("concurrency_10_clients", {}).get("qps", 0),
                concur.get("concurrency_40_clients", {}).get("qps", 0)
            ]
            ax.plot(clients, qps_vals, marker='o', linewidth=2.5, label=db, color=PALETTE.get(db, '#333333'))
            
        ax.set_title(f'Concurrency Scaling: Sustained Mixed Workload QPS (80% R / 20% W) {self.title_suffix}', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Concurrent Clients', fontsize=11, fontweight='bold')
        ax.set_ylabel('Throughput (Queries / sec)', fontsize=11, fontweight='bold')
        ax.set_xticks(clients)
        ax.legend(frameon=True, facecolor='white', framealpha=0.9)
        
        plt.tight_layout()
        fig.savefig(self.output_dir / "concurrency_scaling_qps.png")
        plt.close(fig)

    def plot_concurrency_p95(self):
        fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
        clients = [1, 10, 40]
        
        for db in self.db_names:
            concur = self.data[db].get("concurrency", {})
            p95_vals = [
                concur.get("concurrency_1_clients", {}).get("p95_ms", 0),
                concur.get("concurrency_10_clients", {}).get("p95_ms", 0),
                concur.get("concurrency_40_clients", {}).get("p95_ms", 0)
            ]
            ax.plot(clients, p95_vals, marker='s', linestyle='--', linewidth=2, label=db, color=PALETTE.get(db, '#333333'))
            
        ax.set_title(f'Tail Latency Degradation Under Load (p95 ms - Lower is Better) {self.title_suffix}', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Concurrent Clients', fontsize=11, fontweight='bold')
        ax.set_ylabel('p95 Latency (Milliseconds)', fontsize=11, fontweight='bold')
        ax.set_xticks(clients)
        ax.legend(frameon=True, facecolor='white', framealpha=0.9)
        
        plt.tight_layout()
        fig.savefig(self.output_dir / "concurrency_p95_latency.png")
        plt.close(fig)

    def plot_concurrency_speedup(self):
        fig, ax = plt.subplots(figsize=(12, 5), dpi=300)
        factors = []
        for db in self.db_names:
            concur = self.data[db].get("concurrency", {})
            q1 = concur.get("concurrency_1_clients", {}).get("qps", 1e-6)
            q40 = concur.get("concurrency_40_clients", {}).get("qps", 0)
            factors.append(round(q40 / q1, 2) if q1 > 0 else 0)
            
        colors = [PALETTE.get(db, '#4F46E5') for db in self.db_names]
        bars = ax.bar(self.db_names, factors, color=colors, alpha=0.85, edgecolor='#333333')
        
        ax.set_title(f'Concurrency Scalability Factor (40 Workers QPS / 1 Worker QPS) {self.title_suffix}', fontsize=14, fontweight='bold', pad=15)
        ax.set_ylabel('Scaling Multiplier (Higher is Better)', fontsize=11, fontweight='bold')
        ax.set_xticklabels(self.db_names, fontsize=10, fontweight='bold', rotation=15, ha='right')
        
        for bar in bars:
            h = bar.get_height()
            ax.annotate(f'{h:.1f}x',
                        xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')
                        
        plt.tight_layout()
        fig.savefig(self.output_dir / "concurrency_speedup_factor.png")
        plt.close(fig)

    def plot_cold_vs_warm(self):
        fig, ax = plt.subplots(figsize=(12, 5), dpi=300)
        x = np.arange(len(self.db_names))
        width = 0.35
        
        cold_lats = [self.data[db].get("queries", {}).get("point_lookup", {}).get("cold_ms", 0) for db in self.db_names]
        warm_p50 = [self.data[db].get("queries", {}).get("point_lookup", {}).get("p50_ms", 0) for db in self.db_names]
        
        r1 = ax.bar(x - width/2, cold_lats, width, label='Cold Latency (ms)', color='#64748B', alpha=0.85)
        r2 = ax.bar(x + width/2, warm_p50, width, label='Warm p50 Latency (ms)', color='#3B82F6', alpha=0.85)
        
        ax.set_title(f'Cold Start vs. Warm Cache Latency (Point Lookup) {self.title_suffix}', fontsize=14, fontweight='bold', pad=15)
        ax.set_ylabel('Latency (Milliseconds)', fontsize=11, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(self.db_names, fontsize=10, fontweight='bold', rotation=15, ha='right')
        ax.legend(frameon=True, facecolor='white', framealpha=0.9)
        
        plt.tight_layout()
        fig.savefig(self.output_dir / "cold_vs_warm_latency.png")
        plt.close(fig)

    def plot_radar_profile(self):
        categories = ['Ingest Throughput', 'Lookup Latency', '1-Hop Traversal', '3-Hop Traversal', 'Concurrency QPS', 'Scalability Factor']
        N = len(categories)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True), dpi=300)
        plt.xticks(angles[:-1], categories, color='black', size=9, fontweight='bold')
        
        for db in self.db_names:
            db_data = self.data[db]
            ingest_s = min(10, (db_data.get("ingest", {}).get("nodes_per_sec", 0) / 4000) * 2)
            lookup_s = max(1, min(10, 10 - (db_data.get("queries", {}).get("point_lookup", {}).get("p50_ms", 100) / 30)))
            hop1_s = max(1, min(10, 10 - (db_data.get("queries", {}).get("traversal_1_hop", {}).get("p50_ms", 100) / 30)))
            hop3_s = max(1, min(10, 10 - (db_data.get("queries", {}).get("traversal_3_hop", {}).get("p50_ms", 100) / 30)))
            qps_s = min(10, max(1, (db_data.get("concurrency", {}).get("concurrency_40_clients", {}).get("qps", 0) / 80)))
            scale_s = min(10, max(1, (db_data.get("concurrency", {}).get("concurrency_40_clients", {}).get("qps", 1) / max(0.1, db_data.get("concurrency", {}).get("concurrency_1_clients", {}).get("qps", 1))) / 2))
            
            values = [ingest_s, lookup_s, hop1_s, hop3_s, qps_s, scale_s]
            values += values[:1]
            
            color = PALETTE.get(db, '#333333')
            ax.plot(angles, values, linewidth=2, linestyle='solid', label=db, color=color)
            ax.fill(angles, values, color=color, alpha=0.1)
            
        ax.set_title(f'Holistic Multi-Dimensional Radar Performance Profile {self.title_suffix}', size=13, fontweight='bold', pad=25)
        ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.15), fontsize=8)
        
        plt.tight_layout()
        fig.savefig(self.output_dir / "radar_performance_profile.png")
        plt.close(fig)

    def plot_tail_jitter(self):
        fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
        x = np.arange(len(self.db_names))
        width = 0.25
        
        p50 = [self.data[db].get("queries", {}).get("traversal_2_hop", {}).get("p50_ms", 0) for db in self.db_names]
        p95 = [self.data[db].get("queries", {}).get("traversal_2_hop", {}).get("p95_ms", 0) for db in self.db_names]
        p99 = [self.data[db].get("queries", {}).get("traversal_2_hop", {}).get("p99_ms", 0) for db in self.db_names]
        
        r1 = ax.bar(x - width, p50, width, label='p50 Latency', color='#3B82F6', alpha=0.85)
        r2 = ax.bar(x, p95, width, label='p95 Tail Latency', color='#F59E0B', alpha=0.85)
        r3 = ax.bar(x + width, p99, width, label='p99 Max Jitter', color='#EF4444', alpha=0.85)
        
        ax.set_title(f'Latency Tail Jitter & Variance (2-Hop Traversal) {self.title_suffix}', fontsize=14, fontweight='bold', pad=15)
        ax.set_ylabel('Latency (Milliseconds)', fontsize=11, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(self.db_names, fontsize=10, fontweight='bold', rotation=15, ha='right')
        ax.legend(frameon=True, facecolor='white', framealpha=0.9)
        
        plt.tight_layout()
        fig.savefig(self.output_dir / "jitter_tail_latency_comparison.png")
        plt.close(fig)

    def plot_architectural_quadrant(self):
        fig, ax = plt.subplots(figsize=(11, 8), dpi=300)
        
        for db in self.db_names:
            db_data = self.data[db]
            lat = db_data.get("queries", {}).get("traversal_1_hop", {}).get("p50_ms", 50)
            qps = db_data.get("concurrency", {}).get("concurrency_40_clients", {}).get("qps", 50)
            ingest = db_data.get("ingest", {}).get("nodes_per_sec", 1000)
            size = max(120, min(1400, ingest / 25))
            
            color = PALETTE.get(db, '#333333')
            ax.scatter(lat, qps, s=size, color=color, alpha=0.75, edgecolors='black', linewidth=1.5, label=db)
            ax.annotate(db, (lat, qps), xytext=(8, 5), textcoords='offset points', fontsize=9, fontweight='bold')
            
        ax.set_title(f'Architectural Tradeoff Quadrant (Bubble Size = Ingest Throughput) {self.title_suffix}', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('1-Hop Traversal Latency (p50 ms - Lower is Better)', fontsize=11, fontweight='bold')
        ax.set_ylabel('40-Worker Sustained QPS (Higher is Better)', fontsize=11, fontweight='bold')
        ax.axvline(x=50, color='gray', linestyle='--', alpha=0.5)
        ax.axhline(y=150, color='gray', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        fig.savefig(self.output_dir / "architectural_tradeoff_quadrant.png")
        plt.close(fig)

    def plot_comprehensive_matrix(self):
        fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
        metrics = ['Ingest (n/s)', 'Ingest (e/s)', 'Point Lookup (p50)', '1-Hop (p50)', '3-Hop (p50)', 'Degree Agg (p50)', '40-Worker QPS']
        
        matrix = []
        for db in self.db_names:
            db_data = self.data[db]
            row = [
                db_data.get("ingest", {}).get("nodes_per_sec", 0),
                db_data.get("ingest", {}).get("edges_per_sec", 0),
                db_data.get("queries", {}).get("point_lookup", {}).get("p50_ms", 0),
                db_data.get("queries", {}).get("traversal_1_hop", {}).get("p50_ms", 0),
                db_data.get("queries", {}).get("traversal_3_hop", {}).get("p50_ms", 0),
                db_data.get("queries", {}).get("aggregation", {}).get("p50_ms", 0),
                db_data.get("concurrency", {}).get("concurrency_40_clients", {}).get("qps", 0)
            ]
            matrix.append(row)
            
        matrix_np = np.array(matrix, dtype=float)
        norm_matrix = np.zeros_like(matrix_np)
        for col in range(matrix_np.shape[1]):
            col_vals = matrix_np[:, col]
            if col in [2, 3, 4, 5]:
                norm_matrix[:, col] = 1 - (col_vals - np.min(col_vals)) / (np.max(col_vals) - np.min(col_vals) + 1e-6)
            else:
                norm_matrix[:, col] = (col_vals - np.min(col_vals)) / (np.max(col_vals) - np.min(col_vals) + 1e-6)
                
        sns.heatmap(norm_matrix, annot=matrix_np, fmt='.1f', cmap='YlGnBu', xticklabels=metrics, yticklabels=self.db_names, ax=ax, cbar=False)
        ax.set_title(f'Comprehensive Benchmark Workload Matrix {self.title_suffix}', fontsize=14, fontweight='bold', pad=15)
        
        plt.tight_layout()
        fig.savefig(self.output_dir / "comprehensive_benchmark_matrix.png")
        plt.close(fig)

    def generate_summary_markdown(self):
        lines = []
        lines.append("### 📊 Ingestion & Indexing Performance\n")
        lines.append("| Database | Paradigm | Index Build (ms) | Node Ingest (n/s) | Edge Ingest (e/s) | Wall-Clock (s) |")
        lines.append("|:---|:---|:---:|:---:|:---:|:---:|")
        for db in self.db_names:
            d = self.data[db]
            paradigm = d.get("paradigm", "Graph Database")
            ib = f"{d.get('ingest', {}).get('index_build_time_ms', 0):.2f} ms"
            ni = f"{d.get('ingest', {}).get('nodes_per_sec', 0):,.1f}"
            ei = f"{d.get('ingest', {}).get('edges_per_sec', 0):,.1f}"
            wc = f"{d.get('ingest', {}).get('total_ingest_wall_clock_sec', 0):.2f}s"
            lines.append(f"| **{db}** | {paradigm} | {ib} | {ni} | {ei} | {wc} |")
            
        lines.append("\n### ⚡ Query Latency Profile (Percentiles in Milliseconds)\n")
        lines.append("| Database | Point Lookup (p50 / p95) | 1-Hop Traversal (p50 / p95) | 2-Hop Traversal (p50 / p95) | 3-Hop Traversal (p50 / p95) | Degree Aggregation (p50) |")
        lines.append("|:---|:---:|:---:|:---:|:---:|:---:|")
        for db in self.db_names:
            d = self.data[db].get("queries", {})
            p_lk = f"{d.get('point_lookup', {}).get('p50_ms', 0)} / {d.get('point_lookup', {}).get('p95_ms', 0)}"
            h1 = f"{d.get('traversal_1_hop', {}).get('p50_ms', 0)} / {d.get('traversal_1_hop', {}).get('p95_ms', 0)}"
            h2 = f"{d.get('traversal_2_hop', {}).get('p50_ms', 0)} / {d.get('traversal_2_hop', {}).get('p95_ms', 0)}"
            h3 = f"{d.get('traversal_3_hop', {}).get('p50_ms', 0)} / {d.get('traversal_3_hop', {}).get('p95_ms', 0)}"
            deg = f"{d.get('aggregation', {}).get('p50_ms', 0):.2f} ms"
            lines.append(f"| **{db}** | {p_lk} | {h1} | {h2} | {h3} | {deg} |")
            
        lines.append("\n### 📈 Concurrency & Scalability Matrix (Mixed 80% Read / 20% Write)\n")
        lines.append("| Database | 1 Client (QPS / p95) | 10 Clients (QPS / p95) | 40 Clients (QPS / p95) | Scalability Factor (40x / 1x) |")
        lines.append("|:---|:---:|:---:|:---:|:---:|")
        for db in self.db_names:
            c = self.data[db].get("concurrency", {})
            c1 = f"{c.get('concurrency_1_clients', {}).get('qps', 0)} QPS ({c.get('concurrency_1_clients', {}).get('p95_ms', 0)}ms)"
            c10 = f"{c.get('concurrency_10_clients', {}).get('qps', 0)} QPS ({c.get('concurrency_10_clients', {}).get('p95_ms', 0)}ms)"
            c40 = f"{c.get('concurrency_40_clients', {}).get('qps', 0)} QPS ({c.get('concurrency_40_clients', {}).get('p95_ms', 0)}ms)"
            q1 = c.get('concurrency_1_clients', {}).get('qps', 1e-6)
            q40 = c.get('concurrency_40_clients', {}).get('qps', 0)
            fac = f"**{q40 / q1:.1f}x**" if q1 > 0 else "**N/A**"
            lines.append(f"| **{db}** | {c1} | {c10} | {c40} | {fac} |")
            
        lines.append("\n### 🌐 Network RTT vs Server-Side Net Compute Time (p50)\n")
        lines.append("| Database | Baseline Network RTT | 1-Hop p50 (Gross) | 1-Hop Net Compute | 2-Hop Net Compute | 3-Hop Net Compute |")
        lines.append("|:---|:---:|:---:|:---:|:---:|:---:|")
        for db in self.db_names:
            d = self.data[db]
            rtt = f"{d.get('baseline_rtt_ms', 0):.2f} ms"
            h1 = f"{d.get('queries', {}).get('traversal_1_hop', {}).get('p50_ms', 0):.2f} ms"
            n1 = f"**{d.get('net_compute', {}).get('1_hop_net_ms', 0):.2f} ms**"
            n2 = f"**{d.get('net_compute', {}).get('2_hop_net_ms', 0):.2f} ms**"
            n3 = f"**{d.get('net_compute', {}).get('3_hop_net_ms', 0):.2f} ms**"
            lines.append(f"| **{db}** | {rtt} | {h1} | {n1} | {n2} | {n3} |")
            
        md_text = "\n".join(lines)
        with open(self.output_dir / "summary_tables.md", "w", encoding="utf-8") as f:
            f.write(md_text)


def run():
    print("Loading CloudRun and LocalRun datasets...")
    with open("CloudRun/benchmark_results.json", "r", encoding="utf-8") as f:
        cloud_raw = json.load(f)
        
    with open("Local Run/benchmark_results.json", "r", encoding="utf-8") as f:
        local_raw = json.load(f)
        
    local_clean = {}
    
    # Insert CognoDB Cloud into Local Run (as explicitly directed: 'use the cloud run numbers for the cognoDB in the local run report')
    if "CognoDB Cloud" in cloud_raw:
        local_clean["CognoDB Cloud"] = cloud_raw["CognoDB Cloud"]
    elif "cognoDB" in cloud_raw:
        local_clean["CognoDB Cloud"] = cloud_raw["cognoDB"]
        
    for k, v in local_raw.items():
        k_clean = clean_key_name(k)
        if k_clean != "CognoDB Cloud":
            local_clean[k_clean] = v
            
    with open("Local Run/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(local_clean, f, indent=2)
    with open("LocalRun/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(local_clean, f, indent=2)
    with open("results/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(local_clean, f, indent=2)
        
    print(f"Merged Local Run contains {len(local_clean)} databases: {list(local_clean.keys())}")
    
    print("Generating visual diagrams for Local Run (8 Databases)...")
    gen_local = MasterReportGenerator(local_clean, Path("Local Run/assets"), title_suffix="(Local 0.50 vCPU / 512MB RAM + CognoDB Cloud)")
    gen_local.generate_all()
    gen_local_root = MasterReportGenerator(local_clean, Path("assets"), title_suffix="(Local Capped Benchmark Suite)")
    gen_local_root.generate_all()
    gen_local_dup = MasterReportGenerator(local_clean, Path("LocalRun/assets"), title_suffix="(Local 0.50 vCPU / 512MB RAM + CognoDB Cloud)")
    gen_local_dup.generate_all()
    
    with open("Local Run/assets/summary_tables.md", "r", encoding="utf-8") as f:
        md_text = f.read()
    with open("Local Run/summary_tables.md", "w", encoding="utf-8") as f:
        f.write(md_text)
    with open("LocalRun/summary_tables.md", "w", encoding="utf-8") as f:
        f.write(md_text)
    with open("results/summary_tables.md", "w", encoding="utf-8") as f:
        f.write(md_text)

    print("Generating visual diagrams for Cloud Run (5 Cloud Databases)...")
    gen_cloud = MasterReportGenerator(cloud_raw, Path("CloudRun/assets"), title_suffix="(Cloud Baseline c0 / Managed Tiers)")
    gen_cloud.generate_all()
    with open("CloudRun/assets/summary_tables.md", "r", encoding="utf-8") as f:
        md_cloud = f.read()
    with open("CloudRun/summary_tables.md", "w", encoding="utf-8") as f:
        f.write(md_cloud)

    print("All diagrams, telemetry JSONs, and summary tables successfully compiled!")

if __name__ == "__main__":
    run()
