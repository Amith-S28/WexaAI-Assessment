"""
Interactive Visual Dashboard Generator for Cloud Run & Local Run Benchmark Results.
Generates an executive-grade, interactive HTML dashboard with embedded charts,
interactive KPI cards, comparison tables, and architectural insights.
"""

import json
from pathlib import Path

def generate_dashboard():
    with open("Local Run/benchmark_results.json", "r", encoding="utf-8") as f:
        local_data = json.load(f)
        
    with open("CloudRun/benchmark_results.json", "r", encoding="utf-8") as f:
        cloud_data = json.load(f)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Wexa AI Graph Benchmark — Cloud Run & Local Run Executive Suite</title>
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

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background-color: var(--paper);
      color: var(--ink);
      font-family: 'Geist', -apple-system, BlinkMacSystemFont, sans-serif;
      line-height: 1.5;
      padding: 2.5rem 1.5rem 5rem;
    }}

    .container {{
      max-width: 1200px;
      margin: 0 auto;
    }}

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

    /* View Switcher */
    .view-switcher {{
      display: flex;
      gap: 1rem;
      margin: 1.5rem 0 2rem;
      background: #e2e8f0;
      padding: 0.35rem;
      border-radius: 10px;
      width: fit-content;
    }}

    .view-btn {{
      padding: 0.6rem 1.4rem;
      border: none;
      background: transparent;
      font-family: 'Geist', sans-serif;
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--muted);
      cursor: pointer;
      border-radius: 8px;
      transition: all 0.2s ease;
    }}

    .view-btn.active {{
      background: var(--paper-card);
      color: var(--ink);
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}

    /* Section Headers */
    .section-title {{
      font-family: 'Instrument Serif', Georgia, serif;
      font-size: 2rem;
      font-weight: 400;
      margin: 2.5rem 0 1rem;
      color: var(--ink);
      border-bottom: 1px solid var(--rule-solid);
      padding-bottom: 0.5rem;
    }}

    /* KPI Cards */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 1.25rem;
      margin-bottom: 2rem;
    }}

    .kpi-card {{
      background: var(--paper-card);
      border: 1px solid var(--rule-solid);
      border-radius: 12px;
      padding: 1.25rem 1.5rem;
    }}

    .kpi-label {{
      font-family: 'Geist Mono', monospace;
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      margin-bottom: 0.35rem;
    }}

    .kpi-val {{
      font-size: 1.75rem;
      font-weight: 700;
      color: var(--ink);
      letter-spacing: -0.02em;
    }}

    .kpi-desc {{
      font-size: 0.82rem;
      color: var(--muted);
      margin-top: 0.25rem;
    }}

    /* Diagram Grid */
    .diagram-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(540px, 1fr));
      gap: 1.75rem;
      margin-bottom: 2.5rem;
    }}

    .diagram-card {{
      background: var(--paper-card);
      border: 1px solid var(--rule-solid);
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}

    .diagram-card-full {{
      grid-column: 1 / -1;
    }}

    .diagram-card-header {{
      padding: 1rem 1.25rem;
      border-bottom: 1px solid var(--rule-solid);
      background: #fafbfc;
    }}

    .diagram-title {{
      font-size: 1.05rem;
      font-weight: 700;
      color: var(--ink);
    }}

    .diagram-desc {{
      font-size: 0.85rem;
      color: var(--muted);
      margin-top: 0.2rem;
    }}

    .diagram-card-body {{
      padding: 1rem;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #ffffff;
    }}

    .diagram-img {{
      width: 100%;
      height: auto;
      border-radius: 6px;
      display: block;
    }}

    /* Table Styles */
    .table-container {{
      background: var(--paper-card);
      border: 1px solid var(--rule-solid);
      border-radius: 12px;
      overflow-x: auto;
      margin-bottom: 2rem;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
      text-align: left;
    }}

    th {{
      background: #f1f5f9;
      font-family: 'Geist Mono', monospace;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      padding: 0.85rem 1.2rem;
      border-bottom: 1px solid var(--rule-solid);
    }}

    td {{
      padding: 0.85rem 1.2rem;
      border-bottom: 1px solid var(--rule-solid);
      color: var(--ink);
    }}

    tr:last-child td {{
      border-bottom: none;
    }}

    tr:hover td {{
      background: #f8fafc;
    }}

    .db-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      font-weight: 600;
    }}

    .badge-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }}

    .hidden {{
      display: none !important;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="eyebrow">Wexa AI Graph Database Benchmarking Suite</div>
      <h1>Performance & Scalability Comparative Analysis</h1>
      <p class="subtitle">
        Empirical evaluation comparing <strong>CognoDB Cloud</strong> against open-source graph engines (Neo4j, Memgraph, FalkorDB, ArangoDB, KùzuDB, JanusGraph, ArcadeDB) across bulk ingestion, multi-hop traversals, tail latency jitter, and concurrent throughput scaling.
      </p>
    </header>

    <!-- View Switcher -->
    <div class="view-switcher">
      <button class="view-btn active" onclick="switchView('local')">📊 Local Run (8 Engines + CognoDB Baseline)</button>
      <button class="view-btn" onclick="switchView('cloud')">☁️ Cloud Run (5 Cloud Managed Tiers)</button>
    </div>

    <!-- LOCAL VIEW -->
    <div id="local-view">
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">Fastest Ingestion Engine</div>
          <div class="kpi-val" style="color: var(--color-falkor)">FalkorDB</div>
          <div class="kpi-desc">41,924.5 nodes/s & 10,190.7 edges/s</div>
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

      <h2 class="section-title">Visual Diagrams & Telemetry Charts</h2>

      <div class="diagram-grid">
        <!-- Ingestion -->
        <div class="diagram-card">
          <div class="diagram-card-header">
            <div class="diagram-title">Bulk Ingestion & Indexing Throughput</div>
            <div class="diagram-desc">Node insertion (nodes/sec) and edge relationship creation (edges/sec) on 350K Pokec dataset.</div>
          </div>
          <div class="diagram-card-body">
            <img src="Local Run/assets/ingestion_throughput.png" alt="Ingestion Throughput" class="diagram-img">
          </div>
        </div>

        <!-- Traversal -->
        <div class="diagram-card">
          <div class="diagram-card-header">
            <div class="diagram-title">Multi-Hop Traversal Latency (p50 ms)</div>
            <div class="diagram-desc">1-Hop, 2-Hop, and 3-Hop neighborhood expansion latencies (lower is better).</div>
          </div>
          <div class="diagram-card-body">
            <img src="Local Run/assets/traversal_latency_comparison.png" alt="Traversal Latency" class="diagram-img">
          </div>
        </div>

        <!-- Concurrency QPS -->
        <div class="diagram-card">
          <div class="diagram-card-header">
            <div class="diagram-title">Concurrency Throughput Scaling (QPS)</div>
            <div class="diagram-desc">Sustained queries per second across 1, 10, and 40 concurrent worker threads.</div>
          </div>
          <div class="diagram-card-body">
            <img src="Local Run/assets/concurrency_scaling_qps.png" alt="Concurrency Scaling QPS" class="diagram-img">
          </div>
        </div>

        <!-- Concurrency Tail Latency -->
        <div class="diagram-card">
          <div class="diagram-card-header">
            <div class="diagram-title">Tail Latency Degradation Under Load (p95 ms)</div>
            <div class="diagram-desc">p95 latency growth as concurrent client connections increase from 1 to 40.</div>
          </div>
          <div class="diagram-card-body">
            <img src="Local Run/assets/concurrency_p95_latency.png" alt="Concurrency p95 Latency" class="diagram-img">
          </div>
        </div>

        <!-- Radar Profile -->
        <div class="diagram-card">
          <div class="diagram-card-header">
            <div class="diagram-title">Multi-Dimensional Radar Profile</div>
            <div class="diagram-desc">Holistic comparison across Ingest, Lookup, 1-Hop, 3-Hop, QPS, and Scalability.</div>
          </div>
          <div class="diagram-card-body">
            <img src="Local Run/assets/radar_performance_profile.png" alt="Radar Performance Profile" class="diagram-img">
          </div>
        </div>

        <!-- Architectural Quadrant -->
        <div class="diagram-card">
          <div class="diagram-card-header">
            <div class="diagram-title">Architectural Tradeoff Quadrant</div>
            <div class="diagram-desc">1-Hop Traversal Latency vs Concurrency QPS (Bubble size = Ingestion speed).</div>
          </div>
          <div class="diagram-card-body">
            <img src="Local Run/assets/architectural_tradeoff_quadrant.png" alt="Architectural Tradeoff Quadrant" class="diagram-img">
          </div>
        </div>

        <!-- Tail Jitter -->
        <div class="diagram-card">
          <div class="diagram-card-header">
            <div class="diagram-title">Tail Jitter & Latency Variance</div>
            <div class="diagram-desc">Comparison of p50 median, p95 tail, and p99 extreme latency spread.</div>
          </div>
          <div class="diagram-card-body">
            <img src="Local Run/assets/jitter_tail_latency_comparison.png" alt="Jitter Tail Latency" class="diagram-img">
          </div>
        </div>

        <!-- Speedup Factor -->
        <div class="diagram-card">
          <div class="diagram-card-header">
            <div class="diagram-title">Concurrency Speedup Multiplier</div>
            <div class="diagram-desc">Speedup ratio achieved at 40 concurrent workers relative to single-threaded baseline.</div>
          </div>
          <div class="diagram-card-body">
            <img src="Local Run/assets/concurrency_speedup_factor.png" alt="Concurrency Speedup Factor" class="diagram-img">
          </div>
        </div>

        <!-- Comprehensive Heatmap Matrix -->
        <div class="diagram-card diagram-card-full">
          <div class="diagram-card-header">
            <div class="diagram-title">Comprehensive Workload Benchmark Heatmap Matrix</div>
            <div class="diagram-desc">Normalized multi-workload matrix ranking all 8 engines across ingestion, point lookups, multi-hop traversals, degree aggregations, and concurrent throughput.</div>
          </div>
          <div class="diagram-card-body">
            <img src="Local Run/assets/comprehensive_benchmark_matrix.png" alt="Comprehensive Matrix" class="diagram-img">
          </div>
        </div>
      </div>

      <h2 class="section-title">Detailed Workload Metric Summary Tables</h2>

      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Database</th>
              <th>Paradigm</th>
              <th>Index Build</th>
              <th>Node Ingest</th>
              <th>Edge Ingest</th>
              <th>1-Hop p50</th>
              <th>3-Hop p50</th>
              <th>40-Client QPS</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><span class="db-badge"><span class="badge-dot" style="background: var(--color-cogno)"></span>CognoDB Cloud</span></td>
              <td>Cloud Native Graph (Bolt)</td>
              <td>608.41 ms</td>
              <td>1,483.0 n/s</td>
              <td>3,565.6 e/s</td>
              <td>310.16 ms</td>
              <td>306.62 ms</td>
              <td>9.11 QPS</td>
            </tr>
            <tr>
              <td><span class="db-badge"><span class="badge-dot" style="background: var(--color-falkor)"></span>FalkorDB</span></td>
              <td>GraphBLAS Sparse Matrix (C)</td>
              <td>3.45 ms</td>
              <td>41,924.5 n/s</td>
              <td>10,190.7 e/s</td>
              <td>1.09 ms</td>
              <td>1.08 ms</td>
              <td>766.87 QPS</td>
            </tr>
            <tr>
              <td><span class="db-badge"><span class="badge-dot" style="background: var(--color-memgraph)"></span>Memgraph</span></td>
              <td>In-Memory Native Graph (C++)</td>
              <td>9.09 ms</td>
              <td>32,261.5 n/s</td>
              <td>37,930.3 e/s</td>
              <td>1.42 ms</td>
              <td>1.68 ms</td>
              <td>183.15 QPS</td>
            </tr>
            <tr>
              <td><span class="db-badge"><span class="badge-dot" style="background: var(--color-neo4j)"></span>Neo4j 5 Community</span></td>
              <td>JVM Property Graph (LPG)</td>
              <td>684.77 ms</td>
              <td>7,541.5 n/s</td>
              <td>9,437.5 e/s</td>
              <td>3.92 ms</td>
              <td>3.63 ms</td>
              <td>119.95 QPS</td>
            </tr>
            <tr>
              <td><span class="db-badge"><span class="badge-dot" style="background: var(--color-arango)"></span>ArangoDB</span></td>
              <td>Multi-Model RocksDB (AQL)</td>
              <td>94.27 ms</td>
              <td>27,189.0 n/s</td>
              <td>21,465.1 e/s</td>
              <td>43.71 ms</td>
              <td>43.75 ms</td>
              <td>463.97 QPS</td>
            </tr>
            <tr>
              <td><span class="db-badge"><span class="badge-dot" style="background: var(--color-janus)"></span>JanusGraph</span></td>
              <td>TinkerPop Gremlin (BerkeleyJE)</td>
              <td>88.74 ms</td>
              <td>853.8 n/s</td>
              <td>1,266.3 e/s</td>
              <td>55.33 ms</td>
              <td>52.68 ms</td>
              <td>172.86 QPS</td>
            </tr>
            <tr>
              <td><span class="db-badge"><span class="badge-dot" style="background: var(--color-arcade)"></span>ArcadeDB</span></td>
              <td>Document + Graph (openCypher)</td>
              <td>408.87 ms</td>
              <td>3,023.7 n/s</td>
              <td>381.2 e/s</td>
              <td>51.90 ms</td>
              <td>60.81 ms</td>
              <td>2.54 QPS</td>
            </tr>
            <tr>
              <td><span class="db-badge"><span class="badge-dot" style="background: var(--color-kuzu)"></span>KùzuDB</span></td>
              <td>Columnar In-Process Engine</td>
              <td>219.78 ms</td>
              <td>191.5 n/s</td>
              <td>149.3 e/s</td>
              <td>51.74 ms</td>
              <td>55.09 ms</td>
              <td>34.83 QPS</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- CLOUD VIEW -->
    <div id="cloud-view" class="hidden">
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">Fastest Cloud Ingestion</div>
          <div class="kpi-val" style="color: var(--color-memgraph)">Memgraph Cloud</div>
          <div class="kpi-desc">3,279.2 nodes/s & 1,694.1 edges/s</div>
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

      <h2 class="section-title">Cloud Run Visual Diagrams & Telemetry Charts</h2>

      <div class="diagram-grid">
        <!-- Cloud Ingestion -->
        <div class="diagram-card">
          <div class="diagram-card-header">
            <div class="diagram-title">Cloud Ingestion & Indexing Throughput</div>
            <div class="diagram-desc">Node and edge ingestion over public WAN connection.</div>
          </div>
          <div class="diagram-card-body">
            <img src="CloudRun/assets/ingestion_throughput.png" alt="Cloud Ingestion Throughput" class="diagram-img">
          </div>
        </div>

        <!-- Cloud Traversal -->
        <div class="diagram-card">
          <div class="diagram-card-header">
            <div class="diagram-title">Cloud Traversal Latency Profile</div>
            <div class="diagram-desc">Multi-hop graph expansion over WAN network endpoints.</div>
          </div>
          <div class="diagram-card-body">
            <img src="CloudRun/assets/traversal_latency_comparison.png" alt="Cloud Traversal Latency" class="diagram-img">
          </div>
        </div>

        <!-- Cloud Concurrency QPS -->
        <div class="diagram-card">
          <div class="diagram-card-header">
            <div class="diagram-title">Cloud Concurrency Scaling (QPS)</div>
            <div class="diagram-desc">Sustained throughput under 1, 10, 40 remote client sessions.</div>
          </div>
          <div class="diagram-card-body">
            <img src="CloudRun/assets/concurrency_scaling_qps.png" alt="Cloud Concurrency Scaling" class="diagram-img">
          </div>
        </div>

        <!-- Cloud Radar Profile -->
        <div class="diagram-card">
          <div class="diagram-card-header">
            <div class="diagram-title">Cloud Radar Performance Profile</div>
            <div class="diagram-desc">Comprehensive comparative radar polygon across cloud tiers.</div>
          </div>
          <div class="diagram-card-body">
            <img src="CloudRun/assets/radar_performance_profile.png" alt="Cloud Radar Profile" class="diagram-img">
          </div>
        </div>
      </div>

      <h2 class="section-title">Cloud Workload Metric Summary Tables</h2>

      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Database</th>
              <th>Paradigm</th>
              <th>Index Build</th>
              <th>Node Ingest</th>
              <th>Edge Ingest</th>
              <th>1-Hop p50</th>
              <th>3-Hop p50</th>
              <th>40-Client QPS</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><span class="db-badge"><span class="badge-dot" style="background: var(--color-cogno)"></span>CognoDB Cloud</span></td>
              <td>Cloud Native Graph (Bolt)</td>
              <td>608.41 ms</td>
              <td>1,483.0 n/s</td>
              <td>3,565.6 e/s</td>
              <td>310.16 ms</td>
              <td>306.62 ms</td>
              <td>9.11 QPS</td>
            </tr>
            <tr>
              <td><span class="db-badge"><span class="badge-dot" style="background: var(--color-neo4j)"></span>Neo4j AuraDB</span></td>
              <td>JVM Property Graph (LPG)</td>
              <td>573.84 ms</td>
              <td>3,109.8 n/s</td>
              <td>2,826.2 e/s</td>
              <td>262.99 ms</td>
              <td>273.53 ms</td>
              <td>27.84 QPS</td>
            </tr>
            <tr>
              <td><span class="db-badge"><span class="badge-dot" style="background: var(--color-memgraph)"></span>Memgraph Cloud</span></td>
              <td>In-Memory Native Graph (C++)</td>
              <td>515.97 ms</td>
              <td>3,279.2 n/s</td>
              <td>1,694.1 e/s</td>
              <td>260.03 ms</td>
              <td>262.10 ms</td>
              <td>35.37 QPS</td>
            </tr>
            <tr>
              <td><span class="db-badge"><span class="badge-dot" style="background: var(--color-falkor)"></span>FalkorDB Cloud</span></td>
              <td>GraphBLAS Sparse Matrix (C)</td>
              <td>470.96 ms</td>
              <td>1,282.6 n/s</td>
              <td>3,940.4 e/s</td>
              <td>261.28 ms</td>
              <td>274.67 ms</td>
              <td>59.00 QPS</td>
            </tr>
            <tr>
              <td><span class="db-badge"><span class="badge-dot" style="background: var(--color-arango)"></span>ArangoDB Oasis</span></td>
              <td>Multi-Model RocksDB (AQL)</td>
              <td>543.92 ms</td>
              <td>2,001.2 n/s</td>
              <td>3,000.9 e/s</td>
              <td>265.35 ms</td>
              <td>225.63 ms</td>
              <td>68.68 QPS</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <script>
    function switchView(view) {{
      const localView = document.getElementById('local-view');
      const cloudView = document.getElementById('cloud-view');
      const btns = document.querySelectorAll('.view-btn');

      if (view === 'local') {{
        localView.classList.remove('hidden');
        cloudView.classList.add('hidden');
        btns[0].classList.add('active');
        btns[1].classList.remove('active');
      }} else {{
        localView.classList.add('hidden');
        cloudView.classList.remove('hidden');
        btns[0].classList.remove('active');
        btns[1].classList.add('active');
      }}
    }}
  </script>
</body>
</html>
"""
    
    for dest in [
        "d:/Projects/WEXA/benchmark_comparison_dashboard.html",
        "d:/Projects/WEXA/Local Run/benchmark_comparison_dashboard.html",
        "d:/Projects/WEXA/CloudRun/benchmark_comparison_dashboard.html"
    ]:
        with open(dest, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Generated dashboard: {dest}")

if __name__ == "__main__":
    generate_dashboard()
