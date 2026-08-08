import requests
import json

API_KEY = "rnd_lzrQQC9txS3lRO5ZLkd2X3psBrjB"
OWNER_ID = "tea-d6sh9g4r85hc73esjri0"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

payload = {
    "type": "web_service",
    "name": "sera-julius-platform-backend",
    "ownerId": OWNER_ID,
    "repo": "https://github.com/bhavstudent/sera-julius-platform",
    "branch": "main",
    "rootDir": "backend",
    "autoDeploy": "yes",
    "serviceDetails": {
        "env": "python",
        "region": "oregon",
        "plan": "free",
        "healthCheckPath": "/health",
        "envSpecificDetails": {
            "buildCommand": "pip install -r requirements-lite.txt",
            "startCommand": "python -m uvicorn main:app --host 0.0.0.0 --port $PORT"
        },
        "envVars": [
            {"key": "ENTITY_MODE", "value": "mock"},
            {"key": "DEMO_API_KEY", "value": "sera-demo-2026"},
            {"key": "USE_REAL_DATA", "value": "false"}
        ]
    }
}

print("Creating brand new Render backend web service from scratch...")
r = requests.post("https://api.render.com/v1/services", json=payload, headers=headers)
print("STATUS CODE:", r.status_code)
print("RESPONSE:", json.dumps(r.json(), indent=2))
