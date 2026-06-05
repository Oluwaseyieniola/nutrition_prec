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
    "Salmon": {
        "goal": ["fitness", "glucose_control"],
        "category": ["RECOVERY_SUPPORT", "ANTI_INFLAMMATORY"],
        "desc": "Omega-3 rich recovery food"
    },
    "Oats": {
        "goal": ["glucose_control"],
        "category": ["GLUCOSE_STABILIZING", "MICROBIOME_SUPPORT"],
        "desc": "Stable energy carbohydrates"
    },
    "Eggs": {
        "goal": ["fitness"],
        "category": ["RECOVERY_SUPPORT"],
        "desc": "Complete protein source"
    },
    "Spinach": {
        "goal": ["glucose_control"],
        "category": ["ANTI_INFLAMMATORY", "MICROBIOME_SUPPORT"],
        "desc": "Micronutrient dense greens"
    },
    "Chicken Breast": {
        "goal": ["fitness", "fat_loss"],
        "category": ["RECOVERY_SUPPORT"],
        "desc": "Lean protein"
    },
    "Avocado": {
        "goal": ["fat_loss"],
        "category": ["ANTI_INFLAMMATORY"],
        "desc": "Healthy fats"
    },
    "Blueberries": {
        "goal": ["glucose_control"],
        "category": ["COGNITIVE_SUPPORT", "ANTI_INFLAMMATORY"],
        "desc": "Antioxidant support"
    }
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
# NUTRIENT EFFECTS
# =========================================================
NUTRIENT_EFFECTS = {
    "omega3": ["Improves recovery", "Reduces inflammation", "Supports cardiovascular health"],
    "protein": ["Supports muscle repair", "Improves satiety"],
    "fiber": ["Stabilizes glucose", "Supports gut microbiome"],
    "polyphenols": ["Reduces oxidative stress", "Supports metabolic health"],
    "magnesium": ["Supports sleep quality", "Improves muscle recovery"],
    "vitamin_c": ["Supports immunity"],
    "healthy_fats": ["Supports hormone balance"],
    "antioxidants": ["Protects cells from stress", "Supports cognitive health"]
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
# USER CREATION
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
            "food_allergies": np.random.choice(ALLERGY_OPTIONS)
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
# BIOLOGICAL RISK
# =========================================================
def biological_risk(user):
    risk = 0
    reasons = []

    diet = user["dietary_behavior"]
    medical = user["medical_history"]
    micro = user["microbiome"]
    family = user["family_history"]

    if diet["hydration_level"] < 0.5:
        risk += 1.5; reasons.append("Low hydration")
    if diet["smoking"]:
        risk += 2; reasons.append("Smoking detected")
    if diet["alcohol_use"] == "moderate":
        risk += 1; reasons.append("Moderate alcohol intake")
    if medical["diabetes_risk"] > 0.6:
        risk += 2; reasons.append("Elevated diabetes risk")
    if medical["hypertension_risk"] > 0.6:
        risk += 1.5; reasons.append("Hypertension risk")
    if micro["inflammation_level"] > 0.6:
        risk += 2; reasons.append("Inflammatory microbiome")
    if micro["sugar_sensitivity"] > 0.6:
        risk += 1.5; reasons.append("Sugar sensitivity")
    if family["diabetes"] > 0.6:
        risk += 1.5; reasons.append("Family diabetes risk")
    if family["heart_disease"] > 0.6:
        risk += 1.5; reasons.append("Family heart disease risk")

    if risk > 5:
        return "HIGH", reasons
    elif risk > 2.5:
        return "MODERATE", reasons
    return "LOW", reasons

# =========================================================
# RETENTION ENGINE
# =========================================================
def adjusted_nutrients(food, telemetry):
    base = BASE_NUTRITION[food]
    adjusted = {}

    heat = telemetry.avg_transport_temp / 10
    delay = telemetry.transport_delay_hours / 24
    process = telemetry.processing_level

    for nutrient, value in base.items():
        sens = NUTRIENT_SENSITIVITY.get(nutrient, 1.0)

        degradation = (
            heat * 0.2 * sens +
            delay * 0.15 * sens +
            process * 0.25 * sens
        )

        retention = max(0.2, 1 - degradation)

        adjusted[nutrient] = {
            "remaining": round(value * retention,1),
            "retention_percent": round(retention * 100,1)
        }

    return adjusted

# =========================================================
# SCORE ENGINE
# =========================================================
def compute_integrity_score(t):
    score = 100
    score -= t.processing_level * 20
    score -= t.contamination_risk * 25
    score -= t.transport_delay_hours * 0.5
    score += t.soil_quality * 10
    score -= t.pesticide_score * 15
    return round(max(min(score,100),0),1)

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
    risk, reasons = biological_risk(user)

    st.subheader("Wearable Intelligence")
    c1,c2,c3,c4,c5 = st.columns(5)

    c1.metric("BMI", user["bmi"])
    c2.metric("Sleep", wear["sleep"])
    c3.metric("Recovery", wear["recovery"])
    c4.metric("HRV", wear["hrv"])
    c5.metric("Glucose Variability", wear["glucose_variability"])

    st.subheader("Biological Risk")
    st.write("Risk Level:", risk)
    for r in reasons:
        st.write("•", r)

# =========================================================
# FOOD INTELLIGENCE
# =========================================================
elif page == "Food Intelligence":
    food = st.selectbox("Food", FOODS)

    telemetry = fetch_supply_chain_data(food)
    integrity = compute_integrity_score(telemetry)
    nutrients = adjusted_nutrients(food, telemetry)

    st.subheader("Farm → Plate Intelligence")

    c1,c2,c3 = st.columns(3)
    c1.metric("Farm ID", telemetry.farm_id)
    c1.metric("Harvest Date", str(telemetry.harvest_date))  # FIXED
    c2.metric("Transport Temp", f"{telemetry.avg_transport_temp}°C")
    c2.metric("Delay Hours", telemetry.transport_delay_hours)
    c3.metric("Cold Chain Breaks", telemetry.cold_chain_breaks)
    c3.metric("Contamination Risk", round(telemetry.contamination_risk,2))

    st.metric("Food Integrity", integrity)

    st.subheader("Remaining Nutrients")
    for nutrient, values in nutrients.items():
        st.write(f"{nutrient.upper()} → Remaining: {values['remaining']} | Retention: {values['retention_percent']}%")
        st.progress(values["retention_percent"] / 100)
