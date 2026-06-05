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
    "Salmon", "Oats", "Eggs",
    "Spinach", "Chicken Breast",
    "Avocado", "Blueberries"
]

# =========================================================
# FOOD KNOWLEDGE
# =========================================================
FOOD_LIBRARY = {
    "Salmon": {"goal": ["fitness", "glucose_control"], "category": ["RECOVERY_SUPPORT", "ANTI_INFLAMMATORY"], "desc": "Omega-3 rich recovery food"},
    "Oats": {"goal": ["glucose_control"], "category": ["GLUCOSE_STABILIZING", "MICROBIOME_SUPPORT"], "desc": "Stable energy carbohydrates"},
    "Eggs": {"goal": ["fitness"], "category": ["RECOVERY_SUPPORT"], "desc": "Complete protein source"},
    "Spinach": {"goal": ["glucose_control"], "category": ["MICROBIOME_SUPPORT", "ANTI_INFLAMMATORY"], "desc": "Micronutrient dense greens"},
    "Chicken Breast": {"goal": ["fitness", "fat_loss"], "category": ["RECOVERY_SUPPORT"], "desc": "Lean protein support"},
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
    "protein": ["Muscle repair", "Satiety support"],
    "fiber": ["Glucose stability", "Gut microbiome support"],
    "polyphenols": ["Oxidative stress reduction"],
    "magnesium": ["Sleep improvement"],
    "vitamin_c": ["Immune support"],
    "healthy_fats": ["Hormonal balance"],
    "antioxidants": ["Cell protection"]
}

# =========================================================
# SUPPLY CHAIN MODEL
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
# USER ENGINE
# =========================================================
def create_user(*args):
    uid = len(st.session_state.users) + 1
    weight = args[2]
    height = args[3]

    bmi = round(weight / (height ** 2), 1)

    st.session_state.users.append({
        "id": uid,
        "age": args[0],
        "sex": args[1],
        "weight": weight,
        "height": height,
        "goal": args[4],
        "activity": args[5],
        "sleep": args[6],
        "stress": args[7],
        "diet": args[8],
        "allergies": args[9],
        "conditions": args[10],
        "meds": args[11],
        "smoking": args[12],
        "alcohol": args[13],
        "waist": args[14],
        "bmi": bmi
    })

# =========================================================
# HEALTH INSIGHTS (UPGRADED MODEL)
# =========================================================
def health_score(user, wear):
    score = 0
    reasons = []

    score += max(0, user["bmi"] - 24) * 0.7
    score += max(0, user["waist"] - 90) * 0.1
    score += max(0, user["stress"] - 6) * 0.8

    score += max(0, 6 - wear["sleep"]) * 2
    score += max(0, 50 - wear["recovery"]) * 0.05
    score += max(0, wear["glucose_variability"] - 25) * 0.3

    if score > 12:
        risk = "HIGH"
    elif score > 6:
        risk = "MODERATE"
    else:
        risk = "LOW"

    return risk, round(score,1)

# =========================================================
# WEARABLE
# =========================================================
def wearable(uid):
    rng = np.random.default_rng(uid)
    return {
        "sleep": round(rng.uniform(5,8),2),
        "recovery": int(rng.uniform(30,95)),
        "glucose_variability": round(rng.uniform(10,40),1)
    }

# =========================================================
# NUTRIENT ENGINE
# =========================================================
def adjusted_nutrients(food, t):
    base = BASE_NUTRITION[food]
    adjusted = {}

    for n, v in base.items():
        degradation = (
            t.avg_transport_temp/10 * 0.2 +
            t.transport_delay_hours/24 * 0.15 +
            t.processing_level * 0.25
        )

        retention = max(0.2, 1 - degradation)

        adjusted[n] = {
            "value": round(v * retention, 1),
            "retention": round(retention * 100, 1)
        }

    return adjusted

# =========================================================
# INTEGRITY SCORE
# =========================================================
def integrity_score(t):
    score = 100
    score -= t.transport_delay_hours * 0.5
    score -= t.warehouse_days * 1.5
    score -= t.processing_level * 20
    score -= t.contamination_risk * 25
    score -= t.cold_chain_breaks * 10
    score += t.soil_quality * 10
    score -= t.pesticide_score * 15
    return round(max(0,min(score,100)),1)

# =========================================================
# GRADE SYSTEM
# =========================================================
def grade(score):
    if score >= 85: return "A - Excellent"
    if score >= 70: return "B - Good"
    if score >= 55: return "C - Moderate"
    if score >= 40: return "D - Poor"
    return "F - Very Poor"

# =========================================================
# SUPPLY CHAIN STORY
# =========================================================
def supply_story(t):
    return (
        f"Harvested {t.harvest_date}, traveled through "
        f"{t.transport_delay_hours}h delay, stored for "
        f"{t.warehouse_days} days, with processing level "
        f"{t.processing_level:.2f}. Contamination risk "
        f"estimated at {t.contamination_risk:.2f}."
    )

# =========================================================
# RECOMMENDATION ENGINE
# =========================================================
def food_recommendation(food, user, wear):

    t = fetch_supply_chain_data(food)
    integrity = integrity_score(t)
    nutrients = adjusted_nutrients(food, t)

    nutrient_power = sum([x["value"] for x in nutrients.values()])

    score = integrity * 0.5 + nutrient_power * 0.3

    if user["goal"] in FOOD_LIBRARY[food]["goal"]:
        score += 10

    if wear["recovery"] < 50:
        score += 5

    if wear["glucose_variability"] > 30:
        score += 5

    # restriction logic
    if user["diet"] == "vegan" and food in ["Salmon","Eggs","Chicken Breast"]:
        score -= 100

    g = grade(score)

    return {
        "food": food,
        "score": round(score,1),
        "grade": g,
        "description": FOOD_LIBRARY[food]["desc"],
        "integrity": integrity,
        "story": supply_story(t),
        "nutrients": nutrients,
        "effects": list(set([e for n in nutrients if n in NUTRIENT_EFFECTS for e in NUTRIENT_EFFECTS[n]]))
    }

# =========================================================
# RECOMMENDER
# =========================================================
def recommend(user, uid):
    wear = wearable(uid)
    recs = [food_recommendation(f, user, wear) for f in FOODS]
    return sorted(recs, key=lambda x: x["score"], reverse=True), wear

# =========================================================
# UI
# =========================================================
st.title("🧠 Precision Nutrition Intelligence")

page = st.sidebar.radio(
    "Pages",
    ["Create User", "Health Insights", "Recommendations"]
)

# =========================================================
# CREATE USER
# =========================================================
if page == "Create User":

    st.subheader("User Profile")

    age = st.number_input("Age",18,100,30)
    sex = st.selectbox("Sex",["Male","Female"])
    weight = st.number_input("Weight",40.0,200.0,70.0)
    height = st.number_input("Height",1.2,2.5,1.7)
    waist = st.number_input("Waist",40,200,85)

    goal = st.selectbox("Goal",["fitness","fat_loss","glucose_control"])
    activity = st.selectbox("Activity",["low","moderate","high"])

    sleep = st.slider("Sleep",3,12,7)
    stress = st.slider("Stress",1,10,5)

    diet = st.selectbox("Diet",["omnivore","vegetarian","vegan","keto"])

    allergies = st.text_area("Allergies")
    conditions = st.text_area("Medical Conditions")
    meds = st.text_area("Medications")

    smoking = st.selectbox("Smoking",["No","Yes"])
    alcohol = st.selectbox("Alcohol",["No","Occasional","Frequent"])

    if st.button("Create User"):
        create_user(age,sex,weight,height,goal,activity,sleep,stress,
                    diet,allergies,conditions,meds,smoking,alcohol,waist)
        st.success("User Created")

# =========================================================
# HEALTH INSIGHTS
# =========================================================
elif page == "Health Insights":

    users = pd.DataFrame(st.session_state.users)
    if users.empty:
        st.stop()

    uid = st.selectbox("User",users.id)
    user = users[users.id==uid].iloc[0].to_dict()

    wear = wearable(uid)
    risk, score = health_score(user, wear)

    st.metric("Risk Level", risk)
    st.metric("Health Score", score)

# =========================================================
# RECOMMENDATIONS
# =========================================================
elif page == "Recommendations":

    users = pd.DataFrame(st.session_state.users)
    if users.empty:
        st.stop()

    uid = st.selectbox("User",users.id)
    user = users[users.id==uid].iloc[0].to_dict()

    recs, wear = recommend(user, uid)

    st.subheader("Wearable State")
    st.write(wear)

    for r in recs:

        st.markdown("---")
        st.subheader(f"{r['food']} — Grade {r['grade']}")

        st.write(r["description"])
        st.write("Integrity:", r["integrity"])
        st.write(r["story"])

        st.write("Effects:")
        for e in r["effects"]:
            st.write("•", e)

        st.write("Nutrients:")
        for n,v in r["nutrients"].items():
            st.write(f"{n}: {v['value']} ({v['retention']}%)")
            st.progress(v["retention"]/100)
