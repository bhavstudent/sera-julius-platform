"""
AI Package
==========
LLM & AI Orchestration Layer.

Submodules:
    - chat_service: AI Assistant processing
    - llm_client: Multi-provider LLM wrapper
    - security_orchestrator: Autonomous threat analyzer
"""

from .chat_service import chat

# Alias for backward compatibility
ChatService = chat

# Optional imports with fallbacks
try:
    from .llm_client import LLMClient
except ImportError:
    LLMClient = None

try:
    from .security_orchestrator import SecurityOrchestrator
except ImportError:
    SecurityOrchestrator = None

__all__ = [
    'chat',
    'ChatService',
    'LLMClient',
    'SecurityOrchestrator',
]