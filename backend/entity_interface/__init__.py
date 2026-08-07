"""
Entity Interface Package
========================
Core AI/ML interfaces for the SERA platform.

This package provides:
- LiveEntity: Production entity AI with real neural networks (CIFN, KRONOS, DRSN, CSIE, APEX)
- MockEntity: Development/testing entity AI with mock responses
- SignalSynthesizer: Synthetic signal generation for entities
- APEXCausalEngine: Causal graph reasoning and inference
- CSIESheafLayer: Concept grounding and sheaf-based reasoning
- DRSNNetwork: Dynamic Recurrent Spiking Neural Network
- AXIOMCompressor: Lossless model compression

Submodules:
    kronos/     - KRONOS neural scaling engine (9-pillar transformer)
    axiom/      - AXIOM compression modules (gauge fixing, null space, TT decomposition)
    noether/    - NOETHER extension (13-component unified model, optional)
"""

from .base import EntityInterface
from .live_entity import LiveEntity
from .mock_entity import MockEntity
from .signal_synthesizer import SignalSynthesizer
from .apex_causal import APEXCausalEngine, CausalObject, KMorphism
from .csie_sheaf import CSIESheafLayer
from .drsn_node import DRSNNetwork
from .axiom_compression import analyse_kronos_model, compress_kronos_model

# Optional: Import NOETHER if available
try:
    from .noether.noether_kronos import NOETHER_KRONOS
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
        'NOETHER_KRONOS',
    ]
except ImportError:
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

# Package metadata
__version__ = '1.0.0'
__author__ = 'SERA Platform'
__description__ = 'Entity AI Interface for behavioral intelligence'

# Convenience function to get the appropriate entity interface
def get_entity_interface(mode: str = 'live', **kwargs):
    """
    Factory function to get the appropriate entity interface.
    
    Args:
        mode: 'live' or 'mock'
        **kwargs: Additional arguments to pass to the constructor
    
    Returns:
        EntityInterface instance
    
    Examples:
        >>> from entity_interface import get_entity_interface
        >>> entity = get_entity_interface('mock')
        >>> prediction = await entity.predict('NVDA', {'entropy': 0.85})
    """
    if mode == 'live':
        return LiveEntity(**kwargs)
    else:
        return MockEntity(**kwargs)

# Log initialization
import logging
logger = logging.getLogger("sera.entity_interface")
logger.info(f"Entity Interface v{__version__} initialized")
logger.info(f"Available classes: {', '.join(__all__)}")