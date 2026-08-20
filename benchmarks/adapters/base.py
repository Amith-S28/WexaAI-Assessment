"""
Base Graph Database Adapter Interface.
Defines the standard contract for all database adapters to ensure uniform benchmarking.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional
import time

class BaseGraphAdapter(ABC):
    """Abstract base class for all benchmarked graph database adapters."""
    
    def __init__(self, name: str, db_type: str, paradigm: str):
        self.name = name
        self.db_type = db_type
        self.paradigm = paradigm
        self.is_connected = False
        
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the database. Returns True if successful."""
        pass
        
    @abstractmethod
    def close(self) -> None:
        """Close connections and release driver resources."""
        pass

    @abstractmethod
    def reset_database(self) -> bool:
        """Clear existing benchmark data (nodes, edges, indexes) for a fresh run."""
        pass

    @abstractmethod
    def create_schema_and_indexes(self) -> float:
        """Create indexes on User.id and User.category. Returns elapsed time in ms."""
        pass

    @abstractmethod
    def bulk_insert_nodes(self, nodes: List[Dict[str, Any]], batch_size: int = 1000) -> Dict[str, Any]:
        """
        Ingest node records in batches.
        Returns dict with: total_nodes, elapsed_sec, throughput_nodes_sec
        """
        pass

    @abstractmethod
    def bulk_insert_edges(self, edges: List[Dict[str, Any]], batch_size: int = 1000) -> Dict[str, Any]:
        """
        Ingest edge records in batches.
        Returns dict with: total_edges, elapsed_sec, throughput_edges_sec
        """
        pass

    @abstractmethod
    def point_lookup(self, node_id: int) -> Tuple[float, Optional[Dict[str, Any]]]:
        """Lookup node by ID. Returns (latency_ms, record_dict)."""
        pass

    @abstractmethod
    def indexed_filter_lookup(self, category: str, limit: int = 50) -> Tuple[float, List[Dict[str, Any]]]:
        """Filter nodes by category. Returns (latency_ms, list_of_records)."""
        pass

    @abstractmethod
    def traverse_1_hop(self, node_id: int) -> Tuple[float, int]:
        """1-hop traversal (immediate neighbors). Returns (latency_ms, neighbor_count)."""
        pass

    @abstractmethod
    def traverse_2_hop(self, node_id: int) -> Tuple[float, int]:
        """2-hop traversal (distinct friends-of-friends). Returns (latency_ms, distinct_neighbor_count)."""
        pass

    @abstractmethod
    def traverse_3_hop(self, node_id: int) -> Tuple[float, int]:
        """3-hop traversal (distinct 3rd-degree neighbors). Returns (latency_ms, distinct_neighbor_count)."""
        pass

    @abstractmethod
    def aggregate_degree_distribution(self, limit: int = 10) -> Tuple[float, List[Dict[str, Any]]]:
        """Aggregate top-N nodes by out-degree. Returns (latency_ms, list_of_top_nodes)."""
        pass

    @abstractmethod
    def execute_mixed_transaction(self, read_id: int, write_node: Dict[str, Any]) -> Tuple[float, bool]:
        """Execute a mixed read/write transaction. Returns (latency_ms, success)."""
        pass

    @abstractmethod
    def ping_rtt(self) -> float:
        """Measure raw network RTT with a no-op RETURN 1 query. Returns latency_ms."""
        pass
        
    @abstractmethod
    def get_footprint(self) -> Dict[str, Any]:
        """Inspect storage/memory footprint where observable."""
        pass

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
