import requests
import json
API_KEY = "sera-demo-2026"
BASE_URL = "http://localhost:8000"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
print("🚀 Testing SERA Platform Endpoints\n")
print("=" * 50)
# Test working endpoints
tests = [
    ("Health", "/health", "GET", None, False),
    ("Auth Status", "/api/auth/status", "GET", None, False),
    ("Terminal Status", "/api/terminal/status", "GET", None, True),
    ("Chat Brain", "/api/chat/brain-status", "GET", None, True),
    ("Nodes Status", "/api/nodes/status", "GET", None, True),
    ("Darkweb Health", "/api/darkweb/health", "GET", None, True),
    ("Exploit Modules", "/api/v1/exploit/api/exploit/modules", "GET", None, True),
    ("Scanner Scan", "/api/v1/scanner/api/scanner/scan", "POST", {"target":"127.0.0.1", "ports":[80,443]}, True),
    ("Intel Pipeline", "/api/v1/intel/api/intel-pipeline/status", "GET", None, True),
    ("Intelligence Health", "/api/v1/intelligence/api/intelligence/health", "GET", None, True),
]
for name, path, method, body, auth in tests:
    try:
        url = f"{BASE_URL}{path}"
        if method == "GET":
            resp = requests.get(url, headers=HEADERS if auth else None, timeout=5)
        else:
            resp = requests.post(url, headers=HEADERS if auth else None, json=body, timeout=10)
        status = "✅" if resp.status_code == 200 else "⚠️"
        print(f"{status} {name}: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict):
                print(f"   → {list(data.keys())[:5]}")
    except Exception as e:
        print(f"❌ {name}: ERROR - {str(e)[:60]}")
print("\n" + "=" * 50)
print("✅ Test complete!")
