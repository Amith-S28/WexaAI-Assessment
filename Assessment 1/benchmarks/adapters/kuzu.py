"""
KùzuDB Adapter.
Implements BaseGraphAdapter for KùzuDB (In-Process / Columnar Graph Engine) via its HTTP / Cypher API.
"""

import time
import requests
from typing import Dict, List, Tuple, Any, Optional
from .base import BaseGraphAdapter

class KuzuDBAdapter(BaseGraphAdapter):
    """Adapter for KùzuDB columnar graph database engine."""
    
    def __init__(self, endpoint: str = "http://localhost:8000", paradigm: str = "Columnar In-Process / Microservice Graph Engine"):
        super().__init__(
            name="KùzuDB",
            db_type="KùzuDB (Columnar)",
            paradigm=paradigm
        )
        self.endpoint = endpoint.rstrip("/")
        self.cypher_url = f"{self.endpoint}/api/cypher"
        self.session = requests.Session()

    def _exec(self, query: str, timeout: int = 30) -> Dict[str, Any]:
        resp = self.session.post(self.cypher_url, json={"query": query}, timeout=timeout)
        if resp.status_code != 200:
            raise RuntimeError(f"KùzuDB Error ({resp.status_code}): {resp.text}")
        return resp.json()

    def connect(self) -> bool:
        for attempt in range(1, 6):
            try:
                self.ping_rtt()
                self.is_connected = True
                return True
            except Exception as e:
                time.sleep(1.5 * attempt)
        self.is_connected = False
        raise ConnectionError(f"[KùzuDB] Failed to connect to {self.endpoint}")

    def close(self) -> None:
        self.session.close()
        self.is_connected = False

    def ping_rtt(self) -> float:
        t0 = time.perf_counter_ns()
        self._exec("RETURN 1 AS ping")
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000

    def reset_database(self) -> bool:
        try:
            self._exec("DROP TABLE FOLLOWS;")
        except Exception:
            pass
        try:
            self._exec("DROP TABLE User;")
        except Exception:
            pass
        return True

    def create_schema_and_indexes(self) -> float:
        t0 = time.perf_counter_ns()
        self.reset_database()
        self._exec("CREATE NODE TABLE User(id INT64, name STRING, category STRING, PRIMARY KEY (id));")
        self._exec("CREATE REL TABLE FOLLOWS(FROM User TO User, weight DOUBLE);")
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000

    def bulk_insert_nodes(self, nodes: List[Dict[str, Any]], batch_size: int = 500) -> Dict[str, Any]:
        t0 = time.perf_counter()
        total = len(nodes)
        
        for i in range(0, total, batch_size):
            batch = nodes[i : i + batch_size]
            statements = []
            for n in batch:
                name_esc = n['name'].replace("'", "\\'")
                cat_esc = n['category'].replace("'", "\\'")
                statements.append(f"CREATE (:User {{id: {n['id']}, name: '{name_esc}', category: '{cat_esc}'}})")
            full_q = ";\n".join(statements) + ";"
            self._exec(full_q, timeout=60)
            
        elapsed = time.perf_counter() - t0
        throughput = total / elapsed if elapsed > 0 else 0
        return {
            "total_nodes": total,
            "elapsed_sec": round(elapsed, 3),
            "throughput_nodes_sec": round(throughput, 1)
        }

    def bulk_insert_edges(self, edges: List[Dict[str, Any]], batch_size: int = 500) -> Dict[str, Any]:
        t0 = time.perf_counter()
        total = len(edges)
        
        for i in range(0, total, batch_size):
            batch = edges[i : i + batch_size]
            statements = []
            for e in batch:
                statements.append(f"MATCH (src:User {{id: {e['source_id']}}}), (dst:User {{id: {e['target_id']}}}) CREATE (src)-[:FOLLOWS {{weight: {e['weight']}}}]->(dst)")
            full_q = ";\n".join(statements) + ";"
            self._exec(full_q, timeout=60)
            
        elapsed = time.perf_counter() - t0
        throughput = total / elapsed if elapsed > 0 else 0
        return {
            "total_edges": total,
            "elapsed_sec": round(elapsed, 3),
            "throughput_edges_sec": round(throughput, 1)
        }

    def point_lookup(self, node_id: int) -> Tuple[float, Optional[Dict[str, Any]]]:
        query = f"MATCH (u:User) WHERE u.id = {node_id} RETURN u.id AS id, u.name AS name, u.category AS category LIMIT 1;"
        t0 = time.perf_counter_ns()
        res = self._exec(query)
        t1 = time.perf_counter_ns()
        rows = res.get("rows", [])
        record = rows[0] if rows else None
        return (t1 - t0) / 1_000_000, record

    def indexed_filter_lookup(self, category: str, limit: int = 50) -> Tuple[float, List[Dict[str, Any]]]:
        query = f"MATCH (u:User) WHERE u.category = '{category}' RETURN u.id AS id, u.name AS name LIMIT {limit};"
        t0 = time.perf_counter_ns()
        res = self._exec(query)
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000, res.get("rows", [])

    def traverse_1_hop(self, node_id: int) -> Tuple[float, int]:
        query = f"MATCH (u:User)-[:FOLLOWS]->(n:User) WHERE u.id = {node_id} RETURN count(n) AS cnt;"
        t0 = time.perf_counter_ns()
        res = self._exec(query)
        t1 = time.perf_counter_ns()
        rows = res.get("rows", [])
        cnt = rows[0].get("cnt", 0) if rows else 0
        return (t1 - t0) / 1_000_000, cnt

    def traverse_2_hop(self, node_id: int) -> Tuple[float, int]:
        query = f"MATCH (u:User)-[:FOLLOWS]->(m:User)-[:FOLLOWS]->(n:User) WHERE u.id = {node_id} RETURN count(DISTINCT n) AS cnt;"
        t0 = time.perf_counter_ns()
        res = self._exec(query)
        t1 = time.perf_counter_ns()
        rows = res.get("rows", [])
        cnt = rows[0].get("cnt", 0) if rows else 0
        return (t1 - t0) / 1_000_000, cnt

    def traverse_3_hop(self, node_id: int) -> Tuple[float, int]:
        query = f"MATCH (u:User)-[:FOLLOWS]->(:User)-[:FOLLOWS]->(:User)-[:FOLLOWS]->(n:User) WHERE u.id = {node_id} RETURN count(DISTINCT n) AS cnt;"
        t0 = time.perf_counter_ns()
        res = self._exec(query)
        t1 = time.perf_counter_ns()
        rows = res.get("rows", [])
        cnt = rows[0].get("cnt", 0) if rows else 0
        return (t1 - t0) / 1_000_000, cnt

    def aggregate_degree_distribution(self, limit: int = 10) -> Tuple[float, List[Dict[str, Any]]]:
        query = f"""
        MATCH (u:User)-[:FOLLOWS]->(n:User)
        RETURN u.id AS user_id, count(n) AS degree
        ORDER BY degree DESC
        LIMIT {limit};
        """
        t0 = time.perf_counter_ns()
        res = self._exec(query)
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000, res.get("rows", [])

    def execute_mixed_transaction(self, read_id: int, write_node: Dict[str, Any]) -> Tuple[float, bool]:
        read_q = f"MATCH (u:User) WHERE u.id = {read_id} RETURN u.id LIMIT 1;"
        name_esc = write_node['name'].replace("'", "\\'")
        cat_esc = write_node['category'].replace("'", "\\'")
        write_q = f"CREATE (:User {{id: {write_node['id']}, name: '{name_esc}', category: '{cat_esc}'}});"
        
        t0 = time.perf_counter_ns()
        try:
            self._exec(read_q)
            self._exec(write_q)
            t1 = time.perf_counter_ns()
            return (t1 - t0) / 1_000_000, True
        except Exception:
            t1 = time.perf_counter_ns()
            return (t1 - t0) / 1_000_000, False

    def get_footprint(self) -> Dict[str, Any]:
        return {"engine": "KùzuDB", "memory_usage": "Capped 512MB RAM", "disk_footprint": "Columnar mmap"}
