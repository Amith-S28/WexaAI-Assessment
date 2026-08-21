"""
Graphify Pipeline Execution Harness
Executes graphify Steps 1-5 on the repository.
"""

import sys
import json
from pathlib import Path
from graphify.detect import detect
from graphify.extract import collect_files, extract
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json, to_html

def run_pipeline(root_path: Path):
    out_dir = root_path / "graphify-out"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print("=== Step 1 & 2: Detecting Files ===")
    detection = detect(root_path)
    detect_file = out_dir / ".graphify_detect.json"
    detect_file.write_text(json.dumps(detection, ensure_ascii=False, indent=2), encoding="utf-8")
    
    total_files = detection.get("total_files", 0)
    total_words = detection.get("total_words", 0)
    print(f"Corpus: {total_files} files · ~{total_words:,} words")
    for k, v in detection.get("files", {}).items():
        if v:
            print(f"  {k}: {len(v)} files")
            
    print("\n=== Step 3: AST Extraction for Code Files ===")
    code_files = []
    for f in detection.get("files", {}).get("code", []):
        p = Path(f)
        if p.exists():
            code_files.extend(collect_files(p) if p.is_dir() else [p])
            
    if code_files:
        ast_result = extract(code_files, cache_root=root_path)
        print(f"AST: {len(ast_result['nodes'])} nodes, {len(ast_result['edges'])} edges extracted")
    else:
        ast_result = {'nodes': [], 'edges': [], 'input_tokens': 0, 'output_tokens': 0}
        print("No code files to extract.")
        
    (out_dir / ".graphify_ast.json").write_text(json.dumps(ast_result, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Semantic extraction
    sem_result = {'nodes': [], 'edges': [], 'hyperedges': [], 'input_tokens': 0, 'output_tokens': 0}
    (out_dir / ".graphify_semantic.json").write_text(json.dumps(sem_result, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Merge AST + Semantic
    merged_nodes = list(ast_result['nodes'])
    merged_edges = list(ast_result['edges'])
    merged_extract = {
        'nodes': merged_nodes,
        'edges': merged_edges,
        'hyperedges': [],
        'input_tokens': 0,
        'output_tokens': 0,
    }
    (out_dir / ".graphify_extract.json").write_text(json.dumps(merged_extract, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Merged extraction: {len(merged_nodes)} nodes, {len(merged_edges)} edges")
    
    print("\n=== Step 4: Building Graph & Clustering ===")
    G = build_from_json(merged_extract, root=str(root_path), directed=False)
    if G.number_of_nodes() == 0:
        print("ERROR: Graph is empty.")
        return
        
    communities = cluster(G)
    cohesion = score_all(G, communities)
    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)
    
    # Generate informative labels
    labels = {}
    for cid, nodes in communities.items():
        sub_names = [n for n in nodes if not n.startswith("file:")][:3]
        if sub_names:
            labels[cid] = f"Module: {', '.join(sub_names)}"
        else:
            labels[cid] = f"Cluster {cid} ({len(nodes)} entities)"
            
    questions = suggest_questions(G, communities, labels)
    tokens = {'input': 0, 'output': 0}
    
    # Export outputs
    to_json(G, communities, str(out_dir / "graph.json"), force=True, community_labels=labels)
    
    report_text = generate(
        G=G,
        communities=communities,
        cohesion_scores=cohesion,
        community_labels=labels,
        god_node_list=gods,
        surprise_list=surprises,
        detection_result=detection,
        token_cost=tokens,
        root=str(root_path),
        suggested_questions=questions
    )
    (out_dir / "GRAPH_REPORT.md").write_text(report_text, encoding="utf-8")
    
    to_html(G, communities, str(out_dir / "graph.html"), community_labels=labels)
    
    cost_data = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_cost_usd": 0.0,
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "communities": len(communities)
    }
    (out_dir / "cost.json").write_text(json.dumps(cost_data, indent=2), encoding="utf-8")
    
    print(f"\n[OK] Graphify pipeline completed successfully:")
    print(f"  - Nodes: {G.number_of_nodes()}")
    print(f"  - Edges: {G.number_of_edges()}")
    print(f"  - Communities: {len(communities)}")
    print(f"  - Report: {out_dir / 'GRAPH_REPORT.md'}")
    print(f"  - Visual Graph: {out_dir / 'graph.html'}")
    print(f"  - GraphRAG JSON: {out_dir / 'graph.json'}")

if __name__ == "__main__":
    run_pipeline(Path("d:/Projects/WEXA"))
