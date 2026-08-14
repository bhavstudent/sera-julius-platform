import requests
import json
API_KEY = "sera-demo-2026"
BASE_URL = "http://localhost:8000"
HEADERS = {"X-API-Key": API_KEY}
# Test all possible paths
endpoints = [
    # No auth required
    ("/health", False),
    ("/api/auth/status", False),
    # With auth - try different prefixes
    ("/api/terminal/status", True),
    ("/terminal/status", True),
    ("/api/chat/brain-status", True),
    ("/chat/brain-status", True),
    ("/api/scanner/status", True),
    ("/scanner/status", True),
    ("/api/v1/scanner/status", True),
    ("/api/exploit/status", True),
    ("/exploit/status", True),
    ("/api/v1/exploit/status", True),
    ("/api/intel/status", True),
    ("/intel/status", True),
    ("/api/osint/status", True),
    ("/osint/status", True),
    ("/api/darkweb/status", True),
    ("/darkweb/status", True),
    ("/api/nodes/status", True),
    ("/nodes/status", True),
]
print("🔍 Testing endpoints...\n")
for path, needs_auth in endpoints:
    try:
        url = f"{BASE_URL}{path}"
        if needs_auth:
            resp = requests.get(url, headers=HEADERS, timeout=5)
        else:
            resp = requests.get(url, timeout=5)
        status = "✅" if resp.status_code == 200 else "⚠️"
        print(f"{status} {path}: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict):
                print(f"   → {list(data.keys())[:3]}")
    except Exception as e:
        print(f"❌ {path}: ERROR - {str(e)[:50]}")
print("\n✅ Test complete!")
