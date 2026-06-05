import streamlit as st
import pandas as pd
import numpy as np
import datetime
import random
from dataclasses import dataclass

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Precision Nutrition Intelligence",
    layout="wide"
)

# =========================================================
# SESSION STATE
# =========================================================
def init():
    if "users" not in st.session_state:
        st.session_state.users = []

init()

# =========================================================
# FOOD DOMAIN
# =========================================================
FOODS = [
    "Salmon",
    "Oats",
    "Eggs",
    "Spinach",
    "Chicken Breast",
    "Avocado",
    "Blueberries"
]

# =========================================================
# FOOD KNOWLEDGE
# =========================================================
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
# BASE NUTRITION
# =========================================================
BASE_NUTRITION = {
    "Salmon": {"protein": 25, "omega3": 100, "vitamin_d": 90, "cal": 208},
    "Oats": {"fiber": 85, "protein": 17, "magnesium": 70, "cal": 389},
    "Eggs": {"protein": 12, "b12": 70, "cal": 155},
    "Spinach": {"magnesium": 95, "iron": 90, "cal": 23},
    "Chicken Breast": {"protein": 31, "selenium": 55, "cal": 165},
    "Avocado": {"healthy_fats": 90, "fiber": 65, "cal": 160},
    "Blueberries": {"polyphenols": 100, "vitamin_c": 80, "cal": 57}
}

# =========================================================
# NUTRIENT EFFECTS
# =========================================================
NUTRIENT_EFFECTS = {
    "omega3": ["Reduces inflammation", "Supports heart health"],
    "protein": ["Muscle repair", "Satiety support"],
    "fiber": ["Gut health", "Glucose stability"],
    "magnesium": ["Sleep support", "Recovery support"],
    "vitamin_c": ["Immune support"],
    "healthy_fats": ["Hormone balance"],
    "polyphenols": ["Anti-oxidative protection"]
}

# =========================================================
# TELEMETRY MODEL
# =========================================================
@dataclass
class SupplyTelemetry:
    farm_id: str
    harvest_date: datetime.date
    soil_quality: float
    pesticide_score: float
    avg_transport_temp: float
    transport_delay_hours: int
    processing_level: float
    contamination_risk: float

# =========================================================
# MOCK SUPPLY CHAIN
# =========================================================
def fetch_supply_chain_data(food):
    rng = np.random.default_rng(abs(hash(food)) % 10000)

    return SupplyTelemetry(
        farm_id=f"FARM-{rng.integers(100,999)}",
        harvest_date=datetime.date.today() - datetime.timedelta(days=int(rng.integers(1,10))),
        soil_quality=round(rng.uniform(0.6,1.0),2),
        pesticide_score=round(rng.uniform(0.0,0.4),2),
        avg_transport_temp=round(rng.uniform(2,15),1),
        transport_delay_hours=int(rng.integers(0,20)),
        processing_level=round(rng.uniform(0.0,0.6),2),
        contamination_risk=round(rng.uniform(0.0,0.4),2),
    )

# =========================================================
# USER CREATION (NEW SCHEMA)
# =========================================================
def create_user(data):
    data["id"] = len(st.session_state.users) + 1
    st.session_state.users.append(data)

# =========================================================
# RISK ENGINE (UPDATED TO NEW SCHEMA)
# =========================================================
def biological_risk(user):
    risk = 0
    reasons = []

    lifestyle = user["lifestyle"]
    medical = user["medical_history"]
    family = user["family_history"]
    wearable = user["wearable_data"]

    if lifestyle["smoking"]:
        risk += 2; reasons.append("Smoking detected")

    if lifestyle["alcohol_use"] == "high":
        risk += 1.5; reasons.append("High alcohol intake")

    if wearable["sleep_hours"] < 6:
        risk += 1.5; reasons.append("Low sleep")

    if medical["conditions"]:
        if "diabetes" in medical["conditions"]:
            risk += 2; reasons.append("Diabetes condition")

    if family["diabetes"]:
        risk += 1.5; reasons.append("Family diabetes risk")

    if wearable["hrv"] < 40:
        risk += 1; reasons.append("Low HRV")

    if risk > 5:
        return "HIGH", reasons
    elif risk > 2.5:
        return "MODERATE", reasons
    return "LOW", reasons

# =========================================================
# NUTRIENT ADJUSTMENT
# =========================================================
def adjusted_nutrients(food, telemetry):
    base = BASE_NUTRITION[food]
    adjusted = {}

    heat = telemetry.avg_transport_temp / 10
    delay = telemetry.transport_delay_hours / 24
    process = telemetry.processing_level

    for nutrient, value in base.items():
        degradation = heat * 0.2 + delay * 0.15 + process * 0.25
        retention = max(0.2, 1 - degradation)

        adjusted[nutrient] = {
            "remaining": round(value * retention,1),
            "retention": round(retention * 100,1)
        }

    return adjusted

# =========================================================
# FOOD SCORE ENGINE
# =========================================================
def food_score(food, user):
    score = 50

    if user["dietary_preferences"]["goal"] in FOOD_LIBRARY[food]["goal"]:
        score += 25

    if user["wearable_data"]["recovery_score"] < 50:
        score += 10

    if user["wearable_data"]["hrv"] < 50:
        score += 10

    return score

# =========================================================
# UI
# =========================================================
st.title("🧠 Precision Nutrition Intelligence")

page = st.sidebar.radio(
    "Pages",
    ["Create User", "Health Insights", "Food Intelligence"]
)

# =========================================================
# CREATE USER (NEW FORM)
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

        activity = st.selectbox("Activity Level", ["low","moderate","high"])

        smoking = st.radio("Smoking", ["no","yes"]) == "yes"
        alcohol = st.selectbox("Alcohol", ["none","low","moderate","high"])

        conditions = st.multiselect(
            "Medical Conditions",
            ["diabetes","hypertension","asthma","none"]
        )

        fam_diabetes = st.radio("Family Diabetes", ["no","yes"]) == "yes"

        goal = st.selectbox("Goal", ["fitness","fat_loss","glucose_control"])
        allergies = st.multiselect("Allergies", ["nuts","gluten","dairy"])

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
                    "recovery_score": recovery,
                    "activity": activity
                },
                "lifestyle": {
                    "smoking": smoking,
                    "alcohol_use": alcohol
                },
                "medical_history": {
                    "conditions": conditions,
                    "allergies": allergies
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
# HEALTH INSIGHTS
# =========================================================
elif page == "Health Insights":

    if not st.session_state.users:
        st.warning("No users yet")
        st.stop()

    uid = st.selectbox("User", range(len(st.session_state.users)))
    user = st.session_state.users[uid]

    risk, reasons = biological_risk(user)

    st.subheader("Risk Profile")
    st.write(risk)
    st.write(reasons)

# =========================================================
# FOOD INTELLIGENCE
# =========================================================
elif page == "Food Intelligence":

    food = st.selectbox("Food", FOODS)
    user = st.session_state.users[0] if st.session_state.users else None

    if not user:
        st.warning("Create a user first")
        st.stop()

    telemetry = fetch_supply_chain_data(food)

    st.subheader("Supply Chain")
    st.write(telemetry)

    st.subheader("Food Score")
    st.write(food_score(food, user))

    st.subheader("Nutrition (simplified)")
    st.write(adjusted_nutrients(food, telemetry))
