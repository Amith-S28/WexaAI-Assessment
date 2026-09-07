"""
Neo4j AuraDB Adapter.
Implements BoltGraphAdapter for Neo4j AuraDB Cloud.
"""

from .bolt_base import BoltGraphAdapter

class Neo4jAdapter(BoltGraphAdapter):
    """Adapter for Neo4j AuraDB Free / Professional Cloud instance."""
    
    def __init__(self, uri: str, user: str = "neo4j", password: str = ""):
        super().__init__(
            name="Neo4j AuraDB",
            db_type="Neo4j Aura",
            paradigm="JVM Labeled Property Graph (LPG)",
            uri=uri,
            user=user,
            password=password
        )
