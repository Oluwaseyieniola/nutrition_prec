import streamlit as st
import pandas as pd
import numpy as np
import datetime
import random

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Precision Nutrition Intelligence", layout="wide")

# =========================================================
# SESSION STATE
# =========================================================
def init():
    if "users" not in st.session_state:
        st.session_state.users = []

init()

# =========================================================
# FOOD SYSTEM
# =========================================================
FOODS = [
    "Salmon", "Oats", "Eggs", "Spinach",
    "Chicken Breast", "Avocado", "Blueberries"
]

FOOD_LIBRARY = {
    "Salmon": {"goal": ["fitness", "glucose_control"], "desc": "Omega-3 rich recovery food"},
    "Oats": {"goal": ["glucose_control"], "desc": "Stable energy carbohydrates"},
    "Eggs": {"goal": ["fitness"], "desc": "Complete protein source"},
    "Spinach": {"goal": ["glucose_control"], "desc": "Micronutrient dense greens"},
    "Chicken Breast": {"goal": ["fitness", "fat_loss"], "desc": "Lean protein"},
    "Avocado": {"goal": ["fat_loss"], "desc": "Healthy fats"},
    "Blueberries": {"goal": ["glucose_control"], "desc": "Antioxidant support"}
}

# =========================================================
# SUPPLY CHAIN (CACHED + CLEAN)
# =========================================================
@st.cache_data
def fetch_supply_chain_data(food):
    rng = np.random.default_rng(abs(hash(food)) % 10000)

    return {
        "farm_id": f"FARM-{rng.integers(100,999)}",
        "harvest_date": datetime.date.today() - datetime.timedelta(days=int(rng.integers(1,10))),
        "soil_quality": float(rng.uniform(0.6, 1.0)),
        "pesticide_score": float(rng.uniform(0.0, 0.4)),
        "avg_transport_temp": float(rng.uniform(2, 15)),
        "transport_delay_hours": int(rng.integers(0, 20)),
        "processing_level": float(rng.uniform(0.0, 0.6)),
        "contamination_risk": float(rng.uniform(0.0, 0.4)),
    }

# =========================================================
# USER CREATION
# =========================================================
def create_user(user):
    user["id"] = len(st.session_state.users) + 1
    st.session_state.users.append(user)

# =========================================================
# RISK ENGINE
# =========================================================
def biological_risk(user):
    risk = 0
    reasons = []

    lifestyle = user["lifestyle"]
    medical = user["medical_history"]
    wearable = user["wearable_data"]

    if lifestyle["smoking"]:
        risk += 2
        reasons.append("Smoking detected")

    if lifestyle["alcohol_use"] == "high":
        risk += 1.5
        reasons.append("High alcohol intake")

    if wearable["sleep_hours"] < 6:
        risk += 1.5
        reasons.append("Low sleep")

    if wearable["hrv"] < 40:
        risk += 1
        reasons.append("Low HRV")

    if "diabetes" in medical["conditions"]:
        risk += 2
        reasons.append("Diabetes condition")

    if risk > 5:
        return "HIGH", reasons
    elif risk > 2.5:
        return "MODERATE", reasons
    return "LOW", reasons

# =========================================================
# SCORE ENGINE (REAL LOGIC)
# =========================================================
def food_score(food, user, telemetry):

    score = 50

    prefs = user["dietary_preferences"]
    wear = user["wearable_data"]
    lifestyle = user["lifestyle"]
    medical = user["medical_history"]

    # goal alignment
    if prefs["goal"] in FOOD_LIBRARY[food]["goal"]:
        score += 25

    # wearable signals
    if wear["recovery_score"] < 50:
        score += 10
    if wear["hrv"] < 50:
        score += 10
    if wear["sleep_hours"] < 6:
        score -= 10

    # lifestyle penalties
    if lifestyle["smoking"]:
        score -= 10
    if lifestyle["alcohol_use"] == "high":
        score -= 5

    # medical interaction
    if "diabetes" in medical["conditions"] and food in ["Oats", "Blueberries"]:
        score -= 5

    # supply chain quality
    integrity = compute_integrity_score(telemetry)
    score += integrity * 0.2

    return round(max(min(score, 100), 0), 1)

# =========================================================
# SUPPLY CHAIN SCORE
# =========================================================
def compute_integrity_score(t):
    score = 100
    score -= t["processing_level"] * 20
    score -= t["contamination_risk"] * 25
    score -= t["transport_delay_hours"] * 0.5
    score += t["soil_quality"] * 10
    score -= t["pesticide_score"] * 15
    return round(max(min(score, 100), 0), 1)

# =========================================================
# UI
# =========================================================
st.title("🧠 Precision Nutrition Intelligence")

page = st.sidebar.radio(
    "Pages",
    ["Create User", "Health Insights", "Food Intelligence"]
)

# =========================================================
# CREATE USER (FULL SCHEMA)
# =========================================================
if page == "Create User":

    st.subheader("Create Health Profile")

    with st.form("user_form"):

        age = st.number_input("Age", 1, 120, 25)
        sex = st.selectbox("Sex", ["male", "female", "other"])
        country = st.text_input("Country", "Nigeria")
        region = st.text_input("Region", "Lagos")

        weight = st.number_input("Weight (kg)", 30.0, 250.0, 75.0)
        height = st.number_input("Height (m)", 1.0, 2.5, 1.75)
        bmi = round(weight / (height ** 2), 1)

        heart_rate = st.number_input("Heart Rate", 40, 200, 72)
        hrv = st.number_input("HRV", 10, 120, 55)
        sleep = st.number_input("Sleep (hrs)", 0.0, 12.0, 7.0)
        recovery = st.slider("Recovery Score", 0, 100, 70)

        smoking = st.radio("Smoking", ["no", "yes"]) == "yes"
        alcohol = st.selectbox("Alcohol Use", ["none", "low", "moderate", "high"])

        conditions = st.multiselect(
            "Medical Conditions",
            ["diabetes", "hypertension", "asthma", "none"]
        )

        fam_diabetes = st.radio("Family Diabetes", ["no", "yes"]) == "yes"

        goal = st.selectbox("Goal", ["fitness", "fat_loss", "glucose_control"])

        submitted = st.form_submit_button("Create User")

        if submitted:

            user = {
                "demographics": {
                    "age": age,
                    "sex": sex,
                    "country": country,
                    "region": region
                },
                "anthropometrics": {
                    "weight": weight,
                    "height": height,
                    "bmi": bmi
                },
                "wearable_data": {
                    "heart_rate": heart_rate,
                    "hrv": hrv,
                    "sleep_hours": sleep,
                    "recovery_score": recovery
                },
                "lifestyle": {
                    "smoking": smoking,
                    "alcohol_use": alcohol
                },
                "medical_history": {
                    "conditions": conditions
                },
                "family_history": {
                    "diabetes": fam_diabetes
                },
                "dietary_preferences": {
                    "goal": goal
                }
            }

            create_user(user)
            st.success("User created successfully")

# =========================================================
# HEALTH INSIGHTS (FIXED + STRUCTURED)
# =========================================================
elif page == "Health Insights":

    if not st.session_state.users:
        st.warning("No users available")
        st.stop()

    user = st.session_state.users[st.selectbox("Select User", range(len(st.session_state.users)))]

    st.subheader("Demographics")
    st.json(user["demographics"])

    st.subheader("Body")
    st.json(user["anthropometrics"])

    st.subheader("Wearables")
    st.json(user["wearable_data"])

    st.subheader("Lifestyle")
    st.json(user["lifestyle"])

    st.subheader("Medical History")
    st.json(user["medical_history"])

    risk, reasons = biological_risk(user)

    st.subheader("Risk Engine")
    st.metric("Risk Level", risk)

    for r in reasons:
        st.write("•", r)

# =========================================================
# FOOD INTELLIGENCE (RECOMMENDATION SYSTEM FIXED)
# =========================================================
elif page == "Food Intelligence":

    if not st.session_state.users:
        st.warning("Create a user first")
        st.stop()

    user = st.session_state.users[st.selectbox("Select User", range(len(st.session_state.users)))]

    results = []

    for food in FOODS:

        telemetry = fetch_supply_chain_data(food)

        score = food_score(food, user, telemetry)

        results.append({
            "food": food,
            "score": score,
            "telemetry": telemetry
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    st.subheader("Ranked Recommendations")

    for r in results:

        t = r["telemetry"]

        with st.container(border=True):

            st.subheader(f"{r['food']} — Score: {r['score']}")
            st.write(FOOD_LIBRARY[r["food"]]["desc"])

            c1, c2, c3 = st.columns(3)

            c1.metric("Farm", t["farm_id"])
            c1.metric("Harvest", str(t["harvest_date"]))

            c2.metric("Temp", f"{t['avg_transport_temp']:.1f}°C")
            c2.metric("Delay", t["transport_delay_hours"])

            c3.metric("Contamination", round(t["contamination_risk"], 2))
            c3.metric("Processing", round(t["processing_level"], 2))
