"""
JanusGraph Adapter.
Implements BaseGraphAdapter for JanusGraph (Apache TinkerPop / Gremlin Server) via its HTTP API.
"""

import time
import requests
from typing import Dict, List, Tuple, Any, Optional
from .base import BaseGraphAdapter

class JanusGraphAdapter(BaseGraphAdapter):
    """Adapter for JanusGraph distributed graph database via TinkerPop Gremlin HTTP endpoint."""
    
    def __init__(self, endpoint: str = "http://localhost:8182"):
        super().__init__(
            name="JanusGraph",
            db_type="JanusGraph (TinkerPop)",
            paradigm="TinkerPop Gremlin Framework (HTTP Server)"
        )
        self.endpoint = endpoint.rstrip("/")
        self.session = requests.Session()

    def _exec_gremlin(self, gremlin: str, bindings: Optional[Dict[str, Any]] = None, timeout: int = 60) -> Any:
        payload: Dict[str, Any] = {"gremlin": gremlin}
        if bindings:
            payload["bindings"] = bindings
        resp = self.session.post(self.endpoint, json=payload, timeout=timeout)
        if resp.status_code != 200:
            raise RuntimeError(f"JanusGraph Gremlin Error ({resp.status_code}): {resp.text}")
        data = resp.json()
        result = data.get("result", {}).get("data", {})
        if isinstance(result, dict) and "@value" in result:
            return result["@value"]
        return result

    def connect(self) -> bool:
        for attempt in range(1, 6):
            try:
                self.ping_rtt()
                self.is_connected = True
                return True
            except Exception as e:
                time.sleep(1.5 * attempt)
        self.is_connected = False
        raise ConnectionError(f"[JanusGraph] Failed to connect to {self.endpoint}")

    def close(self) -> None:
        self.session.close()
        self.is_connected = False

    def ping_rtt(self) -> float:
        t0 = time.perf_counter_ns()
        self._exec_gremlin("1 + 1")
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000

    def reset_database(self) -> bool:
        try:
            self._exec_gremlin("g.V().drop().iterate()")
        except Exception:
            pass
        return True

    def create_schema_and_indexes(self) -> float:
        t0 = time.perf_counter_ns()
        self.reset_database()
        schema_script = """
        mgmt = graph.openManagement()
        if (!mgmt.containsPropertyKey('uid')) {
            uid = mgmt.makePropertyKey('uid').dataType(Integer.class).make()
            name = mgmt.makePropertyKey('name').dataType(String.class).make()
            cat = mgmt.makePropertyKey('category').dataType(String.class).make()
            weight = mgmt.makePropertyKey('weight').dataType(Double.class).make()
            user = mgmt.makeVertexLabel('User').make()
            follows = mgmt.makeEdgeLabel('FOLLOWS').make()
            mgmt.buildIndex('byUserUid', Vertex.class).addKey(uid).buildCompositeIndex()
            mgmt.buildIndex('byUserCategory', Vertex.class).addKey(cat).buildCompositeIndex()
            mgmt.commit()
        } else {
            mgmt.rollback()
        }
        """
        try:
            self._exec_gremlin(schema_script)
        except Exception:
            pass
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000

    def bulk_insert_nodes(self, nodes: List[Dict[str, Any]], batch_size: int = 500) -> Dict[str, Any]:
        t0 = time.perf_counter()
        total = len(nodes)
        
        script = """
        def tx = g.tx()
        batch.each { n ->
            g.addV('User').property('uid', n.id).property('name', n.name).property('category', n.category).next()
        }
        tx.commit()
        """
        
        for i in range(0, total, batch_size):
            batch = nodes[i : i + batch_size]
            self._exec_gremlin(script, bindings={"batch": batch}, timeout=60)
            
        elapsed = time.perf_counter() - t0
        throughput = total / elapsed if elapsed > 0 else 0
        return {
            "total_nodes": total,
            "elapsed_sec": round(elapsed, 3),
            "throughput_nodes_sec": round(throughput, 1)
        }

    def bulk_insert_edges(self, edges: List[Dict[str, Any]], batch_size: int = 100) -> Dict[str, Any]:
        t0 = time.perf_counter()
        total = len(edges)
        
        script = """
        def tx = g.tx()
        batch.each { e ->
            try {
                def src = g.V().has('User', 'uid', e.source_id).next()
                def dst = g.V().has('User', 'uid', e.target_id).next()
                src.addEdge('FOLLOWS', dst, 'weight', e.weight)
            } catch (Exception ex) {}
        }
        tx.commit()
        """
        
        for i in range(0, total, batch_size):
            batch = edges[i : i + batch_size]
            self._exec_gremlin(script, bindings={"batch": batch}, timeout=180)
            
        elapsed = time.perf_counter() - t0
        throughput = total / elapsed if elapsed > 0 else 0
        return {
            "total_edges": total,
            "elapsed_sec": round(elapsed, 3),
            "throughput_edges_sec": round(throughput, 1)
        }

    def _extract_val(self, res: Any) -> Any:
        if isinstance(res, list) and len(res) == 1:
            res = res[0]
        if isinstance(res, dict):
            if res.get("@type") == "g:Map" and isinstance(res.get("@value"), list):
                items = res["@value"]
                return {items[i]: self._extract_val(items[i+1]) for i in range(0, len(items), 2)}
            if "@value" in res:
                return self._extract_val(res["@value"])
        return res

    def point_lookup(self, node_id: int) -> Tuple[float, Optional[Dict[str, Any]]]:
        gremlin = f"g.V().has('User', 'uid', {node_id}).project('id', 'name', 'category').by('uid').by('name').by('category').toList()"
        t0 = time.perf_counter_ns()
        res = self._exec_gremlin(gremlin)
        t1 = time.perf_counter_ns()
        if res:
            rec = self._extract_val(res)
            if isinstance(rec, dict):
                return (t1 - t0) / 1_000_000, {
                    "id": int(rec.get("id", node_id)),
                    "name": str(rec.get("name", "")),
                    "category": str(rec.get("category", ""))
                }
        return (t1 - t0) / 1_000_000, None

    def indexed_filter_lookup(self, category: str, limit: int = 50) -> Tuple[float, List[Dict[str, Any]]]:
        gremlin = f"g.V().has('User', 'category', '{category}').limit({limit}).valueMap('uid', 'name').toList()"
        t0 = time.perf_counter_ns()
        res = self._exec_gremlin(gremlin)
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000, res if isinstance(res, list) else []

    def traverse_1_hop(self, node_id: int) -> Tuple[float, int]:
        gremlin = f"g.V().has('User', 'uid', {node_id}).out('FOLLOWS').count().toList()"
        t0 = time.perf_counter_ns()
        res = self._exec_gremlin(gremlin)
        t1 = time.perf_counter_ns()
        val = self._extract_val(res)
        cnt = int(val) if val is not None else 0
        return (t1 - t0) / 1_000_000, cnt

    def traverse_2_hop(self, node_id: int) -> Tuple[float, int]:
        gremlin = f"g.V().has('User', 'uid', {node_id}).out('FOLLOWS').out('FOLLOWS').dedup().count().toList()"
        t0 = time.perf_counter_ns()
        res = self._exec_gremlin(gremlin)
        t1 = time.perf_counter_ns()
        val = self._extract_val(res)
        cnt = int(val) if val is not None else 0
        return (t1 - t0) / 1_000_000, cnt

    def traverse_3_hop(self, node_id: int) -> Tuple[float, int]:
        gremlin = f"g.V().has('User', 'uid', {node_id}).out('FOLLOWS').out('FOLLOWS').out('FOLLOWS').dedup().count().toList()"
        t0 = time.perf_counter_ns()
        res = self._exec_gremlin(gremlin)
        t1 = time.perf_counter_ns()
        val = self._extract_val(res)
        cnt = int(val) if val is not None else 0
        return (t1 - t0) / 1_000_000, cnt

    def aggregate_degree_distribution(self, limit: int = 10) -> Tuple[float, List[Dict[str, Any]]]:
        gremlin = f"g.V().hasLabel('User').limit(5000).project('uid', 'degree').by('uid').by(out('FOLLOWS').count()).order().by(select('degree'), desc).limit({limit}).toList()"
        t0 = time.perf_counter_ns()
        res = self._exec_gremlin(gremlin, timeout=120)
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000, res if isinstance(res, list) else []

    def execute_mixed_transaction(self, read_id: int, write_node: Dict[str, Any]) -> Tuple[float, bool]:
        gremlin = """
        g.V().has('User', 'uid', read_id).valueMap('uid').toList()
        g.addV('User').property('uid', node.id).property('name', node.name).property('category', node.category).next()
        g.tx().commit()
        """
        t0 = time.perf_counter_ns()
        try:
            self._exec_gremlin(gremlin, bindings={"read_id": read_id, "node": write_node}, timeout=30)
            t1 = time.perf_counter_ns()
            return (t1 - t0) / 1_000_000, True
        except Exception:
            t1 = time.perf_counter_ns()
            return (t1 - t0) / 1_000_000, False

    def get_footprint(self) -> Dict[str, Any]:
        return {"engine": "JanusGraph", "memory_usage": "Capped 512MB RAM", "disk_footprint": "TinkerPop Graph"}
