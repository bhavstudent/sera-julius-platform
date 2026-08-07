"""
NOETHER Invariance Subsystem
============================
Physics-based symmetry preservation.

Submodules:
    - noether_components: Physics conservation laws
    - noether_kronos: Unified Noether-Kronos model
    - functional_verification: Symmetry verification
    - functional_verification_extended: Extended audits
    - noether_demo: Demonstration runner
"""

from .noether_components import NoetherComponents
from .noether_kronos import NOETHER_KRONOS
from .functional_verification import verify_symmetries
from .functional_verification_extended import verify_extended_symmetries

__all__ = [
    'NoetherComponents',
    'NOETHER_KRONOS',
    'verify_symmetries',
    'verify_extended_symmetries',
]