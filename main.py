 from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import json
import os
import random

app = FastAPI()

ADMIN_KEY = "TURFAI-ADMIN-2026"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "database.json"
HISTORY_FILE = "history.json"

def load_json(file, default):
    if not os.path.exists(file):
        return default
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def generate():
    chevaux = list(range(1, 21))
    random.shuffle(chevaux)
    return chevaux

@app.get("/quinte")
def quinte():
    prediction = generate()
    history = load_json(HISTORY_FILE, [])
    today = datetime.now().strftime("%Y-%m-%d")

    if not any(h["date"] == today for h in history):
        history.insert(0, {
            "date": today,
            "prediction": prediction[:5]
        })
        save_json(HISTORY_FILE, history)

    return {"prediction": prediction}

@app.get("/history")
def history():
    return load_json(HISTORY_FILE, [])[:10]

@app.get("/premium")
def premium(key: str):
    if key == ADMIN_KEY:
        return {"access": True}

    users = load_json(DB_FILE, {})

    if key not in users:
        return {"access": False}

    expire = datetime.fromisoformat(users[key]["expires"])
    return {"access": expire > datetime.now()}

@app.post("/payment-success")
async def payment(request: Request):
    data = await request.json()

    user = data.get("user_id")
    ref = data.get("ref")

    if not user:
        return {"error": "no user"}

    users = load_json(DB_FILE, {})
    now = datetime.now()

    users[user] = {
        "expires": (now + timedelta(days=30)).isoformat(),
        "referrals": users.get(user, {}).get("referrals", 0)
    }

    if ref and ref in users:
        users[ref]["referrals"] = users[ref].get("referrals", 0) + 1

    save_json(DB_FILE, users)

    return {"ok": True}

@app.get("/")
def home():
    return {"status": "OK"}
