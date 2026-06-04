import streamlit as st
import pandas as pd
import numpy as np
import datetime
import sqlite3
from dataclasses import dataclass
from typing import Dict, List, Any, Callable

# =========================================================
# APP CONFIG
# =========================================================
st.set_page_config(page_title="Precision Nutrition OS", layout="wide")

# =========================================================
# EVENT BUS (Kafka-like lightweight simulation)
# =========================================================
class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        self.subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event_type: str, payload: dict):
        for handler in self.subscribers.get(event_type, []):
            handler(payload)

bus = EventBus()

# =========================================================
# PERSISTENCE LAYER (SQLite)
# =========================================================
conn = sqlite3.connect("nutrition.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    weight REAL,
    height REAL,
    goal TEXT,
    bmi REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS interactions (
    user_id INTEGER,
    food TEXT,
    decision TEXT,
    timestamp TEXT
)
""")

conn.commit()

# =========================================================
# DOMAIN MODELS
# =========================================================
@dataclass
class SupplyTelemetry:
    farm_id: str
    harvest_date: datetime.date
    soil_quality: float
    pesticide_score: float
    avg_transport_temp: float
    transport_delay_hours: int
    warehouse_days: int
    humidity_exposure: float
    processing_level: float
    contamination_risk: float
    cold_chain_breaks: int

# =========================================================
# FOOD ONTOLOGY (PLUGIN READY)
# =========================================================
FOODS = ["Salmon", "Oats", "Eggs", "Spinach", "Chicken Breast", "Avocado", "Blueberries"]

FOOD_LIBRARY = {
    "Salmon": {"goal": ["fitness", "glucose_control"], "desc": "Omega-3 rich recovery food"},
    "Oats": {"goal": ["glucose_control"], "desc": "Stable energy carbohydrates"},
    "Eggs": {"goal": ["fitness"], "desc": "Complete protein source"},
    "Spinach": {"goal": ["glucose_control"], "desc": "Micronutrient dense greens"},
    "Chicken Breast": {"goal": ["fitness", "fat_loss"], "desc": "Lean protein support"},
    "Avocado": {"goal": ["fat_loss"], "desc": "Healthy fats"},
    "Blueberries": {"goal": ["glucose_control"], "desc": "Antioxidant support"},
}

BASE_NUTRITION = {
    k: {"protein": 10 + np.random.rand()*20} for k in FOODS
}

# =========================================================
# NUTRIENT REGISTRY (PLUGIN SYSTEM)
# =========================================================
NUTRIENT_EFFECTS = {
    "protein": ["Muscle repair", "Satiety improvement"]
}

# =========================================================
# RANDOMNESS SERVICE (non-deterministic but stable per session)
# =========================================================
def rng(seed):
    base = int(datetime.datetime.now().timestamp() // 120)
    return np.random.default_rng(hash(seed) + base)

# =========================================================
# LOGISTICS / SUPPLY CHAIN SERVICE
# =========================================================
def fetch_supply_chain_data(food):
    r = rng(food)

    return SupplyTelemetry(
        farm_id=f"FARM-{r.integers(100,999)}",
        harvest_date=datetime.date.today() - datetime.timedelta(days=int(r.integers(1,10))),
        soil_quality=float(r.uniform(0.6, 1.0)),
        pesticide_score=float(r.uniform(0.0, 0.4)),
        avg_transport_temp=float(r.uniform(2, 15)),
        transport_delay_hours=int(r.integers(0, 20)),
        warehouse_days=int(r.integers(1, 7)),
        humidity_exposure=float(r.uniform(0.2, 0.9)),
        processing_level=float(r.uniform(0.0, 0.6)),
        contamination_risk=float(r.uniform(0.0, 0.4)),
        cold_chain_breaks=int(r.integers(0, 3)),
    )

# =========================================================
# HEALTH SERVICE
# =========================================================
def wearable(uid):
    r = rng(uid)
    return {
        "sleep": float(r.uniform(5, 8)),
        "recovery": int(r.uniform(30, 95)),
        "glucose_variability": float(r.uniform(10, 40)),
        "hrv": int(r.uniform(20, 90)),
    }

def health_risk(user, wear):
    score = 0
    if user["bmi"] > 27: score += 2
    if wear["sleep"] < 6: score += 2
    if wear["recovery"] < 50: score += 2
    if wear["glucose_variability"] > 30: score += 2

    if score >= 6: return "HIGH"
    if score >= 3: return "MODERATE"
    return "LOW"

# =========================================================
# NUTRIENT ENGINE (retention simulation)
# =========================================================
def adjusted_nutrients(food, telemetry):
    base = BASE_NUTRITION[food]
    out = {}

    for n, v in base.items():
        degradation = (
            telemetry.avg_transport_temp * 0.02 +
            telemetry.transport_delay_hours * 0.01 +
            telemetry.processing_level * 0.2
        )

        retention = max(0.2, 1 - degradation)

        out[n] = {
            "remaining": round(v * retention, 2),
            "retention": round(retention * 100, 1)
        }

    return out

# =========================================================
# LOGISTICS SCORE
# =========================================================
def integrity_score(t):
    score = 100
    score -= t.transport_delay_hours * 0.5
    score -= t.processing_level * 20
    score -= t.contamination_risk * 25
    score += t.soil_quality * 10
    return max(0, min(100, score))

# =========================================================
# RECOMMENDATION MODEL (REAL SCORING MODEL)
# =========================================================
def score_food(user, wear, food, integrity):

    x = 0

    if user["goal"] in FOOD_LIBRARY[food]["goal"]:
        x += 2.0

    if wear["recovery"] < 50:
        x += 1.0

    if wear["glucose_variability"] > 30:
        x += 1.0

    # logistic normalization
    raw = x + (integrity / 100)

    return 1 / (1 + np.exp(-raw))

# =========================================================
# RECOMMENDATION SERVICE
# =========================================================
def recommend(user, uid):
    wear = wearable(uid)

    results = []

    for food in FOODS:
        t = fetch_supply_chain_data(food)
        integrity = integrity_score(t)
        nutrients = adjusted_nutrients(food, t)

        score = score_food(user, wear, food, integrity)

        results.append({
            "food": food,
            "score": score,
            "integrity": integrity,
            "telemetry": t,
            "nutrients": nutrients,
            "desc": FOOD_LIBRARY[food]["desc"]
        })

    df = pd.DataFrame(results).sort_values("score", ascending=False)
    return df, wear

# =========================================================
# EVENT HANDLERS
# =========================================================
def on_accept(event):
    cursor.execute(
        "INSERT INTO interactions VALUES (?, ?, ?, ?)",
        (event["user"], event["food"], "yes", str(datetime.datetime.now()))
    )
    conn.commit()

bus.subscribe("ACCEPT_FOOD", on_accept)

# =========================================================
# UI LAYER
# =========================================================
st.title("🧠 Precision Nutrition OS (Production Architecture)")

page = st.sidebar.radio("Pages", [
    "Create User",
    "Health",
    "Recommendations"
])

# -------------------------
# CREATE USER
# -------------------------
if page == "Create User":

    w = st.number_input("Weight", 40.0, 200.0, 70.0)
    h = st.number_input("Height", 1.2, 2.5, 1.75)
    g = st.selectbox("Goal", ["fitness", "fat_loss", "glucose_control"])

    if st.button("Create"):

        bmi = round(w / (h*h), 2)

        cursor.execute(
            "INSERT INTO users (weight, height, goal, bmi) VALUES (?, ?, ?, ?)",
            (w, h, g, bmi)
        )
        conn.commit()

        st.success("User stored in database")

# -------------------------
# HEALTH
# -------------------------
elif page == "Health":

    users = pd.read_sql("SELECT * FROM users", conn)

    if users.empty:
        st.stop()

    uid = st.selectbox("User", users.id)
    user = users[users.id == uid].iloc[0].to_dict()

    wear = wearable(uid)
    risk = health_risk(user, wear)

    st.metric("Risk", risk)
    st.json(wear)

# -------------------------
# RECOMMENDATIONS
# -------------------------
elif page == "Recommendations":

    users = pd.read_sql("SELECT * FROM users", conn)

    if users.empty:
        st.stop()

    uid = st.selectbox("User", users.id)
    user = users[users.id == uid].iloc[0].to_dict()

    recs, wear = recommend(user, uid)

    st.json(wear)

    for _, r in recs.iterrows():

        st.subheader(r.food)
        st.write(r.desc)

        st.metric("Score", round(r.score, 3))
        st.metric("Integrity", r.integrity)

        if st.button(f"Accept {r.food}", key=f"a{r.food}{uid}"):

            bus.publish("ACCEPT_FOOD", {
                "user": uid,
                "food": r.food
            })

            st.rerun()
