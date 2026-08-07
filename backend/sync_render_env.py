import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RENDER_API_KEY", "")
SERVICE_ID = "srv-d9m6cm95efls73ck2jf0"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

env_vars = [
    {"key": "DEMO_API_KEY", "value": os.getenv("DEMO_API_KEY", "sera-demo-2026")},
    {"key": "API_KEYS", "value": os.getenv("API_KEYS", '{"sera-demo-2026":"default_demo"}')},
    {"key": "AI_API_KEY", "value": os.getenv("AI_API_KEY", "")},
    {"key": "OPENAI_API_KEY", "value": os.getenv("OPENAI_API_KEY", "")},
    {"key": "LLM_PROVIDER", "value": os.getenv("LLM_PROVIDER", "openai")},
    {"key": "AI_BASE_URL", "value": os.getenv("AI_BASE_URL", "https://integrate.api.nvidia.com/v1")},
    {"key": "AI_MODEL", "value": os.getenv("AI_MODEL", "meta/llama-3.1-8b-instruct")},
    {"key": "GITHUB_TOKEN", "value": os.getenv("GITHUB_TOKEN", "")},
    {"key": "AIS_STREAM_KEY", "value": os.getenv("AIS_STREAM_KEY", "")},
    {"key": "APIFY_TOKEN", "value": os.getenv("APIFY_TOKEN", "")},
    {"key": "USE_REAL_DATA", "value": "true"},
    {"key": "ENTITY_MODE", "value": "live"},
    {"key": "USE_PRETRAINED_CIFN", "value": "true"},
    {"key": "STYX_ENABLED", "value": "true"},
    {"key": "ZERO_INPUT_ENABLED", "value": "true"},
    {"key": "CORS_ORIGINS", "value": "*"},
    {"key": "SEC_IDENTITY_EMAIL", "value": "name@domain.com"},
    {"key": "GDELT_INTERVAL_MINUTES", "value": "15"},
    {"key": "AIS_INTERVAL_MINUTES", "value": "60"},
    {"key": "JOBS_INTERVAL_MINUTES", "value": "60"},
    {"key": "EXEC_INTERVAL_MINUTES", "value": "60"}
]

if API_KEY:
    r = requests.put(f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars", json=env_vars, headers=headers)
    print("ENV VARS SYNC HTTP STATUS:", r.status_code)
else:
    print("No RENDER_API_KEY provided.")
