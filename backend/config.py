"""
SERA Platform — Central Configuration
======================================
All configurable values live here. We use environment variables
with Pydantic validation to fail fast on invalid or missing configurations.
"""

import os
import logging
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator, ValidationError

# Load environment variables from .env file if it exists
load_dotenv()

class AppSettings(BaseModel):
    # Running Environment
    PRODUCTION: bool = Field(default=False)

    # Database
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./sera_db.sqlite3")

    # Entity AI Layer
    ENTITY_MODE: str = Field(default="mock")
    USE_NOETHER: bool = Field(default=False)
    USE_PRETRAINED_CIFN: bool = Field(default=True)
    ENTITY_API_URL: str = Field(default="http://localhost:8000")

    # AI Chat Assistant
    AI_API_KEY: str = Field(default="")
    AI_MODEL: str = Field(default="llama-3.3-70b-versatile")
    AI_BASE_URL: str = Field(default="https://api.groq.com/openai/v1")
    GROQ_API_KEY: str = Field(default="")
    GEMINI_API_KEY: str = Field(default="")
    OPENROUTER_API_KEY: str = Field(default="")

    # Synthetic Data Generation rates
    FINANCIAL_EVENTS_PER_SEC: float = Field(default=2.0, ge=0.0)
    HEALTHCARE_EVENTS_PER_SEC: float = Field(default=1.5, ge=0.0)
    IOT_EVENTS_PER_SEC: float = Field(default=3.0, ge=0.0)
    SOCIAL_EVENTS_PER_SEC: float = Field(default=2.5, ge=0.0)

    # Entropy Engine
    ENTROPY_WINDOW_SIZE: int = Field(default=50, gt=0)
    ENTROPY_ALERT_THRESHOLD: float = Field(default=2.0, gt=0.0)

    # Redis settings
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_PASSWORD: str = Field(default="")
    REDIS_DB: int = Field(default=0)

    # Server settings
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000, ge=1, le=65535)
    CORS_ORIGINS: List[str] = Field(default=["*"])

    # API credentials and sync toggles
    USE_REAL_DATA: bool = Field(default=True)
    SEC_IDENTITY_EMAIL: str = Field(default="name@domain.com")
    GITHUB_TOKEN: str = Field(default="")
    AIS_STREAM_KEY: str = Field(default="")
    APIFY_TOKEN: str = Field(default="")
    DATAGOV_IN_API_KEY: str = Field(default="")

    # Neo4j settings
    NEO4J_URI: str = Field(default="bolt://localhost:7687")
    NEO4J_USER: str = Field(default="neo4j")
    NEO4J_PASSWORD: str = Field(default="")

    # Background sync intervals (minutes)
    GDELT_INTERVAL_MINUTES: int = Field(default=15, gt=0)
    AIS_INTERVAL_MINUTES: int = Field(default=60, gt=0)
    JOBS_INTERVAL_MINUTES: int = Field(default=60, gt=0)
    EXEC_INTERVAL_MINUTES: int = Field(default=60, gt=0)
    FULL_SYNC_HOUR: int = Field(default=6, ge=0, le=23)
    FULL_SYNC_MINUTE: int = Field(default=0, ge=0, le=59)

    # ─── SECURITY AGENT CONFIG ───
    KALI_IMAGE: str = Field(default="custom-kali:latest")
    ZERO_INPUT_ENABLED: bool = Field(default=False)
    NETWORK_INTERFACE: str = Field(default="eth0")
    EXPLOIT_SERVER_IP: str = Field(default="192.168.1.100")
    
    # ─── LLM PROVIDER CONFIG ───
    LLM_PROVIDER: str = Field(default="local")  # anthropic, openai, local
    ANTHROPIC_API_KEY: str = Field(default="")
    OPENAI_API_KEY: str = Field(default="")
    LOCAL_LLM_URL: str = Field(default="http://localhost:11434/api/generate")
    LOCAL_LLM_MODEL: str = Field(default="qwen2.5:1.5b")

    # ─── CENSYS ───
    CENSYS_API_ID: str = Field(default="")
    CENSYS_API_SECRET: str = Field(default="")

    # ============================================================
    # ✅ NEW: HACKING FEATURE FLAGS
    # ============================================================
    
    # --- Advanced Hacking ---
    ENABLE_ADVANCED_HACKING: bool = Field(default=True)
    ENABLE_WEB_EXPLOIT: bool = Field(default=True)
    ENABLE_ZERO_INPUT_EXPLOIT: bool = Field(default=True)
    ENABLE_AUTONOMOUS_SCANNER: bool = Field(default=True)
    
    # --- Remote Operations ---
    ENABLE_REMOTE_OPS: bool = Field(default=True)
    ENABLE_LINUX_SHELL: bool = Field(default=True)
    ENABLE_FILE_TRANSFER: bool = Field(default=True)
    ENABLE_REMOTE_ACCESS: bool = Field(default=True)
    
    # --- BGP/MITM ---
    ENABLE_BGP_MITM: bool = Field(default=True)
    ENABLE_ARP_SPOOF: bool = Field(default=True)
    ENABLE_DNS_SPOOF: bool = Field(default=True)
    ENABLE_BGP_HIJACK: bool = Field(default=True)
    ENABLE_PACKET_SNIFFING: bool = Field(default=True)
    ENABLE_TRANSACTION_MODIFIER: bool = Field(default=True)
    ENABLE_FULL_ATTACK: bool = Field(default=True)
    
    # --- Workflow & Automation ---
    ENABLE_WORKFLOW_ENGINE: bool = Field(default=True)
    ENABLE_SELF_EVOLUTION: bool = Field(default=True)
    ENABLE_EXTERNAL_DISCOVERY: bool = Field(default=True)
    
    # --- Intelligence ---
    ENABLE_OSINT: bool = Field(default=True)
    ENABLE_SIGNAL_COLLECTION: bool = Field(default=True)
    ENABLE_PERSON_VERIFICATION: bool = Field(default=True)
    ENABLE_INTELLIGENCE_REPORT: bool = Field(default=True)
    ENABLE_DARK_WEB: bool = Field(default=True)
    ENABLE_NODE_CONTROL: bool = Field(default=True)
    
    # --- Scanner Configuration ---
    SCANNER_DEFAULT_TIMEOUT: int = Field(default=30, gt=0)
    SCANNER_MAX_CONCURRENT: int = Field(default=100, gt=0)
    SCANNER_DEFAULT_PORTS: str = Field(default="21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5900,8080")
    
    # --- Terminal Configuration ---
    TERMINAL_SESSION_TIMEOUT: int = Field(default=300, gt=0)
    TERMINAL_MAX_SESSIONS: int = Field(default=10, gt=0)
    TERMINAL_COMMAND_HISTORY: int = Field(default=1000, gt=0)
    
    # --- Exploit Configuration ---
    EXPLOIT_SAFE_MODE: bool = Field(default=True)
    EXPLOIT_MAX_TARGETS: int = Field(default=10, gt=0)
    EXPLOIT_TIMEOUT: int = Field(default=60, gt=0)
    
    # --- Veil/OPSEC ---
    VEIL_ENABLED: bool = Field(default=True)
    VEIL_TOR_ENABLED: bool = Field(default=True)
    VEIL_MIXNET_ENABLED: bool = Field(default=False)
    VEIL_COVER_TRAFFIC: bool = Field(default=False)
    
    # --- Rate Limits ---
    RATE_LIMIT_DEFAULT: str = Field(default="60/minute")
    RATE_LIMIT_HACKING: str = Field(default="10/minute")
    RATE_LIMIT_SCANNER: str = Field(default="5/minute")
    RATE_LIMIT_OSINT: str = Field(default="30/minute")
    
    # --- Logging ---
    LOG_LEVEL: str = Field(default="INFO")
    LOG_HACKING_ACTIONS: bool = Field(default=True)
    LOG_ATTACK_CHAINS: bool = Field(default=True)
    
    # --- Security ---
    SECURITY_AUDIT_ENABLED: bool = Field(default=True)
    SECURITY_MAX_LOGIN_ATTEMPTS: int = Field(default=5, gt=0)
    SECURITY_SESSION_TIMEOUT: int = Field(default=3600, gt=0)
    
    # --- Monitoring ---
    MONITORING_INTERVAL: int = Field(default=60, gt=0)
    MONITORING_RETENTION: int = Field(default=86400, gt=0)  # 24 hours
    
    # --- Intel Pipeline ---
    INTEL_PIPELINE_BATCH_SIZE: int = Field(default=100, gt=0)
    INTEL_PIPELINE_MAX_QUEUE: int = Field(default=10000, gt=0)
    INTEL_PIPELINE_PROCESS_INTERVAL: int = Field(default=5, gt=0)

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        allowed_prefixes = (
            "postgresql+asyncpg://",
            "sqlite+aiosqlite://",
            "sqlite://",
            "postgresql://"
        )
        if not any(v.startswith(prefix) for prefix in allowed_prefixes):
            raise ValueError(
                f"DATABASE_URL must start with one of: {', '.join(allowed_prefixes)}. "
                f"Got: {v}"
            )
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


def _load_settings() -> AppSettings:
    raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
    
    # Helper to parse string bools
    def get_bool(key: str, default: bool) -> bool:
        val = os.getenv(key)
        if val is None:
            return default
        return val.strip().lower() in ("true", "1", "yes")

    try:
        settings = AppSettings(
            PRODUCTION=get_bool("PRODUCTION", False) or (os.getenv("ENTITY_MODE", "mock").lower() != "mock"),
            DATABASE_URL=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./sera_db.sqlite3"),
            ENTITY_MODE=os.getenv("ENTITY_MODE", "mock"),
            USE_NOETHER=get_bool("USE_NOETHER", False),
            USE_PRETRAINED_CIFN=get_bool("USE_PRETRAINED_CIFN", True),
            ENTITY_API_URL=os.getenv("ENTITY_API_URL", "http://localhost:8000"),
            AI_API_KEY=os.getenv("AI_API_KEY", ""),
            AI_MODEL=os.getenv("AI_MODEL", "grok-3-mini-fast"),
            AI_BASE_URL=os.getenv("AI_BASE_URL", "https://api.x.ai/v1"),
            FINANCIAL_EVENTS_PER_SEC=float(os.getenv("FINANCIAL_EVENTS_PER_SEC", "2.0")),
            HEALTHCARE_EVENTS_PER_SEC=float(os.getenv("HEALTHCARE_EVENTS_PER_SEC", "1.5")),
            IOT_EVENTS_PER_SEC=float(os.getenv("IOT_EVENTS_PER_SEC", "3.0")),
            SOCIAL_EVENTS_PER_SEC=float(os.getenv("SOCIAL_EVENTS_PER_SEC", "2.5")),
            ENTROPY_WINDOW_SIZE=int(os.getenv("ENTROPY_WINDOW_SIZE", "50")),
            ENTROPY_ALERT_THRESHOLD=float(os.getenv("ENTROPY_ALERT_THRESHOLD", "2.0")),
            REDIS_HOST=os.getenv("REDIS_HOST", "localhost"),
            REDIS_PORT=int(os.getenv("REDIS_PORT", "6379")),
            REDIS_PASSWORD=os.getenv("REDIS_PASSWORD", ""),
            REDIS_DB=int(os.getenv("REDIS_DB", "0")),
            HOST=os.getenv("HOST", "0.0.0.0"),
            PORT=int(os.getenv("PORT", "8000")),
            CORS_ORIGINS=raw_origins,
            USE_REAL_DATA=get_bool("USE_REAL_DATA", False),
            SEC_IDENTITY_EMAIL=os.getenv("SEC_IDENTITY_EMAIL", ""),
            GITHUB_TOKEN=os.getenv("GITHUB_TOKEN", ""),
            AIS_STREAM_KEY=os.getenv("AIS_STREAM_KEY", ""),
            APIFY_TOKEN=os.getenv("APIFY_TOKEN", ""),
            DATAGOV_IN_API_KEY=os.getenv("DATAGOV_IN_API_KEY", ""),
            NEO4J_URI=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            NEO4J_USER=os.getenv("NEO4J_USER", "neo4j"),
            NEO4J_PASSWORD=os.getenv("NEO4J_PASSWORD", ""),
            GDELT_INTERVAL_MINUTES=int(os.getenv("GDELT_INTERVAL_MINUTES", "15")),
            AIS_INTERVAL_MINUTES=int(os.getenv("AIS_INTERVAL_MINUTES", "60")),
            JOBS_INTERVAL_MINUTES=int(os.getenv("JOBS_INTERVAL_MINUTES", "60")),
            EXEC_INTERVAL_MINUTES=int(os.getenv("EXEC_INTERVAL_MINUTES", "60")),
            FULL_SYNC_HOUR=int(os.getenv("FULL_SYNC_HOUR", "6")),
            FULL_SYNC_MINUTE=int(os.getenv("FULL_SYNC_MINUTE", "0")),
            KALI_IMAGE=os.getenv("KALI_IMAGE", "custom-kali:latest"),
            ZERO_INPUT_ENABLED=get_bool("ZERO_INPUT_ENABLED", False),
            NETWORK_INTERFACE=os.getenv("NETWORK_INTERFACE", "eth0"),
            EXPLOIT_SERVER_IP=os.getenv("EXPLOIT_SERVER_IP", "192.168.1.100"),
            LLM_PROVIDER=os.getenv("LLM_PROVIDER", "local"),
            ANTHROPIC_API_KEY=os.getenv("ANTHROPIC_API_KEY", ""),
            OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", ""),
            LOCAL_LLM_URL=os.getenv("LOCAL_LLM_URL", "http://localhost:11434/api/generate"),
            LOCAL_LLM_MODEL=os.getenv("LOCAL_LLM_MODEL", "qwen2.5:1.5b"),
            CENSYS_API_ID=os.getenv("CENSYS_API_ID", ""),
            CENSYS_API_SECRET=os.getenv("CENSYS_API_SECRET", ""),
            # ============================================================
            # ✅ NEW: HACKING FEATURE FLAGS
            # ============================================================
            ENABLE_ADVANCED_HACKING=get_bool("ENABLE_ADVANCED_HACKING", True),
            ENABLE_WEB_EXPLOIT=get_bool("ENABLE_WEB_EXPLOIT", True),
            ENABLE_ZERO_INPUT_EXPLOIT=get_bool("ENABLE_ZERO_INPUT_EXPLOIT", True),
            ENABLE_AUTONOMOUS_SCANNER=get_bool("ENABLE_AUTONOMOUS_SCANNER", True),
            ENABLE_REMOTE_OPS=get_bool("ENABLE_REMOTE_OPS", True),
            ENABLE_LINUX_SHELL=get_bool("ENABLE_LINUX_SHELL", True),
            ENABLE_FILE_TRANSFER=get_bool("ENABLE_FILE_TRANSFER", True),
            ENABLE_REMOTE_ACCESS=get_bool("ENABLE_REMOTE_ACCESS", True),
            ENABLE_BGP_MITM=get_bool("ENABLE_BGP_MITM", True),
            ENABLE_ARP_SPOOF=get_bool("ENABLE_ARP_SPOOF", True),
            ENABLE_DNS_SPOOF=get_bool("ENABLE_DNS_SPOOF", True),
            ENABLE_BGP_HIJACK=get_bool("ENABLE_BGP_HIJACK", True),
            ENABLE_PACKET_SNIFFING=get_bool("ENABLE_PACKET_SNIFFING", True),
            ENABLE_TRANSACTION_MODIFIER=get_bool("ENABLE_TRANSACTION_MODIFIER", True),
            ENABLE_FULL_ATTACK=get_bool("ENABLE_FULL_ATTACK", True),
            ENABLE_WORKFLOW_ENGINE=get_bool("ENABLE_WORKFLOW_ENGINE", True),
            ENABLE_SELF_EVOLUTION=get_bool("ENABLE_SELF_EVOLUTION", True),
            ENABLE_EXTERNAL_DISCOVERY=get_bool("ENABLE_EXTERNAL_DISCOVERY", True),
            ENABLE_OSINT=get_bool("ENABLE_OSINT", True),
            ENABLE_SIGNAL_COLLECTION=get_bool("ENABLE_SIGNAL_COLLECTION", True),
            ENABLE_PERSON_VERIFICATION=get_bool("ENABLE_PERSON_VERIFICATION", True),
            ENABLE_INTELLIGENCE_REPORT=get_bool("ENABLE_INTELLIGENCE_REPORT", True),
            ENABLE_DARK_WEB=get_bool("ENABLE_DARK_WEB", True),
            ENABLE_NODE_CONTROL=get_bool("ENABLE_NODE_CONTROL", True),
            SCANNER_DEFAULT_TIMEOUT=int(os.getenv("SCANNER_DEFAULT_TIMEOUT", "30")),
            SCANNER_MAX_CONCURRENT=int(os.getenv("SCANNER_MAX_CONCURRENT", "100")),
            SCANNER_DEFAULT_PORTS=os.getenv("SCANNER_DEFAULT_PORTS", "21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5900,8080"),
            TERMINAL_SESSION_TIMEOUT=int(os.getenv("TERMINAL_SESSION_TIMEOUT", "300")),
            TERMINAL_MAX_SESSIONS=int(os.getenv("TERMINAL_MAX_SESSIONS", "10")),
            TERMINAL_COMMAND_HISTORY=int(os.getenv("TERMINAL_COMMAND_HISTORY", "1000")),
            EXPLOIT_SAFE_MODE=get_bool("EXPLOIT_SAFE_MODE", True),
            EXPLOIT_MAX_TARGETS=int(os.getenv("EXPLOIT_MAX_TARGETS", "10")),
            EXPLOIT_TIMEOUT=int(os.getenv("EXPLOIT_TIMEOUT", "60")),
            VEIL_ENABLED=get_bool("VEIL_ENABLED", True),
            VEIL_TOR_ENABLED=get_bool("VEIL_TOR_ENABLED", True),
            VEIL_MIXNET_ENABLED=get_bool("VEIL_MIXNET_ENABLED", False),
            VEIL_COVER_TRAFFIC=get_bool("VEIL_COVER_TRAFFIC", False),
            RATE_LIMIT_DEFAULT=os.getenv("RATE_LIMIT_DEFAULT", "60/minute"),
            RATE_LIMIT_HACKING=os.getenv("RATE_LIMIT_HACKING", "10/minute"),
            RATE_LIMIT_SCANNER=os.getenv("RATE_LIMIT_SCANNER", "5/minute"),
            RATE_LIMIT_OSINT=os.getenv("RATE_LIMIT_OSINT", "30/minute"),
            LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
            LOG_HACKING_ACTIONS=get_bool("LOG_HACKING_ACTIONS", True),
            LOG_ATTACK_CHAINS=get_bool("LOG_ATTACK_CHAINS", True),
            SECURITY_AUDIT_ENABLED=get_bool("SECURITY_AUDIT_ENABLED", True),
            SECURITY_MAX_LOGIN_ATTEMPTS=int(os.getenv("SECURITY_MAX_LOGIN_ATTEMPTS", "5")),
            SECURITY_SESSION_TIMEOUT=int(os.getenv("SECURITY_SESSION_TIMEOUT", "3600")),
            MONITORING_INTERVAL=int(os.getenv("MONITORING_INTERVAL", "60")),
            MONITORING_RETENTION=int(os.getenv("MONITORING_RETENTION", "86400")),
            INTEL_PIPELINE_BATCH_SIZE=int(os.getenv("INTEL_PIPELINE_BATCH_SIZE", "100")),
            INTEL_PIPELINE_MAX_QUEUE=int(os.getenv("INTEL_PIPELINE_MAX_QUEUE", "10000")),
            INTEL_PIPELINE_PROCESS_INTERVAL=int(os.getenv("INTEL_PIPELINE_PROCESS_INTERVAL", "5")),
        )

        # In production mode, enforce security checks
        if settings.PRODUCTION:
            if settings.NEO4J_URI.startswith("bolt://localhost") and not os.getenv("ALLOW_LOCALHOST_DB_IN_PROD"):
                logging.warning("[CONFIG] Running in PRODUCTION but NEO4J_URI is local database.")
            if not settings.DATABASE_URL or "localhost" in settings.DATABASE_URL:
                if not os.getenv("ALLOW_LOCALHOST_DB_IN_PROD"):
                    logging.warning("[CONFIG] Running in PRODUCTION but DATABASE_URL points to localhost.")

        return settings

    except ValidationError as e:
        print(f"CRITICAL CONFIGURATION ERROR:\n{e}")
        raise SystemExit(1)
    except Exception as e:
        print(f"CRITICAL CONFIGURATION INITIALIZATION FAILURE: {e}")
        raise SystemExit(1)


# Instance loaded at runtime
_config_instance = _load_settings()

# ============================================================
# EXPORT ALL SETTINGS
# ============================================================

# Core settings
PRODUCTION = _config_instance.PRODUCTION
DATABASE_URL = _config_instance.DATABASE_URL
ENTITY_MODE = _config_instance.ENTITY_MODE
USE_NOETHER = _config_instance.USE_NOETHER
USE_PRETRAINED_CIFN = _config_instance.USE_PRETRAINED_CIFN
ENTITY_API_URL = _config_instance.ENTITY_API_URL

# AI Settings
AI_API_KEY = _config_instance.AI_API_KEY
AI_MODEL = _config_instance.AI_MODEL
AI_BASE_URL = _config_instance.AI_BASE_URL

# Event Generation
FINANCIAL_EVENTS_PER_SEC = _config_instance.FINANCIAL_EVENTS_PER_SEC
HEALTHCARE_EVENTS_PER_SEC = _config_instance.HEALTHCARE_EVENTS_PER_SEC
IOT_EVENTS_PER_SEC = _config_instance.IOT_EVENTS_PER_SEC
SOCIAL_EVENTS_PER_SEC = _config_instance.SOCIAL_EVENTS_PER_SEC

# Entropy
ENTROPY_WINDOW_SIZE = _config_instance.ENTROPY_WINDOW_SIZE
ENTROPY_ALERT_THRESHOLD = _config_instance.ENTROPY_ALERT_THRESHOLD

# Redis
REDIS_HOST = _config_instance.REDIS_HOST
REDIS_PORT = _config_instance.REDIS_PORT
REDIS_PASSWORD = _config_instance.REDIS_PASSWORD
REDIS_DB = _config_instance.REDIS_DB

# Server
HOST = _config_instance.HOST
PORT = _config_instance.PORT
CORS_ORIGINS = _config_instance.CORS_ORIGINS

# Data Sync
USE_REAL_DATA = _config_instance.USE_REAL_DATA
SEC_IDENTITY_EMAIL = _config_instance.SEC_IDENTITY_EMAIL
GITHUB_TOKEN = _config_instance.GITHUB_TOKEN
AIS_STREAM_KEY = _config_instance.AIS_STREAM_KEY
APIFY_TOKEN = _config_instance.APIFY_TOKEN
DATAGOV_IN_API_KEY = _config_instance.DATAGOV_IN_API_KEY

# Neo4j
NEO4J_URI = _config_instance.NEO4J_URI
NEO4J_USER = _config_instance.NEO4J_USER
NEO4J_PASSWORD = _config_instance.NEO4J_PASSWORD

# Sync Intervals
GDELT_INTERVAL_MINUTES = _config_instance.GDELT_INTERVAL_MINUTES
AIS_INTERVAL_MINUTES = _config_instance.AIS_INTERVAL_MINUTES
JOBS_INTERVAL_MINUTES = _config_instance.JOBS_INTERVAL_MINUTES
EXEC_INTERVAL_MINUTES = _config_instance.EXEC_INTERVAL_MINUTES
FULL_SYNC_HOUR = _config_instance.FULL_SYNC_HOUR
FULL_SYNC_MINUTE = _config_instance.FULL_SYNC_MINUTE

# Security Agent
KALI_IMAGE = _config_instance.KALI_IMAGE
ZERO_INPUT_ENABLED = _config_instance.ZERO_INPUT_ENABLED
NETWORK_INTERFACE = _config_instance.NETWORK_INTERFACE
EXPLOIT_SERVER_IP = _config_instance.EXPLOIT_SERVER_IP

# LLM
LLM_PROVIDER = _config_instance.LLM_PROVIDER
ANTHROPIC_API_KEY = _config_instance.ANTHROPIC_API_KEY
OPENAI_API_KEY = _config_instance.OPENAI_API_KEY
LOCAL_LLM_URL = _config_instance.LOCAL_LLM_URL
LOCAL_LLM_MODEL = _config_instance.LOCAL_LLM_MODEL

# Censys
CENSYS_API_ID = _config_instance.CENSYS_API_ID
CENSYS_API_SECRET = _config_instance.CENSYS_API_SECRET

# ============================================================
# ✅ NEW: HACKING EXPORTS
# ============================================================

# Hacking Flags
ENABLE_ADVANCED_HACKING = _config_instance.ENABLE_ADVANCED_HACKING
ENABLE_WEB_EXPLOIT = _config_instance.ENABLE_WEB_EXPLOIT
ENABLE_ZERO_INPUT_EXPLOIT = _config_instance.ENABLE_ZERO_INPUT_EXPLOIT
ENABLE_AUTONOMOUS_SCANNER = _config_instance.ENABLE_AUTONOMOUS_SCANNER
ENABLE_REMOTE_OPS = _config_instance.ENABLE_REMOTE_OPS
ENABLE_LINUX_SHELL = _config_instance.ENABLE_LINUX_SHELL
ENABLE_FILE_TRANSFER = _config_instance.ENABLE_FILE_TRANSFER
ENABLE_REMOTE_ACCESS = _config_instance.ENABLE_REMOTE_ACCESS

# BGP/MITM
ENABLE_BGP_MITM = _config_instance.ENABLE_BGP_MITM
ENABLE_ARP_SPOOF = _config_instance.ENABLE_ARP_SPOOF
ENABLE_DNS_SPOOF = _config_instance.ENABLE_DNS_SPOOF
ENABLE_BGP_HIJACK = _config_instance.ENABLE_BGP_HIJACK
ENABLE_PACKET_SNIFFING = _config_instance.ENABLE_PACKET_SNIFFING
ENABLE_TRANSACTION_MODIFIER = _config_instance.ENABLE_TRANSACTION_MODIFIER
ENABLE_FULL_ATTACK = _config_instance.ENABLE_FULL_ATTACK

# Workflow
ENABLE_WORKFLOW_ENGINE = _config_instance.ENABLE_WORKFLOW_ENGINE
ENABLE_SELF_EVOLUTION = _config_instance.ENABLE_SELF_EVOLUTION
ENABLE_EXTERNAL_DISCOVERY = _config_instance.ENABLE_EXTERNAL_DISCOVERY

# Intelligence
ENABLE_OSINT = _config_instance.ENABLE_OSINT
ENABLE_SIGNAL_COLLECTION = _config_instance.ENABLE_SIGNAL_COLLECTION
ENABLE_PERSON_VERIFICATION = _config_instance.ENABLE_PERSON_VERIFICATION
ENABLE_INTELLIGENCE_REPORT = _config_instance.ENABLE_INTELLIGENCE_REPORT
ENABLE_DARK_WEB = _config_instance.ENABLE_DARK_WEB
ENABLE_NODE_CONTROL = _config_instance.ENABLE_NODE_CONTROL

# Scanner
SCANNER_DEFAULT_TIMEOUT = _config_instance.SCANNER_DEFAULT_TIMEOUT
SCANNER_MAX_CONCURRENT = _config_instance.SCANNER_MAX_CONCURRENT
SCANNER_DEFAULT_PORTS = _config_instance.SCANNER_DEFAULT_PORTS

# Terminal
TERMINAL_SESSION_TIMEOUT = _config_instance.TERMINAL_SESSION_TIMEOUT
TERMINAL_MAX_SESSIONS = _config_instance.TERMINAL_MAX_SESSIONS
TERMINAL_COMMAND_HISTORY = _config_instance.TERMINAL_COMMAND_HISTORY

# Exploit
EXPLOIT_SAFE_MODE = _config_instance.EXPLOIT_SAFE_MODE
EXPLOIT_MAX_TARGETS = _config_instance.EXPLOIT_MAX_TARGETS
EXPLOIT_TIMEOUT = _config_instance.EXPLOIT_TIMEOUT

# Veil
VEIL_ENABLED = _config_instance.VEIL_ENABLED
VEIL_TOR_ENABLED = _config_instance.VEIL_TOR_ENABLED
VEIL_MIXNET_ENABLED = _config_instance.VEIL_MIXNET_ENABLED
VEIL_COVER_TRAFFIC = _config_instance.VEIL_COVER_TRAFFIC

# Rate Limits
RATE_LIMIT_DEFAULT = _config_instance.RATE_LIMIT_DEFAULT
RATE_LIMIT_HACKING = _config_instance.RATE_LIMIT_HACKING
RATE_LIMIT_SCANNER = _config_instance.RATE_LIMIT_SCANNER
RATE_LIMIT_OSINT = _config_instance.RATE_LIMIT_OSINT

# Logging
LOG_LEVEL = _config_instance.LOG_LEVEL
LOG_HACKING_ACTIONS = _config_instance.LOG_HACKING_ACTIONS
LOG_ATTACK_CHAINS = _config_instance.LOG_ATTACK_CHAINS

# Security
SECURITY_AUDIT_ENABLED = _config_instance.SECURITY_AUDIT_ENABLED
SECURITY_MAX_LOGIN_ATTEMPTS = _config_instance.SECURITY_MAX_LOGIN_ATTEMPTS
SECURITY_SESSION_TIMEOUT = _config_instance.SECURITY_SESSION_TIMEOUT

# Monitoring
MONITORING_INTERVAL = _config_instance.MONITORING_INTERVAL
MONITORING_RETENTION = _config_instance.MONITORING_RETENTION

# Intel Pipeline
INTEL_PIPELINE_BATCH_SIZE = _config_instance.INTEL_PIPELINE_BATCH_SIZE
INTEL_PIPELINE_MAX_QUEUE = _config_instance.INTEL_PIPELINE_MAX_QUEUE
INTEL_PIPELINE_PROCESS_INTERVAL = _config_instance.INTEL_PIPELINE_PROCESS_INTERVAL

# ============================================================
# CONFIG VALIDATION (Optional)
# ============================================================

def validate_config():
    """Validate critical configuration values"""
    issues = []
    
    # Check if database URL is set
    if not DATABASE_URL:
        issues.append("DATABASE_URL not set")
    
    # Check if Redis is configured
    if not REDIS_HOST:
        issues.append("REDIS_HOST not set")
    
    # Check if Neo4j is configured
    if not NEO4J_URI:
        issues.append("NEO4J_URI not set")
    
    if issues:
        print(f"⚠️ Configuration warnings: {', '.join(issues)}")
    
    return len(issues) == 0


# ============================================================
# PRINT STARTUP CONFIG (Debug)
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("SERA PLATFORM CONFIGURATION")
    print("=" * 70)
    print(f"Entity Mode: {ENTITY_MODE}")
    print(f"Production: {PRODUCTION}")
    print(f"Database: {DATABASE_URL[:50]}...")
    print(f"Redis: {REDIS_HOST}:{REDIS_PORT}")
    print(f"Neo4j: {NEO4J_URI}")
    print("-" * 70)
    print("HACKING FEATURE FLAGS:")
    print(f"  Advanced Hacking: {ENABLE_ADVANCED_HACKING}")
    print(f"  Web Exploit: {ENABLE_WEB_EXPLOIT}")
    print(f"  Zero-Input Exploit: {ENABLE_ZERO_INPUT_EXPLOIT}")
    print(f"  Autonomous Scanner: {ENABLE_AUTONOMOUS_SCANNER}")
    print(f"  Remote Ops: {ENABLE_REMOTE_OPS}")
    print(f"  Linux Shell: {ENABLE_LINUX_SHELL}")
    print(f"  File Transfer: {ENABLE_FILE_TRANSFER}")
    print("-" * 70)
    print("BGP/MITM:")
    print(f"  ARP Spoof: {ENABLE_ARP_SPOOF}")
    print(f"  DNS Spoof: {ENABLE_DNS_SPOOF}")
    print(f"  BGP Hijack: {ENABLE_BGP_HIJACK}")
    print(f"  Packet Sniffing: {ENABLE_PACKET_SNIFFING}")
    print(f"  Transaction Modifier: {ENABLE_TRANSACTION_MODIFIER}")
    print(f"  Full Attack: {ENABLE_FULL_ATTACK}")
    print("-" * 70)
    print("INTELLIGENCE:")
    print(f"  OSINT: {ENABLE_OSINT}")
    print(f"  Signal Collection: {ENABLE_SIGNAL_COLLECTION}")
    print(f"  Dark Web: {ENABLE_DARK_WEB}")
    print(f"  Node Control: {ENABLE_NODE_CONTROL}")
    print("-" * 70)
    print("RATE LIMITS:")
    print(f"  Default: {RATE_LIMIT_DEFAULT}")
    print(f"  Hacking: {RATE_LIMIT_HACKING}")
    print(f"  Scanner: {RATE_LIMIT_SCANNER}")
    print(f"  OSINT: {RATE_LIMIT_OSINT}")
    print("=" * 70)
# ============================================================
# ? SANDBOX CONFIGURATION (For chat.py file operations)
# ============================================================
SANDBOX_ROOT = os.getenv('SANDBOX_ROOT', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sandbox'))
if not os.path.exists(SANDBOX_ROOT):
    try:
        os.makedirs(SANDBOX_ROOT, exist_ok=True)
    except Exception:
        pass

# ============================================================
# ? API KEYS (For auth.py)
# ============================================================
API_KEYS_ENV = os.getenv('API_KEYS', '')
API_KEYS = {}
if API_KEYS_ENV.strip():
    try:
        import json
        parsed = json.loads(API_KEYS_ENV)
        if isinstance(parsed, dict):
            API_KEYS = parsed
        elif isinstance(parsed, list):
            API_KEYS = {k: f'client_{i}' for i, k in enumerate(parsed)}
    except json.JSONDecodeError:
        for val in API_KEYS_ENV.split(','):
            val = val.strip()
            if val:
                API_KEYS[val] = f'client_{val[-4:] if len(val) >= 4 else val}'

# ============================================================
# OLLAMA CONFIGURATION
# ============================================================
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')

# ============================================================
# SECURITY CONFIGURATION
# ============================================================
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))

# ============================================================
# REDIS CONFIGURATION
# ============================================================
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
REDIS_DB = int(os.getenv('REDIS_DB', '0'))
REDIS_URL = os.getenv('REDIS_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}')

# ============================================================
# OPENROUTER CONFIGURATION (for Darkweb)
# ============================================================
OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
