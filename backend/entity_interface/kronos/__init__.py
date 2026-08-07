"""
KRONOS Neural Engine
====================
Kronecker-based neural architecture scaling.

Submodules:
    - kronos_architecture: Base KRONOS model
    - kronecker_scaler: Tensor scaling
    - orchestrator: Model orchestration
    - kronos_training: Training logic
    - depth_injector: Dynamic depth
    - curriculum: Adaptive training
    - gradient_rank_monitor: Gradient monitoring
    - fractal_generator: Fractal state generation
    - natk: Neural toolkit
    - models: Data containers
"""

# Core components with fallbacks
try:
    from .kronos_architecture import KRONOS
except ImportError:
    KRONOS = None

try:
    from .kronecker_scaler import KroneckerScaler
except ImportError:
    KroneckerScaler = None

try:
    from .orchestrator import KRONOSOrchestrator
except ImportError:
    KRONOSOrchestrator = None

try:
    from .kronos_training import KRONOSTrainer, GodelLoop
except ImportError:
    KRONOSTrainer = None
    GodelLoop = None

try:
    from .depth_injector import DepthInjector
except ImportError:
    DepthInjector = None

# ✅ FIXED: Import MaxInformationCurriculum as CurriculumEngine
try:
    from .curriculum import MaxInformationCurriculum as CurriculumEngine
except ImportError:
    CurriculumEngine = None

try:
    from .gradient_rank_monitor import GradientRankMonitor
except ImportError:
    GradientRankMonitor = None

try:
    from .fractal_generator import FractalGenerator
except ImportError:
    FractalGenerator = None

try:
    from .natk import NATKAnalyzer
except ImportError:
    NATKAnalyzer = None

try:
    from .models import ScalingConfig, TrainingConfig
except ImportError:
    ScalingConfig = None
    TrainingConfig = None

__all__ = [
    'KRONOS',
    'KroneckerScaler',
    'KRONOSOrchestrator',
    'KRONOSTrainer',
    'GodelLoop',
    'DepthInjector',
    'CurriculumEngine',
    'GradientRankMonitor',
    'FractalGenerator',
    'NATKAnalyzer',
    'ScalingConfig',
    'TrainingConfig',
]