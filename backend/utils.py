"""
Utilities Module - Helper functions for SERA Platform
"""
import re
import os
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
logger = logging.getLogger(__name__)
def safe_strip(text: str) -> str:
    if text is None:
        return ""
    return str(text).strip()
def safe_truncate(text: str, max_length: int = 1000) -> str:
    if not text:
        return ""
    text = str(text)
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
def sanitize_filename(filename: str) -> str:
    filename = filename.replace("/", "_").replace("\\", "_")
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return filename.strip().strip('.') or "unnamed"
def extract_emails(text: str) -> List[str]:
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, str(text))
def extract_urls(text: str) -> List[str]:
    pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    return re.findall(pattern, str(text))
def extract_ips(text: str) -> List[str]:
    pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    return re.findall(pattern, str(text))
def get_timestamp() -> str:
    return datetime.utcnow().isoformat()
def generate_id(prefix: str = "") -> str:
    import uuid
    uid = uuid.uuid4().hex[:12]
    return f"{prefix}_{uid}" if prefix else uid
def is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, (str, list, dict, tuple, set)):
        return len(value) == 0
    return False
__all__ = ["safe_strip", "safe_truncate", "sanitize_filename", "extract_emails", "extract_urls", "extract_ips", "get_timestamp", "generate_id", "is_empty"]
