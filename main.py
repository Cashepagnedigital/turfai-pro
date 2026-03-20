 from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import json
import os
import random

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "database.json"

# ========================
# UTILS
# ========================

def load_json():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_json(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ========================
# QUINTE
# ========================

@app.get("/quinte")
def quinte():
    chevaux = list(range(1, 21))
    random.shuffle(chevaux)
    return {"prediction": chevaux[:5]}

# ========================
# HISTORIQUE
# ========================

@app.get("/history")
def history():
    return [
        {
            "date": datetime.now().isoformat(),
            "prediction": random.sample(range(1, 21), 5)
        }
    ]

# ========================
# PREMIUM
# ========================

@app.get("/premium")
def premium(key: str):
    users = load_json()

    if key not in users:
        return {"access": False}

    expire = datetime.fromisoformat(users[key]["expires"])
    return {"access": expire > datetime.now()}

# ========================
# PAYMENT
# ========================

@app.post("/payment-success")
async def payment(request: Request):
    data = await request.json()

    user_id = data.get("user_id")
    ref = data.get("ref")

    users = load_json()
    now = datetime.now()

    if user_id not in users:
        users[user_id] = {
            "expires": (now + timedelta(days=30)).isoformat(),
            "referrals": 0
        }
    else:
        users[user_id]["expires"] = (
            datetime.fromisoformat(users[user_id]["expires"]) + timedelta(days=30)
        ).isoformat()

    if ref and ref in users:
        users[ref]["referrals"] += 1

    save_json(users)

    return {"status": "OK"}

# ========================
# ROOT
# ========================

@app.get("/")
def home():
    return {"status": "OK"}
