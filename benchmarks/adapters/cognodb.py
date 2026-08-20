"""
CognoDB Cloud Adapter.
Implements BoltGraphAdapter for Wexa AI's CognoDB Cloud platform.
"""

from .bolt_base import BoltGraphAdapter

class CognoDBAdapter(BoltGraphAdapter):
    """Adapter for CognoDB Cloud managed graph database."""
    
    def __init__(self, uri: str, user: str = "cognodb", password: str = ""):
        super().__init__(
            name="CognoDB Cloud",
            db_type="CognoDB (c0)",
            paradigm="Cloud Managed Native Graph (Bolt Protocol)",
            uri=uri,
            user=user,
            password=password
        )
