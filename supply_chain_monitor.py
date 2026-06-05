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
# SESSION INIT (UPGRADED)
# =========================================================
def init():
    keys = [
        "users",
        "history",
        "habits",
        "biomarkers",
        "food_logs",
        "lab_results"
    ]

    for k in keys:
        if k not in st.session_state:
            st.session_state[k] = []

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
        "category": ["MICROBIOME_SUPPORT", "ANTI_INFLAMMATORY"],
        "desc": "Micronutrient dense greens"
    },
    "Chicken Breast": {
        "goal": ["fitness", "fat_loss"],
        "category": ["RECOVERY_SUPPORT"],
        "desc": "Lean protein support"
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
# BASE NUTRITION DATABASE
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
# SENSITIVITY + EFFECTS
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

NUTRIENT_EFFECTS = {
    "omega3": ["Improves recovery", "Reduces inflammation"],
    "protein": ["Supports muscle repair", "Improves satiety"],
    "fiber": ["Stabilizes glucose", "Supports gut microbiome"],
    "polyphenols": ["Reduces oxidative stress"],
    "magnesium": ["Supports sleep quality"],
    "vitamin_c": ["Supports immunity"],
    "healthy_fats": ["Hormone balance"],
    "antioxidants": ["Cell protection"]
}

# =========================================================
# SUPPLY TELEMETRY
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
# USER ENGINE (UPGRADED)
# =========================================================
def create_user(
    age,
    sex,
    weight,
    height,
    goal,
    activity_level,
    sleep_hours,
    stress_level,
    diet_pattern,
    allergies,
    medical_conditions,
    medications,
    smoking,
    alcohol,
    waist_circumference
):

    uid = len(st.session_state.users) + 1

    bmi = round(weight / (height ** 2), 1)

    bmr = (10 * weight + 6.25 * (height * 100) - 5 * age + (5 if sex == "Male" else -161))

    st.session_state.users.append({
        "id": uid,
        "age": age,
        "sex": sex,
        "weight": weight,
        "height": height,
        "goal": goal,
        "bmi": bmi,
        "bmr": round(bmr),
        "activity_level": activity_level,
        "sleep_hours": sleep_hours,
        "stress_level": stress_level,
        "diet_pattern": diet_pattern,
        "allergies": allergies,
        "medical_conditions": medical_conditions,
        "medications": medications,
        "smoking": smoking,
        "alcohol": alcohol,
        "waist_circumference": waist_circumference
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
# HEALTH ENGINE (UPGRADED)
# =========================================================
def health_score(user, wear):
    score = 0
    reasons = []

    if user["bmi"] > 27:
        score += 2
        reasons.append("High BMI")

    if user["waist_circumference"] > 102:
        score += 2
        reasons.append("High Waist Circumference")

    if user["stress_level"] > 7:
        score += 1
        reasons.append("High Stress")

    if wear["sleep"] < 6:
        score += 2
        reasons.append("Poor Sleep")

    if wear["recovery"] < 50:
        score += 2
        reasons.append("Low Recovery")

    if wear["glucose_variability"] > 30:
        score += 2
        reasons.append("Glucose Instability")

    risk = "LOW"
    if score >= 6:
        risk = "HIGH"
    elif score >= 3:
        risk = "MODERATE"

    return risk, reasons

# =========================================================
# NUTRIENT + FOOD ENGINE
# =========================================================
def adjusted_nutrients(food, telemetry):
    base = BASE_NUTRITION[food]
    adjusted = {}

    for nutrient, value in base.items():
        sensitivity = NUTRIENT_SENSITIVITY.get(nutrient, 1.0)

        degradation = (
            telemetry.avg_transport_temp / 10 * 0.2 * sensitivity +
            telemetry.transport_delay_hours / 24 * 0.15 * sensitivity +
            telemetry.processing_level * 0.25 * sensitivity
        )

        retention = max(0.2, 1 - degradation)

        adjusted[nutrient] = {
            "original": value,
            "remaining": round(value * retention, 1),
            "retention_percent": round(retention * 100, 1)
        }

    return adjusted

def compute_integrity_score(t):
    score = 100
    score -= t.transport_delay_hours * 0.5
    score -= t.warehouse_days * 1.5
    score -= t.processing_level * 20
    score -= t.contamination_risk * 25
    score -= t.cold_chain_breaks * 10
    score += t.soil_quality * 10
    score -= t.pesticide_score * 15
    return round(max(min(score,100),0),1)

# =========================================================
# RECOMMENDER
# =========================================================
def food_recommendation(food, user, wear):
    telemetry = fetch_supply_chain_data(food)
    integrity = compute_integrity_score(telemetry)
    nutrients = adjusted_nutrients(food, telemetry)

    score = 50

    if user["goal"] in FOOD_LIBRARY[food]["goal"]:
        score += 20

    if wear["recovery"] < 50:
        score += 10

    if wear["glucose_variability"] > 30:
        score += 10

    score += integrity * 0.3

    # Dietary restrictions
    if user["diet_pattern"] == "vegan" and food in ["Salmon", "Eggs", "Chicken Breast"]:
        score -= 100

    if "diabetes" in user["medical_conditions"].lower():
        score += nutrients.get("fiber", {}).get("remaining", 0) * 0.1

    return {
        "food": food,
        "description": FOOD_LIBRARY[food]["desc"],
        "categories": FOOD_LIBRARY[food]["category"],
        "integrity": integrity,
        "score": round(score,1),
        "nutrients": nutrients,
        "telemetry": telemetry,
        "explanations": ["Supports your current physiological state"]
    }

def recommend(user, uid):
    wear = wearable(uid)

    recs = [food_recommendation(f, user, wear) for f in FOODS]
    df = pd.DataFrame(recs)

    return df.sort_values("score", ascending=False), wear

# =========================================================
# UI
# =========================================================
st.title("🧠 Precision Nutrition Intelligence")

page = st.sidebar.radio(
    "Pages",
    ["Create User", "Health Insights", "Recommendations", "Habit Tracker", "Food Intelligence"]
)

# =========================================================
# CREATE USER UI (UPGRADED)
# =========================================================
if page == "Create User":

    st.subheader("Create Precision Nutrition Profile")

    age = st.number_input("Age", 18, 100, 30)
    sex = st.selectbox("Sex", ["Male", "Female"])
    weight = st.number_input("Weight (kg)", 40.0, 200.0, 75.0)
    height = st.number_input("Height (m)", 1.2, 2.5, 1.75)
    waist = st.number_input("Waist (cm)", 40, 200, 90)

    goal = st.selectbox("Goal", ["fitness","fat_loss","glucose_control","muscle_gain","longevity"])
    activity = st.selectbox("Activity", ["sedentary","active","athlete"])

    sleep = st.slider("Sleep Hours", 3, 12, 7)
    stress = st.slider("Stress Level", 1, 10, 5)

    diet = st.selectbox("Diet", ["omnivore","vegetarian","vegan","keto","mediterranean"])
    allergies = st.text_area("Allergies")
    conditions = st.text_area("Medical Conditions")
    meds = st.text_area("Medications")

    smoking = st.selectbox("Smoking", ["No","Yes"])
    alcohol = st.selectbox("Alcohol", ["No","Occasional","Frequent"])

    if st.button("Create User"):
        create_user(
            age, sex, weight, height, goal,
            activity, sleep, stress, diet,
            allergies, conditions, meds,
            smoking, alcohol, waist
        )
        st.success("User Created")

# =========================================================
# OTHER UI SECTIONS (UNCHANGED LOGICALLY)
# =========================================================
elif page == "Health Insights":

    users = pd.DataFrame(st.session_state.users)
    if users.empty:
        st.stop()

    uid = st.selectbox("User", users.id)
    user = users[users.id == uid].iloc[0].to_dict()

    wear = wearable(uid)
    risk, reasons = health_score(user, wear)

    st.metric("Risk", risk)
    st.write(reasons)

elif page == "Recommendations":

    users = pd.DataFrame(st.session_state.users)
    if users.empty:
        st.stop()

    uid = st.selectbox("User", users.id)
    user = users[users.id == uid].iloc[0].to_dict()

    recs, wear = recommend(user, uid)

    st.subheader("Recommendations")
    st.dataframe(recs[["food","score","integrity"]])

elif page == "Food Intelligence":

    food = st.selectbox("Food", FOODS)
    telemetry = fetch_supply_chain_data(food)

    st.json({
        "farm": telemetry.farm_id,
        "integrity": compute_integrity_score(telemetry),
        "temp": telemetry.avg_transport_temp
    })
