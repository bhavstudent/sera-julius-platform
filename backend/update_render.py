import requests

API_KEY = "rnd_lzrQQC9txS3lRO5ZLkd2X3psBrjB"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

patch_payload = {
    "rootDir": "backend",
    "serviceDetails": {
        "envSpecificDetails": {
            "buildCommand": "pip install -r requirements.txt",
            "startCommand": 'sh -c "uvicorn main:app --host 0.0.0.0 --port $PORT"'
        }
    }
}

r = requests.patch("https://api.render.com/v1/services/srv-d9kotttbedkc73b632ig", json=patch_payload, headers=headers)
print("PATCH STATUS:", r.status_code)
print("PATCH RESP:", r.json())

d = requests.post("https://api.render.com/v1/services/srv-d9kotttbedkc73b632ig/deploys", headers=headers)
print("NEW DEPLOY ID:", d.json().get("id"))
