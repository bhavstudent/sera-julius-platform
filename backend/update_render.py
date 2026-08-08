import requests

API_KEY = "rnd_lzrQQC9txS3lRO5ZLkd2X3psBrjB"
SERVICE_ID = "srv-d9rdcbijnfac73ff9d7g"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

patch_payload = {
    "rootDir": "backend",
    "serviceDetails": {
        "healthCheckPath": "/health",
        "envSpecificDetails": {
            "buildCommand": "pip install -r requirements-lite.txt",
            "startCommand": "python -m uvicorn main:app --host 0.0.0.0 --port $PORT"
        }
    }
}

r = requests.patch(f"https://api.render.com/v1/services/{SERVICE_ID}", json=patch_payload, headers=headers)
print("PATCH STATUS:", r.status_code)
if r.status_code == 200:
    print("PATCH SUCCESS:", r.json().get("name"))

d = requests.post(f"https://api.render.com/v1/services/{SERVICE_ID}/deploys", headers=headers)
print("DEPLOY TRIGGER HTTP STATUS:", d.status_code)
if d.status_code in (200, 201) and d.text:
    print("NEW DEPLOY ID:", d.json().get("id"))
