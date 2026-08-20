"""
Publication-Grade Visual Report Generator.
Generates publication-quality charts and Markdown summary tables for the benchmark findings.
"""

import os
import json
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
    "CognoDB Cloud": "#6366F1",    # Indigo
    "Neo4j AuraDB": "#008CC1",     # Neo4j Cyan
    "Memgraph Cloud": "#F97316",   # Orange
    "FalkorDB Cloud": "#EF4444",   # Red
    "ArangoDB Oasis": "#10B981"    # Emerald
}

class ReportGenerator:
    """Renders charts and compiles Markdown report tables."""
    
    def __init__(self, results_data: Dict[str, Any], output_dir: Path = Path("d:/Projects/WEXA/assets")):
        self.data = results_data
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.db_names = list(self.data.keys())

    def generate_all_charts(self):
        """Generate all publication-grade benchmark visualization charts."""
        self.plot_ingest_throughput()
        self.plot_traversal_latencies()
        self.plot_concurrency_qps()
        self.plot_concurrency_p95()
        self.plot_cold_vs_warm()
        self.plot_comprehensive_matrix()

    def plot_ingest_throughput(self):
        fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
        x = np.arange(len(self.db_names))
        width = 0.35
        
        node_tps = [self.data[db]["ingest"]["nodes_per_sec"] for db in self.db_names]
        edge_tps = [self.data[db]["ingest"]["edges_per_sec"] for db in self.db_names]
        
        r1 = ax.bar(x - width/2, node_tps, width, label='Node Ingestion (nodes/s)', color='#4F46E5', alpha=0.9)
        r2 = ax.bar(x + width/2, edge_tps, width, label='Edge Ingestion (rels/s)', color='#06B6D4', alpha=0.9)
        
        ax.set_title('Bulk Ingestion Throughput (350K Pokec Dataset)', fontsize=14, fontweight='bold', pad=15)
        ax.set_ylabel('Throughput (Records / sec)', fontsize=11, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(self.db_names, fontsize=10, fontweight='bold')
        ax.legend(frameon=True, facecolor='white', framealpha=0.9)
        
        # Add labels above bars
        for r in [r1, r2]:
            for bar in r:
                height = bar.get_height()
                ax.annotate(f'{int(height):,}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points",
                            ha='center', va='bottom', fontsize=8, fontweight='bold')
                            
        plt.tight_layout()
        chart_path = self.output_dir / "ingestion_throughput.png"
        fig.savefig(chart_path)
        plt.close(fig)

    def plot_traversal_latencies(self):
        fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
        x = np.arange(len(self.db_names))
        width = 0.25
        
        hop1 = [self.data[db]["queries"]["traversal_1_hop"]["p50_ms"] for db in self.db_names]
        hop2 = [self.data[db]["queries"]["traversal_2_hop"]["p50_ms"] for db in self.db_names]
        hop3 = [self.data[db]["queries"]["traversal_3_hop"]["p50_ms"] for db in self.db_names]
        
        r1 = ax.bar(x - width, hop1, width, label='1-Hop Traversal (p50)', color='#10B981', alpha=0.9)
        r2 = ax.bar(x, hop2, width, label='2-Hop Traversal (p50)', color='#F59E0B', alpha=0.9)
        r3 = ax.bar(x + width, hop3, width, label='3-Hop Traversal (p50)', color='#EF4444', alpha=0.9)
        
        ax.set_title('Multi-Hop Traversal Latency (p50 ms - Lower is Better)', fontsize=14, fontweight='bold', pad=15)
        ax.set_ylabel('Latency (Milliseconds)', fontsize=11, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(self.db_names, fontsize=10, fontweight='bold')
        ax.legend(frameon=True, facecolor='white', framealpha=0.9)
        
        for r in [r1, r2, r3]:
            for bar in r:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}ms',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points",
                            ha='center', va='bottom', fontsize=8, fontweight='bold')
                            
        plt.tight_layout()
        fig.savefig(self.output_dir / "traversal_latency_comparison.png")
        plt.close(fig)

    def plot_concurrency_qps(self):
        fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
        clients = [1, 10, 40]
        
        for db in self.db_names:
            qps_vals = [
                self.data[db]["concurrency"]["concurrency_1_clients"]["qps"],
                self.data[db]["concurrency"]["concurrency_10_clients"]["qps"],
                self.data[db]["concurrency"]["concurrency_40_clients"]["qps"]
            ]
            ax.plot(clients, qps_vals, marker='o', linewidth=2.5, label=db, color=PALETTE.get(db, '#333333'))
            
        ax.set_title('Concurrency Scaling: Sustained Mixed Workload QPS (80% R / 20% W)', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Concurrent Clients', fontsize=11, fontweight='bold')
        ax.set_ylabel('Throughput (Queries / sec)', fontsize=11, fontweight='bold')
        ax.set_xticks(clients)
        ax.legend(frameon=True, facecolor='white', framealpha=0.9)
        
        plt.tight_layout()
        fig.savefig(self.output_dir / "concurrency_scaling_qps.png")
        plt.close(fig)

    def plot_concurrency_p95(self):
        fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
        clients = [1, 10, 40]
        
        for db in self.db_names:
            p95_vals = [
                self.data[db]["concurrency"]["concurrency_1_clients"]["p95_ms"],
                self.data[db]["concurrency"]["concurrency_10_clients"]["p95_ms"],
                self.data[db]["concurrency"]["concurrency_40_clients"]["p95_ms"]
            ]
            ax.plot(clients, p95_vals, marker='s', linestyle='--', linewidth=2, label=db, color=PALETTE.get(db, '#333333'))
            
        ax.set_title('Tail Latency Degradation Under Load (p95 ms - Lower is Better)', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Concurrent Clients', fontsize=11, fontweight='bold')
        ax.set_ylabel('p95 Latency (Milliseconds)', fontsize=11, fontweight='bold')
        ax.set_xticks(clients)
        ax.legend(frameon=True, facecolor='white', framealpha=0.9)
        
        plt.tight_layout()
        fig.savefig(self.output_dir / "concurrency_p95_latency.png")
        plt.close(fig)

    def plot_cold_vs_warm(self):
        fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
        x = np.arange(len(self.db_names))
        width = 0.35
        
        cold_lats = [self.data[db]["queries"]["point_lookup"]["cold_ms"] for db in self.db_names]
        warm_p50 = [self.data[db]["queries"]["point_lookup"]["p50_ms"] for db in self.db_names]
        
        r1 = ax.bar(x - width/2, cold_lats, width, label='Cold Start Query (ms)', color='#3B82F6', alpha=0.9)
        r2 = ax.bar(x + width/2, warm_p50, width, label='Warm State p50 (ms)', color='#10B981', alpha=0.9)
        
        ax.set_title('Cold-Start vs Warm Steady-State Latency (Point Lookups)', fontsize=14, fontweight='bold', pad=15)
        ax.set_ylabel('Latency (ms)', fontsize=11, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(self.db_names, fontsize=10, fontweight='bold')
        ax.legend(frameon=True, facecolor='white', framealpha=0.9)
        
        plt.tight_layout()
        fig.savefig(self.output_dir / "cold_vs_warm_latency.png")
        plt.close(fig)

    def plot_comprehensive_matrix(self):
        """Multi-metric summary matrix bar chart."""
        fig, axs = plt.subplots(2, 2, figsize=(14, 10), dpi=300)
        
        # 1. Ingestion Speed
        ingest_speeds = [self.data[db]["ingest"]["edges_per_sec"] for db in self.db_names]
        colors = [PALETTE.get(db, '#333333') for db in self.db_names]
        axs[0, 0].barh(self.db_names, ingest_speeds, color=colors, alpha=0.85)
        axs[0, 0].set_title('Edge Ingestion Throughput (rels/s)', fontweight='bold')
        
        # 2. 2-Hop Traversal Latency
        hop2_lats = [self.data[db]["queries"]["traversal_2_hop"]["p50_ms"] for db in self.db_names]
        axs[0, 1].barh(self.db_names, hop2_lats, color=colors, alpha=0.85)
        axs[0, 1].set_title('2-Hop Traversal Latency p50 (ms - Lower Better)', fontweight='bold')
        
        # 3. Concurrency 40 QPS
        c40_qps = [self.data[db]["concurrency"]["concurrency_40_clients"]["qps"] for db in self.db_names]
        axs[1, 0].barh(self.db_names, c40_qps, color=colors, alpha=0.85)
        axs[1, 0].set_title('40-Client Concurrency QPS (Higher Better)', fontweight='bold')
        
        # 4. Point Lookup p95 Latency
        pt_p95 = [self.data[db]["queries"]["point_lookup"]["p95_ms"] for db in self.db_names]
        axs[1, 1].barh(self.db_names, pt_p95, color=colors, alpha=0.85)
        axs[1, 1].set_title('Point Lookup p95 Latency (ms - Lower Better)', fontweight='bold')
        
        plt.suptitle('Wexa AI Graph Database Cloud Benchmark: Comprehensive Performance Matrix', fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout()
        fig.savefig(self.output_dir / "comprehensive_benchmark_matrix.png")
        plt.close(fig)

    def generate_markdown_tables(self) -> str:
        """Format results into clean GitHub markdown tables."""
        md = []
        md.append("### 📊 Ingestion & Indexing Performance\n")
        md.append("| Database | Paradigm | Index Build (ms) | Node Ingest (n/s) | Edge Ingest (e/s) | Wall-Clock (s) |")
        md.append("|:---|:---|:---:|:---:|:---:|:---:|")
        for db, res in self.data.items():
            ing = res["ingest"]
            md.append(f"| **{db}** | {res['paradigm']} | {ing['index_build_time_ms']} ms | {ing['nodes_per_sec']:,} | {ing['edges_per_sec']:,} | {ing['total_ingest_wall_clock_sec']}s |")
            
        md.append("\n### ⚡ Query Latency Profile (Percentiles in Milliseconds)\n")
        md.append("| Database | Point Lookup (p50 / p95) | 1-Hop Traversal (p50 / p95) | 2-Hop Traversal (p50 / p95) | 3-Hop Traversal (p50 / p95) | Degree Aggregation (p50) |")
        md.append("|:---|:---:|:---:|:---:|:---:|:---:|")
        for db, res in self.data.items():
            q = res["queries"]
            md.append(f"| **{db}** | {q['point_lookup']['p50_ms']} / {q['point_lookup']['p95_ms']} | {q['traversal_1_hop']['p50_ms']} / {q['traversal_1_hop']['p95_ms']} | {q['traversal_2_hop']['p50_ms']} / {q['traversal_2_hop']['p95_ms']} | {q['traversal_3_hop']['p50_ms']} / {q['traversal_3_hop']['p95_ms']} | {q['aggregation']['p50_ms']} ms |")

        md.append("\n### 📈 Concurrency & Scalability Matrix (Mixed 80% Read / 20% Write)\n")
        md.append("| Database | 1 Client (QPS / p95) | 10 Clients (QPS / p95) | 40 Clients (QPS / p95) | Scalability Factor (40x / 1x) |")
        md.append("|:---|:---:|:---:|:---:|:---:|")
        for db, res in self.data.items():
            c = res["concurrency"]
            qps_1 = c["concurrency_1_clients"]["qps"]
            p95_1 = c["concurrency_1_clients"]["p95_ms"]
            qps_10 = c["concurrency_10_clients"]["qps"]
            p95_10 = c["concurrency_10_clients"]["p95_ms"]
            qps_40 = c["concurrency_40_clients"]["qps"]
            p95_40 = c["concurrency_40_clients"]["p95_ms"]
            scale_fac = round(qps_40 / qps_1, 1) if qps_1 > 0 else 0
            md.append(f"| **{db}** | {qps_1} QPS ({p95_1}ms) | {qps_10} QPS ({p95_10}ms) | {qps_40} QPS ({p95_40}ms) | **{scale_fac}x** |")

        md.append("\n### 🌐 Network RTT vs Server-Side Net Compute Time (p50)\n")
        md.append("| Database | Baseline Network RTT | 1-Hop p50 (Gross) | 1-Hop Net Compute | 2-Hop Net Compute | 3-Hop Net Compute |")
        md.append("|:---|:---:|:---:|:---:|:---:|:---:|")
        for db, res in self.data.items():
            rtt = res.get("baseline_rtt_ms", 0.0)
            q = res["queries"]
            h1 = q.get("traversal_1_hop", {}).get("p50_ms", 0)
            h2 = q.get("traversal_2_hop", {}).get("p50_ms", 0)
            h3 = q.get("traversal_3_hop", {}).get("p50_ms", 0)
            net_h1 = max(0.0, round(h1 - rtt, 2)) if h1 > 0 else 0.0
            net_h2 = max(0.0, round(h2 - rtt, 2)) if h2 > 0 else 0.0
            net_h3 = max(0.0, round(h3 - rtt, 2)) if h3 > 0 else 0.0
            md.append(f"| **{db}** | {rtt:.2f} ms | {h1:.2f} ms | **{net_h1:.2f} ms** | **{net_h2:.2f} ms** | **{net_h3:.2f} ms** |")

        return "\n".join(md)
