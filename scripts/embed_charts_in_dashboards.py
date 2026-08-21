"""
Embeds all benchmark visualization charts directly as base64 data URIs
into all HTML dashboards, making them 100% self-contained.

Enhancements:
- Zoomable lightbox modal for all chart images (click to zoom, Esc/click-overlay to close)
- Best-value highlighting in Detailed Workload Metric Summary Tables
"""

import base64
from pathlib import Path


def get_base64_image(image_path: Path) -> str:
    if not image_path.exists():
        print(f"Warning: Image not found: {image_path}")
        return ""
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def build_self_contained_dashboards():
    local_assets_dir = Path("d:/Projects/WEXA/Local Run/assets")
    cloud_assets_dir = Path("d:/Projects/WEXA/CloudRun/assets")

    local_imgs = {
        "ingest": get_base64_image(local_assets_dir / "ingestion_throughput.png"),
        "traversal": get_base64_image(local_assets_dir / "traversal_latency_comparison.png"),
        "qps": get_base64_image(local_assets_dir / "concurrency_scaling_qps.png"),
        "p95": get_base64_image(local_assets_dir / "concurrency_p95_latency.png"),
        "speedup": get_base64_image(local_assets_dir / "concurrency_speedup_factor.png"),
        "radar": get_base64_image(local_assets_dir / "radar_performance_profile.png"),
        "jitter": get_base64_image(local_assets_dir / "jitter_tail_latency_comparison.png"),
        "cold_warm": get_base64_image(local_assets_dir / "cold_vs_warm_latency.png"),
        "quadrant": get_base64_image(local_assets_dir / "architectural_tradeoff_quadrant.png"),
        "matrix": get_base64_image(local_assets_dir / "comprehensive_benchmark_matrix.png"),
    }

    cloud_imgs = {
        "ingest": get_base64_image(cloud_assets_dir / "ingestion_throughput.png"),
        "traversal": get_base64_image(cloud_assets_dir / "traversal_latency_comparison.png"),
        "qps": get_base64_image(cloud_assets_dir / "concurrency_scaling_qps.png"),
        "p95": get_base64_image(cloud_assets_dir / "concurrency_p95_latency.png"),
        "speedup": get_base64_image(cloud_assets_dir / "concurrency_speedup_factor.png"),
        "radar": get_base64_image(cloud_assets_dir / "radar_performance_profile.png"),
        "jitter": get_base64_image(cloud_assets_dir / "jitter_tail_latency_comparison.png"),
        "cold_warm": get_base64_image(cloud_assets_dir / "cold_vs_warm_latency.png"),
        "quadrant": get_base64_image(cloud_assets_dir / "architectural_tradeoff_quadrant.png"),
        "matrix": get_base64_image(cloud_assets_dir / "comprehensive_benchmark_matrix.png"),
    }

    # ── helper: builds a diagram card with zoom onclick ──
    def card(title, desc, img_data, full=False):
        cls = ' diagram-card-full' if full else ''
        return f"""
        <div class="diagram-card{cls}">
          <div class="diagram-card-header">
            <div class="diagram-title">{title}</div>
            <div class="diagram-desc">{desc}</div>
          </div>
          <div class="diagram-card-body">
            <img src="{img_data}" alt="{title}" class="diagram-img" onclick="openLightbox(this)">
          </div>
        </div>"""

    # ── helper: builds a highlighted table row ──
    # best_cols is a dict: col_index -> 'best' for that row
    # We'll compute best values in JS instead for flexibility

    # ── Local Run table rows ──
    # ── RTT-normalized latency computation ──
    # For fair comparison, subtract baseline network RTT from raw p50 latencies.
    # This isolates actual server-side compute time.
    # Raw values shown in parentheses for transparency.
    #
    # Format: (color, name, paradigm, idx_build, node_ing, edge_ing,
    #          hop1_net, hop3_net, qps, deg_net,
    #          hop1_raw, hop3_raw, deg_raw, rtt)

    local_rows = [
        # CognoDB Cloud: RTT=310.68ms
        # 1-hop raw=310.16 -> net=max(0, 310.16-310.68)=0.00
        # 3-hop raw=306.62 -> net=max(0, 306.62-310.68)=0.00
        # agg raw=1597.83 -> net=max(0, 1597.83-310.68)=1287.15
        ("var(--color-cogno)", "CognoDB Cloud", "Cloud Native Graph (Bolt)",
         "608.41 ms", "1,483.0 n/s", "3,565.6 e/s",
         "0.00 ms", "0.00 ms", "9.11 QPS", "1,287.15 ms",
         "310.16", "306.62", "1,597.83", "310.68"),
        # FalkorDB: RTT=1.69ms
        ("var(--color-falkor)", "FalkorDB", "GraphBLAS Sparse Matrix (C)",
         "3.45 ms", "41,924.5 n/s", "10,190.7 e/s",
         "0.00 ms", "0.00 ms", "766.87 QPS", "295.94 ms",
         "1.09", "1.08", "297.63", "1.69"),
        # Memgraph: RTT=2.12ms
        ("var(--color-memgraph)", "Memgraph", "In-Memory Native Graph (C++)",
         "9.09 ms", "32,261.5 n/s", "37,930.3 e/s",
         "0.00 ms", "0.00 ms", "183.15 QPS", "147.65 ms",
         "1.42", "1.68", "149.77", "2.12"),
        # Neo4j: RTT=6.85ms
        ("var(--color-neo4j)", "Neo4j 5 Community", "JVM Property Graph (LPG)",
         "684.77 ms", "7,541.5 n/s", "9,437.5 e/s",
         "0.00 ms", "0.00 ms", "119.95 QPS", "309.33 ms",
         "3.92", "3.63", "316.18", "6.85"),
        # ArangoDB: RTT=45.94ms
        ("var(--color-arango)", "ArangoDB", "Multi-Model RocksDB (AQL)",
         "94.27 ms", "27,189.0 n/s", "21,465.1 e/s",
         "0.00 ms", "0.00 ms", "463.97 QPS", "121.39 ms",
         "43.71", "43.75", "167.33", "45.94"),
        # JanusGraph: RTT=50.78ms
        ("var(--color-janus)", "JanusGraph", "TinkerPop Gremlin (BerkeleyJE)",
         "88.74 ms", "853.8 n/s", "1,266.3 e/s",
         "4.55 ms", "1.90 ms", "172.86 QPS", "453.61 ms",
         "55.33", "52.68", "504.39", "50.78"),
        # ArcadeDB: RTT=4.92ms
        ("var(--color-arcade)", "ArcadeDB", "Document + Graph (openCypher)",
         "408.87 ms", "3,023.7 n/s", "381.2 e/s",
         "46.98 ms", "55.89 ms", "2.54 QPS", "47.90 ms",
         "51.90", "60.81", "52.82", "4.92"),
        # KuzuDB: RTT=7.05ms
        ("var(--color-kuzu)", "KùzuDB", "Columnar In-Process Engine",
         "219.78 ms", "191.5 n/s", "149.3 e/s",
         "44.69 ms", "48.04 ms", "34.83 QPS", "76.92 ms",
         "51.74", "55.09", "83.97", "7.05"),
    ]

    cloud_rows = [
        # CognoDB Cloud: RTT=310.68ms
        ("var(--color-cogno)", "CognoDB Cloud", "Cloud Native Graph (Bolt)",
         "608.41 ms", "1,483.0 n/s", "3,565.6 e/s",
         "0.00 ms", "0.00 ms", "9.11 QPS", "1,287.15 ms",
         "310.16", "306.62", "1,597.83", "310.68"),
        # Neo4j AuraDB: RTT=246.74ms
        ("var(--color-neo4j)", "Neo4j AuraDB", "JVM Property Graph (LPG)",
         "573.84 ms", "3,109.8 n/s", "2,826.2 e/s",
         "16.25 ms", "26.79 ms", "27.84 QPS", "92.65 ms",
         "262.99", "273.53", "339.39", "246.74"),
        # Memgraph Cloud: RTT=252.21ms
        ("var(--color-memgraph)", "Memgraph Cloud", "In-Memory Native Graph (C++)",
         "515.97 ms", "3,279.2 n/s", "1,694.1 e/s",
         "7.82 ms", "9.89 ms", "35.37 QPS", "106.86 ms",
         "260.03", "262.10", "359.07", "252.21"),
        # FalkorDB Cloud: RTT=264.67ms
        ("var(--color-falkor)", "FalkorDB Cloud", "GraphBLAS Sparse Matrix (C)",
         "470.96 ms", "1,282.6 n/s", "3,940.4 e/s",
         "0.00 ms", "10.00 ms", "59.00 QPS", "293.26 ms",
         "261.28", "274.67", "557.93", "264.67"),
        # ArangoDB Oasis: RTT=258.67ms
        ("var(--color-arango)", "ArangoDB Oasis", "Multi-Model RocksDB (AQL)",
         "543.92 ms", "2,001.2 n/s", "3,000.9 e/s",
         "6.68 ms", "0.00 ms", "68.68 QPS", "251.79 ms",
         "265.35", "225.63", "510.46", "258.67"),
    ]


    def build_table_html(rows, table_id):
        html_rows = ""
        for color, name, paradigm, idx_build, node_ing, edge_ing, hop1_net, hop3_net, qps, deg_net, hop1_raw, hop3_raw, deg_raw, rtt in rows:
            html_rows += f"""
            <tr>
              <td><span class="db-badge"><span class="badge-dot" style="background: {color}"></span>{name}</span></td>
              <td>{paradigm}</td>
              <td class="rtt-cell">{rtt} ms</td>
              <td data-val="{idx_build}">{idx_build}</td>
              <td data-val="{node_ing}">{node_ing}</td>
              <td data-val="{edge_ing}">{edge_ing}</td>
              <td data-val="{hop1_net}" title="Raw: {hop1_raw} ms">{hop1_net} <span class="raw-hint">(raw: {hop1_raw})</span></td>
              <td data-val="{hop3_net}" title="Raw: {hop3_raw} ms">{hop3_net} <span class="raw-hint">(raw: {hop3_raw})</span></td>
              <td data-val="{qps}">{qps}</td>
              <td data-val="{deg_net}" title="Raw: {deg_raw} ms">{deg_net} <span class="raw-hint">(raw: {deg_raw})</span></td>
            </tr>"""

        return f"""
      <div class="table-container">
        <table id="{table_id}">
          <thead>
            <tr>
              <th>Database</th>
              <th>Paradigm</th>
              <th>Baseline RTT</th>
              <th data-best="low">Index Build</th>
              <th data-best="high">Node Ingest</th>
              <th data-best="high">Edge Ingest</th>
              <th data-best="low">1-Hop p50 (Net)</th>
              <th data-best="low">3-Hop p50 (Net)</th>
              <th data-best="high">40-Client QPS</th>
              <th data-best="low">Degree Agg (Net)</th>
            </tr>
          </thead>
          <tbody>{html_rows}
          </tbody>
        </table>
      </div>"""

    local_table = build_table_html(local_rows, "local-table")
    cloud_table = build_table_html(cloud_rows, "cloud-table")

    # ── assemble diagram grids ──
    local_diagrams = "".join([
        card("Bulk Ingestion & Indexing Throughput",
             "Node insertion (nodes/sec) and edge relationship creation (edges/sec) — Pokec dataset.",
             local_imgs["ingest"]),
        card("Multi-Hop Traversal Latency (p50 ms)",
             "1-Hop, 2-Hop, and 3-Hop neighborhood expansion latencies (lower is better).",
             local_imgs["traversal"]),
        card("Concurrency Throughput Scaling (QPS)",
             "Sustained queries per second across 1, 10, and 40 concurrent worker threads.",
             local_imgs["qps"]),
        card("Tail Latency Degradation Under Load (p95 ms)",
             "p95 latency growth as concurrent client connections increase from 1 to 40.",
             local_imgs["p95"]),
        card("Multi-Dimensional Radar Performance Profile",
             "Holistic comparison across Ingest, Lookup, 1-Hop, 3-Hop, QPS, and Scalability.",
             local_imgs["radar"]),
        card("Architectural Tradeoff Quadrant",
             "1-Hop Traversal Latency vs Concurrency QPS (Bubble size = Ingestion speed).",
             local_imgs["quadrant"]),
        card("Tail Jitter & Latency Variance (2-Hop)",
             "Comparison of p50 median, p95 tail, and p99 extreme latency spread.",
             local_imgs["jitter"]),
        card("Concurrency Speedup Multiplier",
             "Speedup ratio achieved at 40 concurrent workers relative to single-threaded baseline.",
             local_imgs["speedup"]),
        card("Cold Start vs. Warm Cache Latency",
             "Buffer cache warm-up acceleration on point lookup queries.",
             local_imgs["cold_warm"]),
        card("Comprehensive Workload Benchmark Heatmap Matrix",
             "Normalized multi-workload matrix ranking all 8 engines across ingestion, traversals, aggregations, and concurrent throughput.",
             local_imgs["matrix"], full=True),
    ])

    cloud_diagrams = "".join([
        card("Cloud Ingestion & Indexing Throughput",
             "Node and edge ingestion over public WAN connection to managed cloud tiers.",
             cloud_imgs["ingest"]),
        card("Cloud Traversal Latency Profile (p50 ms)",
             "Multi-hop graph expansion over WAN network endpoints.",
             cloud_imgs["traversal"]),
        card("Cloud Concurrency Scaling (QPS)",
             "Sustained throughput under 1, 10, 40 remote client sessions.",
             cloud_imgs["qps"]),
        card("Cloud Tail Latency Degradation (p95 ms)",
             "p95 latency response under remote client concurrency.",
             cloud_imgs["p95"]),
        card("Cloud Radar Performance Profile",
             "Comprehensive comparative radar polygon across cloud tiers.",
             cloud_imgs["radar"]),
        card("Cloud Architectural Tradeoff Quadrant",
             "1-Hop Traversal Latency vs Concurrency QPS across Cloud databases.",
             cloud_imgs["quadrant"]),
        card("Cloud Tail Jitter & Latency Variance",
             "Comparison of p50, p95, and p99 latency spread across cloud engines.",
             cloud_imgs["jitter"]),
        card("Cloud Concurrency Speedup Multiplier",
             "Scaling multiplier achieved at 40 concurrent remote workers.",
             cloud_imgs["speedup"]),
        card("Cloud Comprehensive Heatmap Matrix",
             "Normalized cross-workload ranking across all 5 cloud managed tiers.",
             cloud_imgs["matrix"], full=True),
    ])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Wexa AI Graph Benchmark — Interactive Executive Suite</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600;700&family=Geist:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
  <style>
    :root {{
      --paper: #f8fafc;
      --paper-card: #ffffff;
      --ink: #0f172a;
      --muted: #475569;
      --soft: #94a3b8;
      --rule: rgba(148, 163, 184, 0.25);
      --rule-solid: #e2e8f0;
      --accent: #eb6c36;
      --accent-tint: rgba(235, 108, 54, 0.10);

      --color-cogno: #6366f1;
      --color-neo4j: #0284c7;
      --color-memgraph: #10b981;
      --color-falkor: #ef4444;
      --color-arango: #f59e0b;
      --color-kuzu: #ec4899;
      --color-janus: #8b5cf6;
      --color-arcade: #eab308;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background-color: var(--paper);
      color: var(--ink);
      font-family: 'Geist', -apple-system, BlinkMacSystemFont, sans-serif;
      line-height: 1.5;
      padding: 2.5rem 1.5rem 5rem;
    }}

    .container {{ max-width: 1200px; margin: 0 auto; }}

    header {{
      margin-bottom: 2rem;
      border-bottom: 1px solid var(--rule-solid);
      padding-bottom: 1.5rem;
    }}

    .eyebrow {{
      font-family: 'Geist Mono', monospace;
      font-size: 0.8rem;
      font-weight: 600;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 0.5rem;
    }}

    h1 {{
      font-family: 'Instrument Serif', Georgia, serif;
      font-size: 2.75rem;
      font-weight: 400;
      color: var(--ink);
      letter-spacing: -0.02em;
      line-height: 1.1;
      margin-bottom: 0.75rem;
    }}

    .subtitle {{
      font-size: 1.05rem;
      color: var(--muted);
      max-width: 900px;
    }}

    /* ── View Switcher ── */
    .view-switcher {{
      display: flex; gap: 1rem; margin: 1.5rem 0 2rem;
      background: #e2e8f0; padding: 0.35rem;
      border-radius: 10px; width: fit-content;
    }}
    .view-btn {{
      padding: 0.6rem 1.4rem; border: none; background: transparent;
      font-family: 'Geist', sans-serif; font-size: 0.95rem; font-weight: 600;
      color: var(--muted); cursor: pointer; border-radius: 8px;
      transition: all 0.2s ease;
    }}
    .view-btn.active {{
      background: var(--paper-card); color: var(--ink);
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}

    /* ── Section Headers ── */
    .section-title {{
      font-family: 'Instrument Serif', Georgia, serif;
      font-size: 2rem; font-weight: 400;
      margin: 2.5rem 0 1rem; color: var(--ink);
      border-bottom: 1px solid var(--rule-solid); padding-bottom: 0.5rem;
    }}

    /* ── KPI Cards ── */
    .kpi-grid {{
      display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 1.25rem; margin-bottom: 2rem;
    }}
    .kpi-card {{
      background: var(--paper-card); border: 1px solid var(--rule-solid);
      border-radius: 12px; padding: 1.25rem 1.5rem;
    }}
    .kpi-label {{
      font-family: 'Geist Mono', monospace; font-size: 0.75rem;
      text-transform: uppercase; letter-spacing: 0.08em;
      color: var(--muted); margin-bottom: 0.35rem;
    }}
    .kpi-val {{
      font-size: 1.75rem; font-weight: 700;
      color: var(--ink); letter-spacing: -0.02em;
    }}
    .kpi-desc {{
      font-size: 0.82rem; color: var(--muted); margin-top: 0.25rem;
    }}

    /* ── Diagram Grid ── */
    .diagram-grid {{
      display: grid; grid-template-columns: repeat(auto-fit, minmax(540px, 1fr));
      gap: 1.75rem; margin-bottom: 2.5rem;
    }}
    .diagram-card {{
      background: var(--paper-card); border: 1px solid var(--rule-solid);
      border-radius: 12px; overflow: hidden;
      display: flex; flex-direction: column;
    }}
    .diagram-card-full {{ grid-column: 1 / -1; }}
    .diagram-card-header {{
      padding: 1rem 1.25rem;
      border-bottom: 1px solid var(--rule-solid); background: #fafbfc;
    }}
    .diagram-title {{ font-size: 1.05rem; font-weight: 700; color: var(--ink); }}
    .diagram-desc {{ font-size: 0.85rem; color: var(--muted); margin-top: 0.2rem; }}
    .diagram-card-body {{
      padding: 1rem; display: flex; align-items: center;
      justify-content: center; background: #ffffff; position: relative;
    }}
    .diagram-img {{
      width: 100%; height: auto; border-radius: 6px;
      display: block; cursor: zoom-in;
      transition: transform 0.15s ease;
    }}
    .diagram-img:hover {{ transform: scale(1.01); }}

    /* ── Zoom hint ── */
    .diagram-card-body::after {{
      content: '🔍 Click to zoom';
      position: absolute; bottom: 12px; right: 16px;
      font-family: 'Geist Mono', monospace; font-size: 0.7rem;
      color: var(--soft); background: rgba(255,255,255,0.85);
      padding: 2px 8px; border-radius: 4px;
      pointer-events: none; opacity: 0;
      transition: opacity 0.2s ease;
    }}
    .diagram-card-body:hover::after {{ opacity: 1; }}

    /* ── Lightbox Modal ── */
    .lightbox-overlay {{
      display: none; position: fixed; inset: 0; z-index: 9999;
      background: rgba(15, 23, 42, 0.88);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      justify-content: center; align-items: center;
      cursor: zoom-out; padding: 2rem;
    }}
    .lightbox-overlay.active {{ display: flex; }}
    .lightbox-overlay img {{
      max-width: 95vw; max-height: 92vh;
      border-radius: 10px;
      box-shadow: 0 25px 60px rgba(0,0,0,0.5);
      cursor: default;
      animation: lightboxIn 0.25s ease;
    }}
    @keyframes lightboxIn {{
      from {{ opacity: 0; transform: scale(0.92); }}
      to {{ opacity: 1; transform: scale(1); }}
    }}
    .lightbox-close {{
      position: fixed; top: 1.5rem; right: 1.5rem;
      width: 44px; height: 44px; border-radius: 50%;
      background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.2);
      color: white; font-size: 1.4rem; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      z-index: 10000; transition: background 0.15s ease;
    }}
    .lightbox-close:hover {{ background: rgba(255,255,255,0.3); }}
    .lightbox-title {{
      position: fixed; bottom: 1.5rem; left: 50%;
      transform: translateX(-50%);
      font-family: 'Geist', sans-serif; font-size: 0.95rem;
      color: rgba(255,255,255,0.9); background: rgba(0,0,0,0.45);
      padding: 0.4rem 1.2rem; border-radius: 8px;
      z-index: 10000; pointer-events: none;
      max-width: 80vw; text-align: center;
    }}

    /* ── Table Styles ── */
    .table-container {{
      background: var(--paper-card); border: 1px solid var(--rule-solid);
      border-radius: 12px; overflow-x: auto; margin-bottom: 2rem;
    }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; text-align: left; }}
    th {{
      background: #f1f5f9; font-family: 'Geist Mono', monospace;
      font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
      letter-spacing: 0.08em; color: var(--muted);
      padding: 0.85rem 1.2rem; border-bottom: 1px solid var(--rule-solid);
      position: sticky; top: 0; z-index: 1;
    }}
    td {{
      padding: 0.85rem 1.2rem;
      border-bottom: 1px solid var(--rule-solid); color: var(--ink);
    }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: #f8fafc; }}

    .db-badge {{ display: inline-flex; align-items: center; gap: 0.4rem; font-weight: 600; }}
    .badge-dot {{ width: 8px; height: 8px; border-radius: 50%; }}

    /* ── Best-value highlight ── */
    td.best-val {{
      background: linear-gradient(135deg, rgba(16,185,129,0.10), rgba(16,185,129,0.05)) !important;
      font-weight: 700;
      position: relative;
    }}
    td.best-val::before {{
      content: '\u2605';
      position: absolute; top: 4px; right: 6px;
      font-size: 0.65rem; color: #10b981;
    }}

    /* ── Raw-value hint (parenthetical) ── */
    .raw-hint {{
      font-size: 0.75rem; color: var(--soft);
      font-family: 'Geist Mono', monospace;
    }}

    /* ── RTT column ── */
    .rtt-cell {{
      font-family: 'Geist Mono', monospace;
      font-size: 0.82rem; color: var(--muted);
      background: rgba(99, 102, 241, 0.04);
    }}

    .hidden {{ display: none !important; }}

    /* ── Legend ── */
    .legend-strip {{
      display: flex; flex-wrap: wrap; gap: 0.5rem;
      margin-bottom: 0.75rem; font-size: 0.82rem; color: var(--muted);
    }}
    .legend-item {{
      display: inline-flex; align-items: center; gap: 0.25rem;
    }}

    @media (max-width: 640px) {{
      .diagram-grid {{ grid-template-columns: 1fr; }}
      h1 {{ font-size: 1.8rem; }}
    }}
  </style>
</head>
<body>
  <!-- Lightbox Modal -->
  <div class="lightbox-overlay" id="lightbox" onclick="closeLightbox(event)">
    <button class="lightbox-close" onclick="closeLightbox(event)" aria-label="Close">&times;</button>
    <img id="lightbox-img" src="" alt="Zoomed Chart">
    <div class="lightbox-title" id="lightbox-title"></div>
  </div>

  <div class="container">
    <header>
      <div class="eyebrow">Wexa AI Graph Database Benchmarking Suite</div>
      <h1>Performance &amp; Scalability Comparative Analysis</h1>
      <p class="subtitle">
        Empirical evaluation comparing <strong>CognoDB Cloud</strong> against open-source graph engines
        (Neo4j, Memgraph, FalkorDB, ArangoDB, KùzuDB, JanusGraph, ArcadeDB) across bulk ingestion,
        multi-hop traversals, tail latency jitter, and concurrent throughput scaling.
      </p>
    </header>

    <!-- View Switcher -->
    <div class="view-switcher">
      <button class="view-btn active" onclick="switchView('local')">📊 Local Run (8 Engines + CognoDB Baseline)</button>
      <button class="view-btn" onclick="switchView('cloud')">☁️ Cloud Run (5 Cloud Managed Tiers)</button>
    </div>

    <!-- ════════════════════════════════════════════════════════ -->
    <!-- LOCAL VIEW                                              -->
    <!-- ════════════════════════════════════════════════════════ -->
    <div id="local-view">
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">Fastest Ingestion Engine</div>
          <div class="kpi-val" style="color: var(--color-falkor)">FalkorDB</div>
          <div class="kpi-desc">41,924.5 nodes/s &amp; 10,190.7 edges/s</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Lowest Traversal Latency (p50)</div>
          <div class="kpi-val" style="color: var(--color-falkor)">1.09 ms</div>
          <div class="kpi-desc">FalkorDB GraphBLAS 1-Hop (1.08ms 3-Hop)</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Peak 40-Worker Throughput</div>
          <div class="kpi-val" style="color: var(--color-falkor)">766.9 QPS</div>
          <div class="kpi-desc">FalkorDB mixed 80% Read / 20% Write</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Highest Scalability Factor</div>
          <div class="kpi-val" style="color: var(--color-arango)">21.1x</div>
          <div class="kpi-desc">ArangoDB Oasis (22 QPS &rarr; 464 QPS)</div>
        </div>
      </div>

      <h2 class="section-title">Visual Diagrams &amp; Telemetry Charts</h2>
      <div class="legend-strip">
        <span class="legend-item">🔍 Click any chart to zoom &amp; inspect details</span>
        <span class="legend-item">| Press <kbd>Esc</kbd> to close</span>
      </div>
      <div class="diagram-grid">
        {local_diagrams}
      </div>

      <h2 class="section-title">Detailed Workload Metric Summary Tables</h2>
      <div class="legend-strip">
        <span class="legend-item"><span style="color:#10b981; font-weight:700;">★</span> Best value per column (lowest latency / highest throughput)</span>
        <span class="legend-item">| <strong>(Net)</strong> = Raw p50 minus Baseline RTT (server-side compute only)</span>
        <span class="legend-item">| <span class="raw-hint">(raw: X)</span> = measured wall-clock latency incl. network</span>
      </div>
      {local_table}
    </div>

    <!-- ════════════════════════════════════════════════════════ -->
    <!-- CLOUD VIEW                                              -->
    <!-- ════════════════════════════════════════════════════════ -->
    <div id="cloud-view" class="hidden">
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">Fastest Cloud Ingestion</div>
          <div class="kpi-val" style="color: var(--color-memgraph)">Memgraph Cloud</div>
          <div class="kpi-desc">3,279.2 nodes/s &amp; 1,694.1 edges/s</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Lowest Cloud Traversal (p50)</div>
          <div class="kpi-val" style="color: var(--color-memgraph)">260.0 ms</div>
          <div class="kpi-desc">Memgraph Cloud 1-Hop (Net: 7.82ms)</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Peak Cloud Concurrency</div>
          <div class="kpi-val" style="color: var(--color-arango)">68.68 QPS</div>
          <div class="kpi-desc">ArangoDB Oasis (40 workers)</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Highest Cloud Speedup</div>
          <div class="kpi-val" style="color: var(--color-neo4j)">38.1x</div>
          <div class="kpi-desc">Neo4j AuraDB (0.73 QPS &rarr; 27.84 QPS)</div>
        </div>
      </div>

      <h2 class="section-title">Cloud Run Visual Diagrams &amp; Telemetry Charts</h2>
      <div class="legend-strip">
        <span class="legend-item">🔍 Click any chart to zoom &amp; inspect details</span>
        <span class="legend-item">| Press <kbd>Esc</kbd> to close</span>
      </div>
      <div class="diagram-grid">
        {cloud_diagrams}
      </div>

      <h2 class="section-title">Cloud Workload Metric Summary Tables</h2>
      <div class="legend-strip">
        <span class="legend-item"><span style="color:#10b981; font-weight:700;">★</span> Best value per column (lowest latency / highest throughput)</span>
        <span class="legend-item">| <strong>(Net)</strong> = Raw p50 minus Baseline RTT (server-side compute only)</span>
        <span class="legend-item">| <span class="raw-hint">(raw: X)</span> = measured wall-clock latency incl. network</span>
      </div>
      {cloud_table}
    </div>
  </div>

  <script>
    /* ── View switching ── */
    function switchView(view) {{
      const local = document.getElementById('local-view');
      const cloud = document.getElementById('cloud-view');
      const btns = document.querySelectorAll('.view-btn');
      if (view === 'local') {{
        local.classList.remove('hidden');
        cloud.classList.add('hidden');
        btns[0].classList.add('active');
        btns[1].classList.remove('active');
      }} else {{
        local.classList.add('hidden');
        cloud.classList.remove('hidden');
        btns[0].classList.remove('active');
        btns[1].classList.add('active');
      }}
      window.scrollTo(0, 0);
    }}

    /* ── Lightbox zoom ── */
    function openLightbox(imgEl) {{
      const overlay = document.getElementById('lightbox');
      const lbImg = document.getElementById('lightbox-img');
      const lbTitle = document.getElementById('lightbox-title');
      lbImg.src = imgEl.src;
      lbTitle.textContent = imgEl.alt || '';
      overlay.classList.add('active');
      document.body.style.overflow = 'hidden';
    }}

    function closeLightbox(e) {{
      if (e && e.target && e.target.tagName === 'IMG') return;
      const overlay = document.getElementById('lightbox');
      overlay.classList.remove('active');
      document.body.style.overflow = '';
    }}

    document.addEventListener('keydown', function(e) {{
      if (e.key === 'Escape') closeLightbox(null);
    }});

    /* ── Best-value highlighting ── */
    function highlightBest(tableId) {{
      const table = document.getElementById(tableId);
      if (!table) return;
      const headers = table.querySelectorAll('thead th[data-best]');
      const rows = table.querySelectorAll('tbody tr');
      if (rows.length === 0) return;

      headers.forEach(function(th, hi) {{
        const colIdx = Array.from(th.parentElement.children).indexOf(th);
        const direction = th.dataset.best; // 'high' or 'low'
        let bestVal = null;
        let bestCells = [];

        rows.forEach(function(tr) {{
          const td = tr.children[colIdx];
          if (!td || !td.dataset.val) return;
          const raw = td.dataset.val.replace(/[^0-9.\-]/g, '');
          const num = parseFloat(raw);
          if (isNaN(num)) return;

          if (bestVal === null) {{
            bestVal = num;
            bestCells = [td];
          }} else if (direction === 'high' && num > bestVal) {{
            bestVal = num;
            bestCells = [td];
          }} else if (direction === 'low' && num < bestVal) {{
            bestVal = num;
            bestCells = [td];
          }} else if (num === bestVal) {{
            bestCells.push(td);
          }}
        }});

        bestCells.forEach(function(td) {{ td.classList.add('best-val'); }});
      }});
    }}

    highlightBest('local-table');
    highlightBest('cloud-table');
  </script>
</body>
</html>"""

    targets = [
        "d:/Projects/WEXA/benchmark_comparison_dashboard.html",
        "d:/Projects/WEXA/Local Run/benchmark_comparison_dashboard.html",
        "d:/Projects/WEXA/LocalRun/benchmark_comparison_dashboard.html",
        "d:/Projects/WEXA/CloudRun/benchmark_comparison_dashboard.html",
    ]

    for t in targets:
        Path(t).parent.mkdir(parents=True, exist_ok=True)
        with open(t, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[OK] Generated: {t}")


if __name__ == "__main__":
    build_self_contained_dashboards()
