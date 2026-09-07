"""
Memgraph Cloud Adapter.
Implements BoltGraphAdapter for Memgraph in-memory C++ graph database.
"""

from .bolt_base import BoltGraphAdapter

class MemgraphAdapter(BoltGraphAdapter):
    """Adapter for Memgraph Cloud in-memory instance."""
    
    def __init__(self, uri: str, user: str = "", password: str = ""):
        super().__init__(
            name="Memgraph Cloud",
            db_type="Memgraph",
            paradigm="In-Memory C++ Native Graph",
            uri=uri,
            user=user,
            password=password
        )
        
    def create_schema_and_indexes(self) -> float:
        """Memgraph specific index syntax."""
        import time
        t0 = time.perf_counter_ns()
        with self.driver.session() as session:
            try:
                session.run("CREATE INDEX ON :User(id)")
            except Exception:
                pass
            try:
                session.run("CREATE INDEX ON :User(category)")
            except Exception:
                pass
        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1_000_000
