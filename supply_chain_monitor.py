import streamlit as st
import pandas as pd
import numpy as np
import datetime
from dataclasses import dataclass

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Precision Nutrition Intelligence",
    layout="wide"
)

# =========================================================
# SESSION INIT
# =========================================================
def init():
    keys = ["users", "history", "habits", "biomarkers", "food_logs", "lab_results"]

    for k in keys:
        if k not in st.session_state:
            st.session_state[k] = []

init()

# =========================================================
# FOOD DOMAIN
# =========================================================
FOODS = ["Salmon", "Oats", "Eggs", "Spinach", "Chicken Breast", "Avocado", "Blueberries"]

FOOD_LIBRARY = {
    "Salmon": {"goal": ["fitness", "glucose_control"], "category": ["RECOVERY_SUPPORT", "ANTI_INFLAMMATORY"], "desc": "Omega-3 rich recovery food"},
    "Oats": {"goal": ["glucose_control"], "category": ["GLUCOSE_STABILIZING", "MICROBIOME_SUPPORT"], "desc": "Stable energy carbohydrates"},
    "Eggs": {"goal": ["fitness"], "category": ["RECOVERY_SUPPORT"], "desc": "Complete protein source"},
    "Spinach": {"goal": ["glucose_control"], "category": ["MICROBIOME_SUPPORT", "ANTI_INFLAMMATORY"], "desc": "Micronutrient dense greens"},
    "Chicken Breast": {"goal": ["fitness", "fat_loss"], "category": ["RECOVERY_SUPPORT"], "desc": "Lean protein support"},
    "Avocado": {"goal": ["fat_loss"], "category": ["ANTI_INFLAMMATORY"], "desc": "Healthy fats"},
    "Blueberries": {"goal": ["glucose_control"], "category": ["COGNITIVE_SUPPORT", "ANTI_INFLAMMATORY"], "desc": "Antioxidant support"}
}

BASE_NUTRITION = {
    "Salmon": {"protein": 25, "omega3": 100, "vitamin_d": 90, "selenium": 75, "b12": 85, "cal": 208},
    "Oats": {"fiber": 85, "protein": 17, "magnesium": 70, "beta_glucan": 95, "polyphenols": 55, "cal": 389},
    "Eggs": {"protein": 12, "b12": 70, "choline": 88, "selenium": 60, "vitamin_d": 50, "cal": 155},
    "Spinach": {"magnesium": 95, "iron": 90, "folate": 88, "fiber": 70, "vitamin_k": 100, "cal": 23},
    "Chicken Breast": {"protein": 31, "selenium": 55, "b6": 60, "niacin": 70, "cal": 165},
    "Avocado": {"healthy_fats": 90, "fiber": 65, "potassium": 80, "folate": 50, "cal": 160},
    "Blueberries": {"polyphenols": 100, "vitamin_c": 80, "fiber": 45, "antioxidants": 100, "cal": 57}
}

# =========================================================
# WEARABLE STREAM (UPGRADED)
# =========================================================
def wearable_stream(uid):
    rng = np.random.default_rng(uid)

    sleep = rng.normal(7, 1)
    stress = rng.uniform(3, 9)
    steps = rng.uniform(2000, 12000)

    sleep_debt = max(0, 8 - sleep)

    recovery = max(0, 100 - (stress * 8 + sleep_debt * 10))
    glucose_variability = rng.uniform(10, 45)

    return {
        "sleep_hours": round(sleep, 2),
        "sleep_debt": round(sleep_debt, 2),
        "stress": round(stress, 2),
        "activity_steps": int(steps),
        "recovery": round(recovery, 1),
        "glucose_variability": round(glucose_variability, 1)
    }

# =========================================================
# METABOLIC STATE ENGINE
# =========================================================
def metabolic_state(user, wear):
    score = 100
    flags = []

    if wear["sleep_debt"] > 1.5:
        score -= 15
        flags.append("Sleep Debt")

    if wear["stress"] > 7:
        score -= 10
        flags.append("High Stress")

    if wear["activity_steps"] < 4000:
        score -= 10
        flags.append("Low Activity")

    if wear["recovery"] < 50:
        score -= 20
        flags.append("Low Recovery")

    if wear["glucose_variability"] > 35:
        score -= 15
        flags.append("Glucose Instability")

    return {
        "state_score": max(0, score),
        "state_flags": flags,
        "state_label": "OPTIMAL" if score > 80 else "STABLE" if score > 60 else "DYSREGULATED"
    }

# =========================================================
# SUPPLY CHAIN SIMULATION
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

def fetch_supply_chain_data(food):
    rng = np.random.default_rng(abs(hash(food)) % 10000)

    return SupplyTelemetry(
        farm_id=f"FARM-{rng.integers(100,999)}",
        harvest_date=datetime.date.today() - datetime.timedelta(days=int(rng.integers(1,10))),
        soil_quality=round(rng.uniform(0.6,1.0),2),
        pesticide_score=round(rng.uniform(0.0,0.4),2),
        avg_transport_temp=round(rng.uniform(2,15),1),
        transport_delay_hours=int(rng.integers(0,20)),
        warehouse_days=int(rng.integers(1,7)),
        humidity_exposure=round(rng.uniform(0.2,0.9),2),
        processing_level=round(rng.uniform(0.0,0.6),2),
        contamination_risk=round(rng.uniform(0.0,0.4),2),
        cold_chain_breaks=int(rng.integers(0,3))
    )

# =========================================================
# HEALTH ENGINE (UPGRADED)
# =========================================================
def health_score(user, wear):
    meta = metabolic_state(user, wear)

    score = 0
    reasons = []

    if user["bmi"] > 27:
        score += 2
        reasons.append("Elevated BMI")

    if user.get("waist_circumference", 0) > 102:
        score += 2
        reasons.append("Central adiposity risk")

    if wear["recovery"] < 50:
        score += 2
        reasons.append("Low recovery capacity")

    if meta["state_score"] < 60:
        score += 3
        reasons.extend(meta["state_flags"])

    risk = "LOW" if score < 3 else "MODERATE" if score < 6 else "HIGH"

    return risk, reasons, meta

# =========================================================
# NUTRIENT ENGINE
# =========================================================
def adjusted_nutrients(food, telemetry):
    base = BASE_NUTRITION[food]
    adjusted = {}

    for nutrient, value in base.items():
        degradation = (
            telemetry.avg_transport_temp / 10 * 0.2 +
            telemetry.transport_delay_hours / 24 * 0.15 +
            telemetry.processing_level * 0.25
        )

        retention = max(0.2, 1 - degradation)

        adjusted[nutrient] = {
            "remaining": round(value * retention, 1),
            "retention_percent": round(retention * 100, 1)
        }

    return adjusted

# =========================================================
# RECOMMENDATION ENGINE (WHOLE FOOD OUTPUT)
# =========================================================
def food_recommendation(food, user, wear):
    telemetry = fetch_supply_chain_data(food)
    integrity = compute_integrity_score(telemetry)
    nutrients = adjusted_nutrients(food, telemetry)

    meta = metabolic_state(user, wear)

    score = 50
    if user["goal"] in FOOD_LIBRARY[food]["goal"]:
        score += 20

    score += integrity * 0.3

    explanation = (
        f"{food} is recommended based on your current metabolic state ({meta['state_label']}). "
        f"It has a supply chain integrity score of {integrity}/100, reflecting real-world handling conditions. "
        f"The food experienced {telemetry.transport_delay_hours}h transport delay and "
        f"{telemetry.avg_transport_temp}°C exposure. "
        f"Biologically, it supports: {', '.join(FOOD_LIBRARY[food]['category'])}."
    )

    return {
        "food": food,
        "score": round(score, 1),
        "integrity": integrity,
        "recommendation": explanation
    }

# =========================================================
# UI
# =========================================================
st.title("🧠 Precision Nutrition Intelligence")

page = st.sidebar.radio("Pages", ["Create User", "Health Insights", "Recommendations"])

# =========================================================
# CREATE USER
# =========================================================
if page == "Create User":

    st.subheader("Create Profile")

    weight = st.number_input("Weight", 40.0, 200.0, 75.0)
    height = st.number_input("Height", 1.2, 2.5, 1.75)
    waist = st.number_input("Waist (cm)", 50, 200, 90)
    goal = st.selectbox("Goal", ["fitness", "fat_loss", "glucose_control"])

    if st.button("Create"):
        uid = len(st.session_state.users) + 1
        st.session_state.users.append({
            "id": uid,
            "weight": weight,
            "height": height,
            "bmi": round(weight / (height ** 2), 1),
            "goal": goal,
            "waist_circumference": waist
        })
        st.success("User created")

# =========================================================
# HEALTH INSIGHTS
# =========================================================
elif page == "Health Insights":

    users = pd.DataFrame(st.session_state.users)
    if users.empty:
        st.stop()

    uid = st.selectbox("User", users.id)
    user = users[users.id == uid].iloc[0].to_dict()

    wear = wearable_stream(uid)
    risk, reasons, meta = health_score(user, wear)

    st.metric("Risk", risk)
    st.metric("Metabolic State", meta["state_label"])
    st.write(reasons)
    st.json(wear)

# =========================================================
# RECOMMENDATIONS
# =========================================================
elif page == "Recommendations":

    users = pd.DataFrame(st.session_state.users)
    if users.empty:
        st.stop()

    uid = st.selectbox("User", users.id)
    user = users[users.id == uid].iloc[0].to_dict()

    wear = wearable_stream(uid)

    recs = [food_recommendation(f, user, wear) for f in FOODS]
    recs = sorted(recs, key=lambda x: x["score"], reverse=True)

    for r in recs:
        with st.container(border=True):
            st.subheader(r["food"])
            st.write(r["recommendation"])
            st.metric("Score", r["score"])
            st.metric("Integrity", r["integrity"])
