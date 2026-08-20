import time
import warnings
import urllib3
from typing import Dict, List, Tuple, Any, Optional
from arango import ArangoClient
from .base import BaseGraphAdapter

# Suppress unverified HTTPS warnings for cloud endpoints
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

class ArangoDBAdapter(BaseGraphAdapter):
    """Adapter for ArangoDB Oasis Cloud multi-model graph engine."""
    
    def __init__(self, url: str, user: str = "root", password: str = "", graph_name: str = "benchmark_graph"):
        super().__init__(
            name="ArangoDB Oasis",
            db_type="ArangoDB",
            paradigm="Multi-Model RocksDB (AQL Graph)"
        )
        self.url = url
        self.user = user
        self.password = password
        self.graph_name = graph_name
        self.client: Optional[ArangoClient] = None
        self.db = None
        self.users = None
        self.follows = None

    def connect(self) -> bool:
        try:
            self.client = ArangoClient(hosts=self.url, verify_override=False)
            self.db = self.client.db("_system", username=self.user, password=self.password)
            self._ensure_schema()
            self.ping_rtt()
            self.is_connected = True
            return True
        except Exception as e:
            self.is_connected = False
            raise ConnectionError(f"[{self.name}] Failed to connect to {self.url}: {e}")

    def _ensure_schema(self):
        if not self.db.has_collection("users"):
            self.users = self.db.create_collection("users")
        else:
            self.users = self.db.collection("users")
            
        if not self.db.has_collection("follows"):
            self.follows = self.db.create_collection("follows", edge=True)
        else:
            self.follows = self.db.collection("follows")

    def close(self) -> None:
        self.client = None
        self.db = None
        self.is_connected = False

    def ping_rtt(self) -> float:
        t0 = time.perf_counter_ns()
        self.db.aql.execute("RETURN 1")
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000

    def reset_database(self) -> bool:
        try:
            if self.db.has_collection("follows"):
                self.db.delete_collection("follows")
            if self.db.has_collection("users"):
                self.db.delete_collection("users")
            self._ensure_schema()
            return True
        except Exception:
            return False

    def create_schema_and_indexes(self) -> float:
        t0 = time.perf_counter_ns()
        try:
            self.users.add_persistent_index(fields=["id"], unique=False)
            self.users.add_persistent_index(fields=["category"], unique=False)
        except Exception:
            pass
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000

    def bulk_insert_nodes(self, nodes: List[Dict[str, Any]], batch_size: int = 1000) -> Dict[str, Any]:
        t0 = time.perf_counter()
        total = len(nodes)
        
        for i in range(0, total, batch_size):
            batch = nodes[i : i + batch_size]
            docs = [{"_key": str(n["id"]), "id": n["id"], "name": n["name"], "category": n["category"]} for n in batch]
            self.users.insert_many(docs, overwrite=True)
            
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
        
        for i in range(0, total, batch_size):
            batch = edges[i : i + batch_size]
            edge_docs = [
                {
                    "_from": f"users/{e['source_id']}",
                    "_to": f"users/{e['target_id']}",
                    "weight": e["weight"]
                }
                for e in batch
            ]
            self.follows.insert_many(edge_docs)
            
        elapsed = time.perf_counter() - t0
        throughput = total / elapsed if elapsed > 0 else 0
        return {
            "total_edges": total,
            "elapsed_sec": round(elapsed, 3),
            "throughput_edges_sec": round(throughput, 1)
        }

    def point_lookup(self, node_id: int) -> Tuple[float, Optional[Dict[str, Any]]]:
        aql = "FOR u IN users FILTER u.id == @id LIMIT 1 RETURN {id: u.id, name: u.name, category: u.category}"
        t0 = time.perf_counter_ns()
        cursor = self.db.aql.execute(aql, bind_vars={"id": node_id})
        record = cursor.next() if not cursor.empty() else None
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000, record

    def indexed_filter_lookup(self, category: str, limit: int = 50) -> Tuple[float, List[Dict[str, Any]]]:
        aql = "FOR u IN users FILTER u.category == @cat LIMIT @limit RETURN {id: u.id, name: u.name}"
        t0 = time.perf_counter_ns()
        cursor = self.db.aql.execute(aql, bind_vars={"cat": category, "limit": limit})
        records = [doc for doc in cursor]
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000, records

    def traverse_1_hop(self, node_id: int) -> Tuple[float, int]:
        aql = """
        WITH users
        FOR v IN 1..1 OUTBOUND CONCAT('users/', @id) follows
        COLLECT WITH COUNT INTO cnt
        RETURN cnt
        """
        t0 = time.perf_counter_ns()
        cursor = self.db.aql.execute(aql, bind_vars={"id": str(node_id)})
        cnt = cursor.next() if not cursor.empty() else 0
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000, cnt

    def traverse_2_hop(self, node_id: int) -> Tuple[float, int]:
        aql = """
        WITH users
        FOR v IN 2..2 OUTBOUND CONCAT('users/', @id) follows
        RETURN DISTINCT v._key
        """
        t0 = time.perf_counter_ns()
        cursor = self.db.aql.execute(aql, bind_vars={"id": str(node_id)})
        cnt = len([doc for doc in cursor])
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000, cnt

    def traverse_3_hop(self, node_id: int) -> Tuple[float, int]:
        aql = """
        WITH users
        FOR v IN 3..3 OUTBOUND CONCAT('users/', @id) follows
        RETURN DISTINCT v._key
        """
        t0 = time.perf_counter_ns()
        cursor = self.db.aql.execute(aql, bind_vars={"id": str(node_id)})
        cnt = len([doc for doc in cursor])
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000, cnt

    def aggregate_degree_distribution(self, limit: int = 10) -> Tuple[float, List[Dict[str, Any]]]:
        aql = """
        FOR e IN follows
        COLLECT src = e._from WITH COUNT INTO deg
        SORT deg DESC
        LIMIT @limit
        RETURN {user_id: src, degree: deg}
        """
        t0 = time.perf_counter_ns()
        cursor = self.db.aql.execute(aql, bind_vars={"limit": limit})
        records = [doc for doc in cursor]
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000, records

    def execute_mixed_transaction(self, read_id: int, write_node: Dict[str, Any]) -> Tuple[float, bool]:
        aql = """
        LET r = (FOR u IN users FILTER u.id == @read_id LIMIT 1 RETURN u.id)
        UPSERT { _key: @key }
        INSERT @write_doc
        UPDATE @write_doc
        IN users
        RETURN 1
        """
        t0 = time.perf_counter_ns()
        try:
            key_str = str(write_node["id"])
            write_doc = {
                "_key": key_str,
                "id": write_node["id"],
                "name": write_node["name"],
                "category": write_node["category"]
            }
            self.db.aql.execute(aql, bind_vars={"read_id": read_id, "key": key_str, "write_doc": write_doc})
            t1 = time.perf_counter_ns()
            return (t1 - t0) / 1_000_000, True
        except Exception:
            t1 = time.perf_counter_ns()
            return (t1 - t0) / 1_000_000, False

    def get_footprint(self) -> Dict[str, Any]:
        return {"engine": "ArangoDB RocksDB", "version": "3.12", "memory_usage": "RocksDB Block Cache", "disk_footprint": "RocksDB SSTables"}
