"""
Bolt-based Base Adapter for Cypher-compatible graph databases:
- CognoDB Cloud (bolt+s://)
- Neo4j AuraDB (neo4j+s://)
- Memgraph Cloud (bolt+ssc://)
"""

import time
from typing import Dict, List, Tuple, Any, Optional
from neo4j import GraphDatabase, Driver
from .base import BaseGraphAdapter

class BoltGraphAdapter(BaseGraphAdapter):
    """Unified Cypher + Bolt Protocol Adapter with robust connection pooling."""
    
    def __init__(self, name: str, db_type: str, paradigm: str, uri: str, user: str, password: str):
        super().__init__(name, db_type, paradigm)
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Optional[Driver] = None
        
    def connect(self) -> bool:
        auth = (self.user, self.password) if self.user else None
        last_err = None
        for attempt in range(1, 4):
            try:
                self.driver = GraphDatabase.driver(
                    self.uri,
                    auth=auth,
                    max_connection_lifetime=3600,
                    max_connection_pool_size=100,
                    connection_acquisition_timeout=60.0,
                    connection_timeout=30.0,
                    keep_alive=True
                )
                # Verify connectivity
                self.ping_rtt()
                self.is_connected = True
                return True
            except Exception as e:
                last_err = e
                time.sleep(1.0 * attempt)
        self.is_connected = False
        raise ConnectionError(f"[{self.name}] Failed to connect to {self.uri} after 3 attempts: {last_err}")

    def close(self) -> None:
        if self.driver:
            self.driver.close()
            self.is_connected = False

    def ping_rtt(self) -> float:
        t0 = time.perf_counter_ns()
        with self.driver.session() as session:
            session.run("RETURN 1 AS ping").consume()
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000

    def reset_database(self) -> bool:
        """Drop existing nodes and relationships in batches to prevent memory OOM."""
        with self.driver.session() as session:
            while True:
                res = session.run("MATCH (n) WITH n LIMIT 5000 DETACH DELETE n RETURN count(n) AS deleted").single()
                if not res or res["deleted"] == 0:
                    break
        return True

    def create_schema_and_indexes(self) -> float:
        t0 = time.perf_counter_ns()
        with self.driver.session() as session:
            try:
                session.run("CREATE INDEX user_id_idx IF NOT EXISTS FOR (u:User) ON (u.id)").consume()
            except Exception:
                try:
                    session.run("CREATE INDEX ON :User(id)").consume()
                except Exception:
                    pass
            try:
                session.run("CREATE INDEX user_cat_idx IF NOT EXISTS FOR (u:User) ON (u.category)").consume()
            except Exception:
                try:
                    session.run("CREATE INDEX ON :User(category)").consume()
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
        
        with self.driver.session() as session:
            for i in range(0, total, batch_size):
                batch = nodes[i : i + batch_size]
                session.run(query, batch=batch)
                
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
        
        with self.driver.session() as session:
            for i in range(0, total, batch_size):
                batch = edges[i : i + batch_size]
                session.run(query, batch=batch)
                
        elapsed = time.perf_counter() - t0
        throughput = total / elapsed if elapsed > 0 else 0
        return {
            "total_edges": total,
            "elapsed_sec": round(elapsed, 3),
            "throughput_edges_sec": round(throughput, 1)
        }

    def point_lookup(self, node_id: int) -> Tuple[float, Optional[Dict[str, Any]]]:
        query = "MATCH (u:User {id: $id}) RETURN u.id AS id, u.name AS name, u.category AS category LIMIT 1"
        t0 = time.perf_counter_ns()
        with self.driver.session() as session:
            res = session.run(query, id=node_id).single()
            record = dict(res) if res else None
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000, record

    def indexed_filter_lookup(self, category: str, limit: int = 50) -> Tuple[float, List[Dict[str, Any]]]:
        query = "MATCH (u:User {category: $cat}) RETURN u.id AS id, u.name AS name LIMIT $limit"
        t0 = time.perf_counter_ns()
        with self.driver.session() as session:
            res = session.run(query, cat=category, limit=limit)
            records = [dict(r) for r in res]
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000, records

    def traverse_1_hop(self, node_id: int) -> Tuple[float, int]:
        query = "MATCH (u:User {id: $id})-[:FOLLOWS]->(n) RETURN count(n) AS cnt"
        t0 = time.perf_counter_ns()
        with self.driver.session() as session:
            res = session.run(query, id=node_id).single()
            cnt = res["cnt"] if res else 0
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000, cnt

    def traverse_2_hop(self, node_id: int) -> Tuple[float, int]:
        query = "MATCH (u:User {id: $id})-[:FOLLOWS]->()-[:FOLLOWS]->(n) RETURN count(DISTINCT n) AS cnt"
        t0 = time.perf_counter_ns()
        with self.driver.session() as session:
            res = session.run(query, id=node_id).single()
            cnt = res["cnt"] if res else 0
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000, cnt

    def traverse_3_hop(self, node_id: int) -> Tuple[float, int]:
        query = "MATCH (u:User {id: $id})-[:FOLLOWS]->()-[:FOLLOWS]->()-[:FOLLOWS]->(n) RETURN count(DISTINCT n) AS cnt"
        t0 = time.perf_counter_ns()
        with self.driver.session() as session:
            res = session.run(query, id=node_id).single()
            cnt = res["cnt"] if res else 0
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000, cnt

    def aggregate_degree_distribution(self, limit: int = 10) -> Tuple[float, List[Dict[str, Any]]]:
        query = """
        MATCH (u:User)-[:FOLLOWS]->(n)
        RETURN u.id AS user_id, count(n) AS degree
        ORDER BY degree DESC
        LIMIT $limit
        """
        t0 = time.perf_counter_ns()
        with self.driver.session() as session:
            res = session.run(query, limit=limit)
            records = [dict(r) for r in res]
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000, records

    def execute_mixed_transaction(self, read_id: int, write_node: Dict[str, Any]) -> Tuple[float, bool]:
        """Atomic read-then-write query."""
        read_q = "MATCH (u:User {id: $id}) RETURN u.id LIMIT 1"
        write_q = "CREATE (u:User {id: $id, name: $name, category: $category})"
        
        t0 = time.perf_counter_ns()
        try:
            with self.driver.session() as session:
                with session.begin_transaction() as tx:
                    tx.run(read_q, id=read_id).consume()
                    tx.run(write_q, **write_node).consume()
                    tx.commit()
            t1 = time.perf_counter_ns()
            return (t1 - t0) / 1_000_000, True
        except Exception:
            t1 = time.perf_counter_ns()
            return (t1 - t0) / 1_000_000, False

    def get_footprint(self) -> Dict[str, Any]:
        """Inspect storage where platform exposes it."""
        try:
            with self.driver.session() as session:
                res = session.run("CALL dbms.components() YIELD name, versions, edition RETURN name, versions, edition").single()
                if res:
                    return {"engine": res["name"], "version": res["versions"], "edition": res["edition"]}
        except Exception:
            pass
        return {"engine": self.name, "memory_usage": "not observable (cloud managed)", "disk_footprint": "not observable"}
