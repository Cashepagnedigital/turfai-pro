 from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import json
import os
import random

app = FastAPI()

# ========================
# 🔐 CLÉ ADMIN PRIVÉE
# ========================
ADMIN_KEY = "TURFAI-ADMIN-2026"

# ========================
# CORS
# ========================
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

def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ========================
# PRONOSTIC
# ========================

def generate_prediction():
    chevaux = list(range(1, 21))
    random.shuffle(chevaux)
    return chevaux

# ========================
# GRATUIT
# ========================

@app.get("/quinte")
def quinte():
    prediction = generate_prediction()
    return {
        "prediction": prediction
    }

# ========================
# VIP + ADMIN
# ========================

@app.get("/premium")
def premium(key: str):

    # ✅ ACCÈS ADMIN TOTAL
    if key == ADMIN_KEY:
        return {
            "access": True,
            "admin": True
        }

    users = load_users()

    if key not in users:
        return {"access": False}

    expire = datetime.fromisoformat(users[key]["expires"])

    if expire > datetime.now():
        return {"access": True}
    else:
        return {"access": False}

# ========================
# STATS
# ========================

@app.get("/user-stats")
def stats(key: str):
    users = load_users()

    if key not in users:
        return {"referrals": 0}

    return {
        "referrals": users[key].get("referrals", 0)
    }

# ========================
# PAIEMENT CHARIOW
# ========================

@app.post("/payment-success")
async def payment_success(request: Request):
    data = await request.json()

    user_id = data.get("user_id") or data.get("metadata", {}).get("user_id")
    ref = data.get("ref") or data.get("metadata", {}).get("ref")

    if not user_id:
        return {"error": "user_id manquant"}

    users = load_users()
    now = datetime.now()

    # Activation VIP 30 jours
    if user_id not in users:
        users[user_id] = {
            "expires": (now + timedelta(days=30)).isoformat(),
            "referrals": 0
        }
    else:
        users[user_id]["expires"] = (
            datetime.fromisoformat(users[user_id]["expires"]) + timedelta(days=30)
        ).isoformat()

    # Parrainage
    if ref and ref in users:
        users[ref]["referrals"] = users[ref].get("referrals", 0) + 1

    save_users(users)

    return {"status": "OK"}

# ========================
# ROOT
# ========================

@app.get("/")
def home():
    return {"status": "TurfAI Pro Backend OK"}
