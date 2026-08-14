"""
Routers Package - SERA Platform API Endpoints
"""
# Core Routers
from . import auth
from . import health
from . import dashboard
from . import entities
from . import graph
from . import semantic
from . import axiom
from . import zola
from . import chat
from . import stream
from . import intel
from . import insights
from . import citation
from . import healthcare
from . import executive
from . import security
from . import censys
from . import omniscience
from . import self_improvement
# Hacking Routers (graceful fallback)
try:
    from . import terminal
except ImportError:
    terminal = None
try:
    from . import darkweb
except ImportError:
    darkweb = None
try:
    from . import node_control
except ImportError:
    node_control = None
try:
    from . import exploit
except ImportError:
    exploit = None
try:
    from . import scanner
except ImportError:
    scanner = None
try:
    from . import intel_pipeline
except ImportError:
    intel_pipeline = None
try:
    from . import osint
except ImportError:
    osint = None
try:
    from . import intelligence
except ImportError:
    intelligence = None
try:
    from . import events
except ImportError:
    events = None
try:
    from . import network
except ImportError:
    network = None
try:
    from . import live
except ImportError:
    live = None
try:
    from . import lan
except ImportError:
    lan = None
try:
    from . import apex
except ImportError:
    apex = None
try:
    from . import causal_functor
except ImportError:
    causal_functor = None
try:
    from . import kronos
except ImportError:
    kronos = None
try:
    from . import stratum
except ImportError:
    stratum = None
try:
    from . import pantheon
except ImportError:
    pantheon = None
__all__ = [
    "auth", "health", "dashboard", "entities", "graph", "semantic",
    "axiom", "zola", "chat", "stream", "intel", "insights",
    "citation", "healthcare", "executive", "security", "censys",
    "omniscience", "self_improvement",
    "terminal", "darkweb", "node_control", "exploit", "scanner",
    "intel_pipeline", "osint", "intelligence", "events",
    "network", "live", "lan", "apex", "causal_functor",
    "kronos", "stratum", "pantheon"
]
