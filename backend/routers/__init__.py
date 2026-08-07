"""
Routers Package
===============
REST & WebSocket API Controllers.

Available routers:
    - auth: Authentication endpoints
    - security: Security assessment endpoints
    - zola: Threat prediction endpoints
    - axiom: Engine diagnostics endpoints
    - entities: Asset management endpoints
    - chat: AI assistant endpoints
    - and 12+ more...
"""

from .auth import router as auth_router
from .security import router as security_router
from .zola import router as zola_router
from .axiom import router as axiom_router
from .entities import router as entities_router
from .chat import router as chat_router
from .dashboard import router as dashboard_router
from .health import router as health_router
from .stream import router as stream_router
from .dark_intel import router as dark_intel_router
from .citation import router as citation_router
from .graph import router as graph_router
from .semantic import router as semantic_router
from .insights import router as insights_router
from .executive import router as executive_router
from .healthcare import router as healthcare_router
from .censys import router as censys_router
from .omniscience import router as omniscience_router

__all__ = [
    'auth_router',
    'security_router',
    'zola_router',
    'axiom_router',
    'entities_router',
    'chat_router',
    'dashboard_router',
    'health_router',
    'stream_router',
    'dark_intel_router',
    'citation_router',
    'graph_router',
    'semantic_router',
    'insights_router',
    'executive_router',
    'healthcare_router',
    'censys_router',
    'omniscience_router',
]