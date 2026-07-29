import urllib.request
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE = "http://localhost:8000"
HEADERS = {"X-API-Key": "sera-demo-2026", "Content-Type": "application/json"}

ENDPOINTS = [
    # Dashboard page
    ("/api/dashboard/stats", "GET"),
    
    # Entities page
    ("/api/entities/", "GET"),
    
    # Signal Synthesis page
    ("/api/insights/expansion/AAPL", "GET"),
    
    # Citation Tracking page
    ("/api/citation/tracked", "GET"),
    
    # AXIOM-Φ Monitor page
    ("/api/axiom/entropy", "GET"),
    ("/api/axiom/alerts", "GET"),
    
    # ZOLA Causal Engine page
    ("/api/zola/predictions", "GET"),
    ("/api/zola/status", "GET"),
    
    # AI Assistant page
    ("/api/chat/", "POST", {"message": "Hello"}),
    
    # Dark Intel Briefings page
    ("/api/intel/classified", "GET"),
    ("/api/intel/news", "GET"),
    
    # Healthcare page
    ("/api/healthcare/metrics", "GET"),
    
    # Executive page
    ("/api/executive/movements", "GET"),
    
    # Security Assessment Console page
    ("/api/security/engagements", "GET"),
]

def test_all():
    print("==========================================================")
    print("PROBING SERA PLATFORM ENDPOINTS FOR ALL FRONTEND PAGES")
    print("==========================================================")
    
    passed = 0
    failed = 0
    
    for item in ENDPOINTS:
        url = BASE + item[0]
        method = item[1]
        body = json.dumps(item[2]).encode() if len(item) > 2 else None
        
        req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
        try:
            res = urllib.request.urlopen(req)
            code = res.getcode()
            content = res.read().decode()
            data = json.loads(content) if content else {}
            data_preview = str(data)[:60]
            print(f"[PASS 200 OK] {method} {item[0]} -> {data_preview}...")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {method} {item[0]} -> ERROR: {e}")
            failed += 1

    print("==========================================================")
    print(f"RESULT SUMMARY: {passed} PASSED, {failed} FAILED")
    print("==========================================================")

if __name__ == "__main__":
    test_all()

