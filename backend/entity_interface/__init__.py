"""
Entity Interface Package
========================
Core AI/ML interfaces for the SERA platform.
"""

from .base import EntityInterface
from .mock_entity import MockEntity
from .signal_synthesizer import SignalSynthesizer

try:
    from .live_entity import LiveEntity
    from .apex_causal import APEXCausalEngine, CausalObject, KMorphism
    from .csie_sheaf import CSIESheafLayer
    from .drsn_node import DRSNNetwork
    from .axiom_compression import analyse_kronos_model, compress_kronos_model
    HAVE_TORCH = True
except ImportError:
    LiveEntity = MockEntity
    APEXCausalEngine = None
    CausalObject = None
    KMorphism = None
    CSIESheafLayer = None
    DRSNNetwork = None
    analyse_kronos_model = None
    compress_kronos_model = None
    HAVE_TORCH = False

__all__ = [
    'EntityInterface',
    'LiveEntity',
    'MockEntity',
    'SignalSynthesizer',
    'APEXCausalEngine',
    'CausalObject',
    'KMorphism',
    'CSIESheafLayer',
    'DRSNNetwork',
    'analyse_kronos_model',
    'compress_kronos_model',
]

__version__ = '1.0.0'
__author__ = 'SERA Platform'
__description__ = 'Entity AI Interface for behavioral intelligence'

def get_entity_interface(mode: str = 'live', **kwargs):
    if mode == 'live' and HAVE_TORCH:
        return LiveEntity(**kwargs)
    else:
        return MockEntity(**kwargs)

import logging
logger = logging.getLogger("sera.entity_interface")
logger.info(f"Entity Interface v{__version__} initialized (PyTorch: {HAVE_TORCH})")