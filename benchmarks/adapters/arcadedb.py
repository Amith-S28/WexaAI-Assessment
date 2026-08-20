"""
ArcadeDB Adapter.
Implements BaseGraphAdapter for ArcadeDB Multi-Model Graph Engine via its HTTP / openCypher API.
"""

import time
import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, List, Tuple, Any, Optional
from .base import BaseGraphAdapter

class ArcadeDBAdapter(BaseGraphAdapter):
    """Adapter for ArcadeDB multi-model graph engine."""
    
    def __init__(self, url: str = "http://localhost:2480", user: str = "root", password: str = "benchmarkpassword", database: str = "benchmark"):
        super().__init__(
            name="ArcadeDB",
            db_type="ArcadeDB (Multi-Model)",
            paradigm="Multi-Model Document + Graph Engine (openCypher / HTTP)"
        )
        self.url = url.rstrip("/")
        self.user = user
        self.password = password
        self.database = database
        self.auth = HTTPBasicAuth(user, password)
        self.session = requests.Session()

    def _command(self, query: str, language: str = "cypher", timeout: int = 30) -> Dict[str, Any]:
        cmd_url = f"{self.url}/api/v1/command/{self.database}"
        payload = {"language": language, "command": query}
        resp = self.session.post(cmd_url, auth=self.auth, json=payload, timeout=timeout)
        if resp.status_code != 200:
            raise RuntimeError(f"ArcadeDB Command Error ({resp.status_code}): {resp.text}")
        return resp.json()

    def _query(self, query: str, language: str = "cypher", timeout: int = 30) -> Dict[str, Any]:
        query_url = f"{self.url}/api/v1/query/{self.database}"
        payload = {"language": language, "command": query}
        resp = self.session.post(query_url, auth=self.auth, json=payload, timeout=timeout)
        if resp.status_code != 200:
            raise RuntimeError(f"ArcadeDB Query Error ({resp.status_code}): {resp.text}")
        return resp.json()

    def connect(self) -> bool:
        for attempt in range(1, 6):
            try:
                # Ensure database exists
                server_url = f"{self.url}/api/v1/server"
                try:
                    self.session.post(server_url, auth=self.auth, json={"command": f"create database {self.database}"}, timeout=5)
                except Exception:
                    pass
                self.ping_rtt()
                self.is_connected = True
                return True
            except Exception as e:
                time.sleep(1.5 * attempt)
        self.is_connected = False
        raise ConnectionError(f"[ArcadeDB] Failed to connect to {self.url}")

    def close(self) -> None:
        self.session.close()
        self.is_connected = False

    def ping_rtt(self) -> float:
        t0 = time.perf_counter_ns()
        self._query("RETURN 1 AS ping")
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000

    def reset_database(self) -> bool:
        try:
            self._command("DELETE FROM User", language="sql")
        except Exception:
            pass
        try:
            self._command("DELETE FROM FOLLOWS", language="sql")
        except Exception:
            pass
        return True

    def create_schema_and_indexes(self) -> float:
        t0 = time.perf_counter_ns()
        self.reset_database()
        try:
            self._command("CREATE VERTEX TYPE User IF NOT EXISTS", language="sql")
            self._command("CREATE PROPERTY User.id IF NOT EXISTS INTEGER", language="sql")
            self._command("CREATE PROPERTY User.name IF NOT EXISTS STRING", language="sql")
            self._command("CREATE PROPERTY User.category IF NOT EXISTS STRING", language="sql")
            self._command("CREATE INDEX ON User(id) UNIQUE IF NOT EXISTS", language="sql")
            self._command("CREATE INDEX ON User(category) NOTUNIQUE IF NOT EXISTS", language="sql")
            self._command("CREATE EDGE TYPE FOLLOWS IF NOT EXISTS", language="sql")
        except Exception:
            pass
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000

    def bulk_insert_nodes(self, nodes: List[Dict[str, Any]], batch_size: int = 1000) -> Dict[str, Any]:
        import json
        t0 = time.perf_counter()
        total = len(nodes)
        
        for i in range(0, total, batch_size):
            batch = nodes[i : i + batch_size]
            json_str = json.dumps(batch)
            cmd = f"INSERT INTO User CONTENT {json_str}"
            self._command(cmd, language="sql", timeout=60)
            
        elapsed = time.perf_counter() - t0
        throughput = total / elapsed if elapsed > 0 else 0
        return {
            "total_nodes": total,
            "elapsed_sec": round(elapsed, 3),
            "throughput_nodes_sec": round(throughput, 1)
        }

    def bulk_insert_edges(self, edges: List[Dict[str, Any]], batch_size: int = 200) -> Dict[str, Any]:
        t0 = time.perf_counter()
        total = len(edges)
        
        for i in range(0, total, batch_size):
            batch = edges[i : i + batch_size]
            script_lines = []
            for e in batch:
                script_lines.append(f"CREATE EDGE FOLLOWS FROM (SELECT FROM User WHERE id = {e['source_id']}) TO (SELECT FROM User WHERE id = {e['target_id']}) SET weight = {e['weight']}")
            full_script = ";\n".join(script_lines)
            self._command(full_script, language="sqlscript", timeout=60)
            
        elapsed = time.perf_counter() - t0
        throughput = total / elapsed if elapsed > 0 else 0
        return {
            "total_edges": total,
            "elapsed_sec": round(elapsed, 3),
            "throughput_edges_sec": round(throughput, 1)
        }

    def point_lookup(self, node_id: int) -> Tuple[float, Optional[Dict[str, Any]]]:
        query = f"MATCH (u:User {{id: {node_id}}}) RETURN u.id AS id, u.name AS name, u.category AS category LIMIT 1"
        t0 = time.perf_counter_ns()
        res = self._query(query)
        t1 = time.perf_counter_ns()
        result_list = res.get("result", [])
        record = result_list[0] if result_list else None
        return (t1 - t0) / 1_000_000, record

    def indexed_filter_lookup(self, category: str, limit: int = 50) -> Tuple[float, List[Dict[str, Any]]]:
        query = f"MATCH (u:User {{category: '{category}'}}) RETURN u.id AS id, u.name AS name LIMIT {limit}"
        t0 = time.perf_counter_ns()
        res = self._query(query)
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000, res.get("result", [])

    def traverse_1_hop(self, node_id: int) -> Tuple[float, int]:
        query = f"MATCH (u:User {{id: {node_id}}})-[:FOLLOWS]->(n) RETURN count(n) AS cnt"
        t0 = time.perf_counter_ns()
        res = self._query(query)
        t1 = time.perf_counter_ns()
        result_list = res.get("result", [])
        cnt = result_list[0].get("cnt", 0) if result_list else 0
        return (t1 - t0) / 1_000_000, cnt

    def traverse_2_hop(self, node_id: int) -> Tuple[float, int]:
        query = f"MATCH (u:User {{id: {node_id}}})-[:FOLLOWS]->()-[:FOLLOWS]->(n) RETURN count(DISTINCT n) AS cnt"
        t0 = time.perf_counter_ns()
        res = self._query(query)
        t1 = time.perf_counter_ns()
        result_list = res.get("result", [])
        cnt = result_list[0].get("cnt", 0) if result_list else 0
        return (t1 - t0) / 1_000_000, cnt

    def traverse_3_hop(self, node_id: int) -> Tuple[float, int]:
        query = f"MATCH (u:User {{id: {node_id}}})-[:FOLLOWS]->()-[:FOLLOWS]->()-[:FOLLOWS]->(n) RETURN count(DISTINCT n) AS cnt"
        t0 = time.perf_counter_ns()
        res = self._query(query)
        t1 = time.perf_counter_ns()
        result_list = res.get("result", [])
        cnt = result_list[0].get("cnt", 0) if result_list else 0
        return (t1 - t0) / 1_000_000, cnt

    def aggregate_degree_distribution(self, limit: int = 10) -> Tuple[float, List[Dict[str, Any]]]:
        query = f"""
        MATCH (u:User)-[:FOLLOWS]->(n)
        RETURN u.id AS user_id, count(n) AS degree
        ORDER BY degree DESC
        LIMIT {limit}
        """
        t0 = time.perf_counter_ns()
        res = self._query(query)
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000, res.get("result", [])

    def execute_mixed_transaction(self, read_id: int, write_node: Dict[str, Any]) -> Tuple[float, bool]:
        read_q = f"MATCH (u:User {{id: {read_id}}}) RETURN u.id LIMIT 1"
        name_esc = write_node['name'].replace("'", "\\'")
        cat_esc = write_node['category'].replace("'", "\\'")
        write_q = f"CREATE (:User {{id: {write_node['id']}, name: '{name_esc}', category: '{cat_esc}'}})"
        
        t0 = time.perf_counter_ns()
        try:
            self._query(read_q)
            self._command(write_q)
            t1 = time.perf_counter_ns()
            return (t1 - t0) / 1_000_000, True
        except Exception:
            t1 = time.perf_counter_ns()
            return (t1 - t0) / 1_000_000, False

    def get_footprint(self) -> Dict[str, Any]:
        return {"engine": "ArcadeDB", "memory_usage": "Capped 512MB RAM", "disk_footprint": "Document + Edge LSM"}
