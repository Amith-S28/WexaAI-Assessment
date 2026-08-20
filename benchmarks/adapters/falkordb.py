"""
FalkorDB Cloud Adapter.
Implements BaseGraphAdapter for FalkorDB's GraphBLAS sparse-matrix graph engine.
"""

import time
from typing import Dict, List, Tuple, Any, Optional
from falkordb import FalkorDB
from .base import BaseGraphAdapter

class FalkorDBAdapter(BaseGraphAdapter):
    """Adapter for FalkorDB Cloud GraphBLAS sparse matrix engine."""
    
    def __init__(self, host: str, port: int = 6379, user: str = "falkordb", password: str = "", graph_name: str = "benchmark_graph"):
        super().__init__(
            name="FalkorDB Cloud",
            db_type="FalkorDB",
            paradigm="GraphBLAS Sparse Linear Algebra (C)"
        )
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.graph_name = graph_name
        self.client: Optional[FalkorDB] = None
        self.graph = None

    def connect(self) -> bool:
        try:
            self.client = FalkorDB(
                host=self.host,
                port=self.port,
                username=self.user,
                password=self.password
            )
            self.graph = self.client.select_graph(self.graph_name)
            self.ping_rtt()
            self.is_connected = True
            return True
        except Exception as e:
            self.is_connected = False
            raise ConnectionError(f"[{self.name}] Failed to connect to {self.host}:{self.port}: {e}")

    def close(self) -> None:
        self.client = None
        self.graph = None
        self.is_connected = False

    def ping_rtt(self) -> float:
        t0 = time.perf_counter_ns()
        self.graph.query("RETURN 1 AS ping")
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000

    def reset_database(self) -> bool:
        try:
            self.graph.delete()
        except Exception:
            pass
        self.graph = self.client.select_graph(self.graph_name)
        return True

    def create_schema_and_indexes(self) -> float:
        t0 = time.perf_counter_ns()
        try:
            self.graph.query("CREATE INDEX FOR (u:User) ON (u.id)")
        except Exception:
            try:
                self.graph.query("CREATE INDEX ON :User(id)")
            except Exception:
                pass
        try:
            self.graph.query("CREATE INDEX FOR (u:User) ON (u.category)")
        except Exception:
            try:
                self.graph.query("CREATE INDEX ON :User(category)")
            except Exception:
                pass
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000

    def bulk_insert_nodes(self, nodes: List[Dict[str, Any]], batch_size: int = 1000) -> Dict[str, Any]:
        t0 = time.perf_counter()
        total = len(nodes)
        
        query = """
        UNWIND $batch AS row
        CREATE (u:User {id: row.id, name: row.name, category: row.category})
        """
        
        for i in range(0, total, batch_size):
            batch = nodes[i : i + batch_size]
            self.graph.query(query, {"batch": batch})
            
        elapsed = time.perf_counter() - t0
        throughput = total / elapsed if elapsed > 0 else 0
        return {
            "total_nodes": total,
            "elapsed_sec": round(elapsed, 3),
            "throughput_nodes_sec": round(throughput, 1)
        }

    def bulk_insert_edges(self, edges: List[Dict[str, Any]], batch_size: int = 1000) -> Dict[str, Any]:
        t0 = time.perf_counter()
        total = len(edges)
        
        query = """
        UNWIND $batch AS row
        MATCH (src:User {id: row.source_id})
        MATCH (dst:User {id: row.target_id})
        CREATE (src)-[:FOLLOWS {weight: row.weight}]->(dst)
        """
        
        for i in range(0, total, batch_size):
            batch = edges[i : i + batch_size]
            self.graph.query(query, {"batch": batch})
            
        elapsed = time.perf_counter() - t0
        throughput = total / elapsed if elapsed > 0 else 0
        return {
            "total_edges": total,
            "elapsed_sec": round(elapsed, 3),
            "throughput_edges_sec": round(throughput, 1)
        }

    def point_lookup(self, node_id: int) -> Tuple[float, Optional[Dict[str, Any]]]:
        query = "MATCH (u:User {id: $id}) RETURN u.id, u.name, u.category LIMIT 1"
        t0 = time.perf_counter_ns()
        res = self.graph.query(query, {"id": node_id})
        t1 = time.perf_counter_ns()
        record = None
        if res.result_set:
            row = res.result_set[0]
            record = {"id": row[0], "name": row[1], "category": row[2]}
        return (t1 - t0) / 1_000_000, record

    def indexed_filter_lookup(self, category: str, limit: int = 50) -> Tuple[float, List[Dict[str, Any]]]:
        query = "MATCH (u:User {category: $cat}) RETURN u.id, u.name LIMIT $limit"
        t0 = time.perf_counter_ns()
        res = self.graph.query(query, {"cat": category, "limit": limit})
        t1 = time.perf_counter_ns()
        records = [{"id": r[0], "name": r[1]} for r in res.result_set] if res.result_set else []
        return (t1 - t0) / 1_000_000, records

    def traverse_1_hop(self, node_id: int) -> Tuple[float, int]:
        query = "MATCH (u:User {id: $id})-[:FOLLOWS]->(n) RETURN count(n)"
        t0 = time.perf_counter_ns()
        res = self.graph.query(query, {"id": node_id})
        t1 = time.perf_counter_ns()
        cnt = res.result_set[0][0] if res.result_set else 0
        return (t1 - t0) / 1_000_000, cnt

    def traverse_2_hop(self, node_id: int) -> Tuple[float, int]:
        query = "MATCH (u:User {id: $id})-[:FOLLOWS]->()-[:FOLLOWS]->(n) RETURN count(DISTINCT n)"
        t0 = time.perf_counter_ns()
        res = self.graph.query(query, {"id": node_id})
        t1 = time.perf_counter_ns()
        cnt = res.result_set[0][0] if res.result_set else 0
        return (t1 - t0) / 1_000_000, cnt

    def traverse_3_hop(self, node_id: int) -> Tuple[float, int]:
        query = "MATCH (u:User {id: $id})-[:FOLLOWS]->()-[:FOLLOWS]->()-[:FOLLOWS]->(n) RETURN count(DISTINCT n)"
        t0 = time.perf_counter_ns()
        res = self.graph.query(query, {"id": node_id})
        t1 = time.perf_counter_ns()
        cnt = res.result_set[0][0] if res.result_set else 0
        return (t1 - t0) / 1_000_000, cnt

    def aggregate_degree_distribution(self, limit: int = 10) -> Tuple[float, List[Dict[str, Any]]]:
        query = """
        MATCH (u:User)-[:FOLLOWS]->(n)
        RETURN u.id, count(n) AS degree
        ORDER BY degree DESC
        LIMIT $limit
        """
        t0 = time.perf_counter_ns()
        res = self.graph.query(query, {"limit": limit})
        t1 = time.perf_counter_ns()
        records = [{"user_id": r[0], "degree": r[1]} for r in res.result_set] if res.result_set else []
        return (t1 - t0) / 1_000_000, records

    def execute_mixed_transaction(self, read_id: int, write_node: Dict[str, Any]) -> Tuple[float, bool]:
        read_q = "MATCH (u:User {id: $id}) RETURN u.id LIMIT 1"
        write_q = "CREATE (u:User {id: $id, name: $name, category: $category})"
        
        t0 = time.perf_counter_ns()
        try:
            self.graph.query(read_q, {"id": read_id})
            self.graph.query(write_q, write_node)
            t1 = time.perf_counter_ns()
            return (t1 - t0) / 1_000_000, True
        except Exception:
            t1 = time.perf_counter_ns()
            return (t1 - t0) / 1_000_000, False

    def get_footprint(self) -> Dict[str, Any]:
        return {"engine": "FalkorDB GraphBLAS", "memory_usage": "sparse matrix representation", "disk_footprint": "in-memory with disk snapshot"}
