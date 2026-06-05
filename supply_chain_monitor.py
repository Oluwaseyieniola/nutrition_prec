import streamlit as st
import pandas as pd
import numpy as np
import datetime
from dataclasses import dataclass
import random  # ✅ FIX: needed for allergy sampling

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
    for k in ["users", "history", "habits"]:
        if k not in st.session_state:
            st.session_state[k] = []

init()

# =========================================================
# SAFE OPTIONS
# =========================================================
ALLERGY_OPTIONS = [
    [],
    ["nuts"],
    ["gluten"],
    ["dairy"]
]

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
    "Salmon": {"goal": ["fitness", "glucose_control"], "category": ["RECOVERY_SUPPORT", "ANTI_INFLAMMATORY"], "desc": "Omega-3 rich recovery food"},
    "Oats": {"goal": ["glucose_control"], "category": ["GLUCOSE_STABILIZING", "MICROBIOME_SUPPORT"], "desc": "Stable energy carbohydrates"},
    "Eggs": {"goal": ["fitness"], "category": ["RECOVERY_SUPPORT"], "desc": "Complete protein source"},
    "Spinach": {"goal": ["glucose_control"], "category": ["ANTI_INFLAMMATORY", "MICROBIOME_SUPPORT"], "desc": "Micronutrient dense greens"},
    "Chicken Breast": {"goal": ["fitness", "fat_loss"], "category": ["RECOVERY_SUPPORT"], "desc": "Lean protein"},
    "Avocado": {"goal": ["fat_loss"], "category": ["ANTI_INFLAMMATORY"], "desc": "Healthy fats"},
    "Blueberries": {"goal": ["glucose_control"], "category": ["COGNITIVE_SUPPORT", "ANTI_INFLAMMATORY"], "desc": "Antioxidant support"}
}

# =========================================================
# BASE NUTRITION
# =========================================================
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
# NUTRIENT SENSITIVITY
# =========================================================
NUTRIENT_SENSITIVITY = {
    "vitamin_c": 1.8,
    "polyphenols": 1.6,
    "omega3": 1.5,
    "vitamin_d": 1.3,
    "antioxidants": 1.6,
    "healthy_fats": 1.2,
    "magnesium": 0.5,
    "protein": 0.3,
    "fiber": 0.4
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
    warehouse_days: int
    humidity_exposure: float
    processing_level: float
    contamination_risk: float
    cold_chain_breaks: int

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
        warehouse_days=int(rng.integers(1,7)),
        humidity_exposure=round(rng.uniform(0.2,0.9),2),
        processing_level=round(rng.uniform(0.0,0.6),2),
        contamination_risk=round(rng.uniform(0.0,0.4),2),
        cold_chain_breaks=int(rng.integers(0,3))
    )

# =========================================================
# USER CREATION (FIXED ALLERGY BUG HERE)
# =========================================================
def create_user(weight, height, goal):
    uid = len(st.session_state.users) + 1

    st.session_state.users.append({
        "id": uid,
        "weight": weight,
        "height": height,
        "goal": goal,
        "bmi": round(weight / (height ** 2), 1),

        "dietary_behavior": {
            "hydration_level": round(np.random.uniform(0.4, 1.0), 2),
            "cravings": np.random.choice(["sugar","fat","carbs","balanced"]),
            "alcohol_use": np.random.choice(["none","low","moderate"]),
            "smoking": bool(np.random.choice([True, False])),
            "food_discipline": round(np.random.uniform(0.3, 1.0), 2),
            "meal_regularity": round(np.random.uniform(0.4, 1.0), 2)
        },

        "medical_history": {
            "diabetes_risk": round(np.random.uniform(0, 1), 2),
            "hypertension_risk": round(np.random.uniform(0, 1), 2),
            "cholesterol_risk": round(np.random.uniform(0, 1), 2),

            # ✅ FIX: replaced np.random.choice on nested list
            "food_allergies": random.choice(ALLERGY_OPTIONS)
        },

        "microbiome": {
            "diversity_score": round(np.random.uniform(0.3, 1.0), 2),
            "inflammation_level": round(np.random.uniform(0, 1), 2),
            "fiber_response": round(np.random.uniform(0, 1), 2),
            "sugar_sensitivity": round(np.random.uniform(0, 1), 2)
        },

        "family_history": {
            "diabetes": round(np.random.uniform(0, 1), 2),
            "heart_disease": round(np.random.uniform(0, 1), 2),
            "obesity": round(np.random.uniform(0, 1), 2)
        }
    })

# =========================================================
# WEARABLE ENGINE
# =========================================================
def wearable(uid):
    rng = np.random.default_rng(uid)
    return {
        "sleep": round(rng.uniform(5,8),2),
        "recovery": int(rng.uniform(30,95)),
        "strain": round(rng.uniform(5,18),1),
        "glucose_variability": round(rng.uniform(10,40),1),
        "hrv": int(rng.uniform(20,90))
    }

# =========================================================
# UI
# =========================================================
st.title("🧠 Precision Nutrition Intelligence")

page = st.sidebar.radio(
    "Pages",
    ["Create User", "Health Insights", "Recommendations", "Food Intelligence"]
)

# =========================================================
# CREATE USER
# =========================================================
if page == "Create User":
    weight = st.number_input("Weight", 40.0, 200.0, 75.0)
    height = st.number_input("Height", 1.2, 2.5, 1.75)
    goal = st.selectbox("Goal", ["fitness", "fat_loss", "glucose_control"])

    if st.button("Create User"):
        create_user(weight, height, goal)
        st.success("User Created")

# =========================================================
# HEALTH INSIGHTS
# =========================================================
elif page == "Health Insights":
    users = pd.DataFrame(st.session_state.users or [])
    if users.empty:
        st.stop()

    uid = st.selectbox("User", users["id"])
    user = users[users["id"] == uid].iloc[0].to_dict()

    wear = wearable(uid)

    st.subheader("Wearable Intelligence")

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("BMI", user["bmi"])
    c2.metric("Sleep", wear["sleep"])
    c3.metric("Recovery", wear["recovery"])
    c4.metric("HRV", wear["hrv"])
    c5.metric("Glucose Variability", wear["glucose_variability"])

# =========================================================
# FOOD INTELLIGENCE
# =========================================================
elif page == "Food Intelligence":
    food = st.selectbox("Food", FOODS)

    telemetry = fetch_supply_chain_data(food)

    c1,c2,c3 = st.columns(3)
    c1.metric("Farm ID", telemetry.farm_id)

    # ✅ FIX: datetime converted to string (Streamlit bug fix)
    c1.metric("Harvest Date", str(telemetry.harvest_date))

    c2.metric("Transport Temp", f"{telemetry.avg_transport_temp}°C")
    c2.metric("Delay Hours", telemetry.transport_delay_hours)
    c3.metric("Cold Chain Breaks", telemetry.cold_chain_breaks)
    c3.metric("Contamination Risk", round(telemetry.contamination_risk,2))

    st.metric("Food Integrity", 100)
