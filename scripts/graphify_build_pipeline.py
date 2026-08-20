import sys
import json
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def main():
    # Part C: Merge AST + Semantic
    ast = json.loads(Path("graphify-out/.graphify_ast.json").read_text(encoding="utf-8"))
    sem = json.loads(Path("graphify-out/.graphify_semantic.json").read_text(encoding="utf-8"))

    seen = {n["id"] for n in ast["nodes"]}
    merged_nodes = list(ast["nodes"])
    for n in sem["nodes"]:
        if n["id"] not in seen:
            merged_nodes.append(n)
            seen.add(n["id"])

    merged_edges = ast["edges"] + sem["edges"]
    merged_hyperedges = sem.get("hyperedges", [])
    merged = {
        "nodes": merged_nodes,
        "edges": merged_edges,
        "hyperedges": merged_hyperedges,
        "input_tokens": sem.get("input_tokens", 0),
        "output_tokens": sem.get("output_tokens", 0),
    }
    Path("graphify-out/.graphify_extract.json").write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Merged: {len(merged_nodes)} nodes, {len(merged_edges)} edges ({len(ast['nodes'])} AST + {len(sem['nodes'])} semantic)")

    # Step 4: Build Graph, cluster, analyze, generate
    from graphify.build import build_from_json
    from graphify.cluster import cluster, score_all
    from graphify.analyze import god_nodes, surprising_connections, suggest_questions
    from graphify.report import generate
    from graphify.export import to_json
    from graphify.diagnostics import diagnose_extraction, format_diagnostic_report

    extraction = merged
    detection = json.loads(Path("graphify-out/.graphify_detect.json").read_text(encoding="utf-8"))

    G = build_from_json(extraction, root=".", directed=False)
    if G.number_of_nodes() == 0:
        print("ERROR: Graph is empty - extraction produced no nodes.")
        sys.exit(1)
        
    communities = cluster(G)
    cohesion = score_all(G, communities)
    tokens = {"input": extraction.get("input_tokens", 0), "output": extraction.get("output_tokens", 0)}
    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)
    labels = {cid: f"Community {cid}" for cid in communities}
    questions = suggest_questions(G, communities, labels)

    wrote = to_json(G, communities, "graphify-out/graph.json")
    print(f"Graph Exported: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities")

    # Step 4.5: Graph health check
    summary = diagnose_extraction(extraction, directed=False, root=".")
    print(format_diagnostic_report(summary))

    # Step 5: Label communities intelligently
    # Inspect top nodes per community to give semantic names
    community_labels = {}
    for cid, node_ids in communities.items():
        node_labels = [G.nodes[nid].get("label", nid) for nid in node_ids[:5] if nid in G.nodes]
        joined = " / ".join(node_labels)
        if any("Adapter" in l or "bolt" in l.lower() or "graph" in l.lower() for l in node_labels):
            community_labels[cid] = "Database Adapters & Wire Protocols"
        elif any("orchestrator" in l.lower() or "runner" in l.lower() or "workload" in l.lower() for l in node_labels):
            community_labels[cid] = "Benchmark Orchestration & Workloads"
        elif any("stats" in l.lower() or "report" in l.lower() or "chart" in l.lower() or "diagram" in l.lower() for l in node_labels):
            community_labels[cid] = "Statistical Analysis & Visual Reporting"
        elif any("verify" in l.lower() or "test" in l.lower() or "probe" in l.lower() for l in node_labels):
            community_labels[cid] = "Pre-Flight Validation & Infrastructure Probes"
        elif any("docker" in l.lower() or "cloud" in l.lower() or "dataset" in l.lower() for l in node_labels):
            community_labels[cid] = "Environment Architecture & Datasets"
        else:
            community_labels[cid] = f"Module Group {cid}"

    real_questions = suggest_questions(G, communities, community_labels)
    report = generate(G, communities, cohesion, community_labels, gods, surprises, detection, tokens, ".", suggested_questions=real_questions)
    Path("graphify-out/GRAPH_REPORT.md").write_text(report, encoding="utf-8")
    Path("graphify-out/.graphify_labels.json").write_text(json.dumps({str(k): v for k, v in community_labels.items()}, ensure_ascii=False), encoding="utf-8")
    print("Report generated in graphify-out/GRAPH_REPORT.md")

if __name__ == "__main__":
    main()
