"""
Services Package
================
Business logic and infrastructure services.

Available services:
    - auth_service: Authentication & JWT
    - security_service: Vulnerability scanning
    - data_orchestrator: Data aggregation
    - autogen_brain: Multi-agent reasoning
    - julius_ai: AI analytical engine
    - self_evolution: Self-adapting logic
    - workflow_engine: Incident workflow
    - kronos_service: Kronos execution
    - and 40+ more...
"""

from .auth_service import AuthService
from .security_service import SecurityService
from .data_orchestrator import DataIngestionService as DataOrchestrator
from .autogen_brain import get_julius_agent, ask_julius
from .julius_ai import JuliusAI
from .self_evolution import SelfEvolution
from .workflow_engine import execute_workflow, create_from_template
from .kronos_service import KronosService

__all__ = [
    'AuthService',
    'SecurityService',
    'DataOrchestrator',
    'get_julius_agent',
    'ask_julius',
    'JuliusAI',
    'SelfEvolution',
    'execute_workflow',
    'create_from_template',
    'KronosService',
]