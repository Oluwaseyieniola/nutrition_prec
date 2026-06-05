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
    keys = ["users", "history", "habits"]
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
# FOOD LIBRARY
# =========================================================
FOOD_LIBRARY = {
    "Salmon": {"goal": ["fitness", "glucose_control"], "desc": "Omega-3 rich recovery food"},
    "Oats": {"goal": ["glucose_control"], "desc": "Stable energy carbohydrates"},
    "Eggs": {"goal": ["fitness"], "desc": "Complete protein source"},
    "Spinach": {"goal": ["glucose_control"], "desc": "Micronutrient dense greens"},
    "Chicken Breast": {"goal": ["fitness", "fat_loss"], "desc": "Lean protein support"},
    "Avocado": {"goal": ["fat_loss"], "desc": "Healthy fats"},
    "Blueberries": {"goal": ["glucose_control"], "desc": "Antioxidant support"}
}

# =========================================================
# BASE NUTRITION
# =========================================================
BASE_NUTRITION = {
    "Salmon": {"protein": 25, "omega3": 100, "vitamin_d": 90, "cal": 208},
    "Oats": {"fiber": 85, "protein": 17, "magnesium": 70, "cal": 389},
    "Eggs": {"protein": 12, "b12": 70, "choline": 88, "cal": 155},
    "Spinach": {"magnesium": 95, "iron": 90, "fiber": 70, "cal": 23},
    "Chicken Breast": {"protein": 31, "b6": 60, "cal": 165},
    "Avocado": {"healthy_fats": 90, "fiber": 65, "cal": 160},
    "Blueberries": {"polyphenols": 100, "vitamin_c": 80, "cal": 57}
}

# =========================================================
# NUTRIENT EFFECTS
# =========================================================
NUTRIENT_EFFECTS = {
    "omega3": "Reduces inflammation & supports recovery",
    "protein": "Muscle repair & satiety",
    "fiber": "Gut health & glucose stability",
    "polyphenols": "Antioxidant protection",
    "healthy_fats": "Hormonal balance",
    "magnesium": "Sleep & recovery",
    "vitamin_c": "Immunity support"
}

# =========================================================
# SUPPLY TELEMETRY
# =========================================================
@dataclass
class SupplyTelemetry:
    farm_id: str
    harvest_age_days: int
    soil_quality: float
    pesticide_score: float
    transport_temp: float
    delay_hours: int
    warehouse_days: int
    processing_level: float
    contamination_risk: float

def fetch_supply_chain_data(food):
    rng = np.random.default_rng(abs(hash(food)) % 9999)

    return SupplyTelemetry(
        farm_id=f"FARM-{rng.integers(100,999)}",
        harvest_age_days=int(rng.integers(1,10)),
        soil_quality=round(rng.uniform(0.6,1.0),2),
        pesticide_score=round(rng.uniform(0.0,0.4),2),
        transport_temp=round(rng.uniform(2,15),1),
        delay_hours=int(rng.integers(0,20)),
        warehouse_days=int(rng.integers(1,7)),
        processing_level=round(rng.uniform(0.0,0.6),2),
        contamination_risk=round(rng.uniform(0.0,0.4),2)
    )

# =========================================================
# NUTRIENT RETENTION
# =========================================================
def adjusted_nutrients(food, t):
    base = BASE_NUTRITION[food]
    adjusted = {}

    degradation = (
        (t.transport_temp/10)*0.2 +
        (t.delay_hours/24)*0.2 +
        t.processing_level*0.3
    )

    for n, v in base.items():
        retention = max(0.25, 1 - degradation)
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
    score -= t.transport_temp * 1.2
    score -= t.delay_hours * 0.6
    score -= t.processing_level * 25
    score -= t.contamination_risk * 30
    score += t.soil_quality * 10
    score -= t.pesticide_score * 20
    return round(max(0, min(100, score)), 1)

# =========================================================
# FOOD GRADE SYSTEM (A–F)
# =========================================================
def grade_food(score):
    if score >= 85:
        return "A (Excellent)"
    elif score >= 70:
        return "B (Good)"
    elif score >= 55:
        return "C (Moderate)"
    elif score >= 40:
        return "D (Poor)"
    return "F (Very Poor)"

# =========================================================
# SUPPLY CHAIN NARRATIVE
# =========================================================
def supply_story(t):
    return f"""
    Harvested {t.harvest_age_days} days ago from Farm {t.farm_id}
    with soil quality at {t.soil_quality:.2f}.
    The food experienced {t.delay_hours}h transport delay,
    {t.warehouse_days} days in storage, and moderate processing
    level of {t.processing_level:.2f}. Contamination risk assessed
    at {t.contamination_risk:.2f}.
    """

# =========================================================
# USER ENGINE
# =========================================================
def create_user(weight, height, goal):
    uid = len(st.session_state.users) + 1
    bmi = round(weight / (height**2), 1)

    st.session_state.users.append({
        "id": uid,
        "weight": weight,
        "height": height,
        "goal": goal,
        "bmi": bmi
    })

# =========================================================
# HEALTH INSIGHTS (UPGRADED)
# =========================================================
def health_score(user, wear):
    score = 0

    score += max(0, user["bmi"] - 22) * 0.5
    score += max(0, 6 - wear["sleep"]) * 2
    score += max(0, 50 - wear["recovery"]) * 0.05
    score += max(0, wear["glucose_variability"] - 25) * 0.3

    risk = "LOW"
    if score > 12:
        risk = "HIGH"
    elif score > 6:
        risk = "MODERATE"

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
# RECOMMENDATION ENGINE (UNIFIED)
# =========================================================
def recommend_food(food, user, wear):

    t = fetch_supply_chain_data(food)
    integrity = integrity_score(t)
    nutrients = adjusted_nutrients(food, t)

    nutrient_power = sum([v["value"] for v in nutrients.values()])

    score = (
        integrity * 0.5 +
        nutrient_power * 0.3 +
        (10 if user["goal"] in FOOD_LIBRARY[food]["goal"] else 0)
    )

    grade = grade_food(score)
    story = supply_story(t)

    explanation = []

    if wear["recovery"] < 50:
        explanation.append("Supports recovery under low readiness state")
    if wear["glucose_variability"] > 30:
        explanation.append("Helps stabilize glucose fluctuations")

    for n in nutrients:
        if n in NUTRIENT_EFFECTS:
            explanation.append(NUTRIENT_EFFECTS[n])

    return {
        "food": food,
        "score": round(score,1),
        "grade": grade,
        "story": story,
        "nutrients": nutrients,
        "integrity": integrity,
        "description": FOOD_LIBRARY[food]["desc"],
        "explanations": list(set(explanation))
    }

# =========================================================
# RECOMMENDER
# =========================================================
def recommend(user, uid):
    wear = wearable(uid)
    recs = [recommend_food(f, user, wear) for f in FOODS]
    return sorted(recs, key=lambda x: x["score"], reverse=True), wear

# =========================================================
# UI
# =========================================================
st.title("🧠 Precision Nutrition Intelligence")

page = st.sidebar.radio("Pages", [
    "Create User",
    "Health Insights",
    "Recommendations"
])

# =========================================================
# CREATE USER
# =========================================================
if page == "Create User":
    w = st.number_input("Weight", 40.0, 200.0, 70.0)
    h = st.number_input("Height", 1.2, 2.5, 1.7)
    g = st.selectbox("Goal", ["fitness","fat_loss","glucose_control"])

    if st.button("Create"):
        create_user(w,h,g)
        st.success("User created")

# =========================================================
# HEALTH INSIGHTS
# =========================================================
elif page == "Health Insights":

    users = pd.DataFrame(st.session_state.users)
    if users.empty:
        st.stop()

    uid = st.selectbox("User", users.id)
    user = users[users.id==uid].iloc[0].to_dict()

    wear = wearable(uid)
    risk, score = health_score(user, wear)

    st.subheader("Health Status")
    st.metric("Risk", risk)
    st.metric("Health Score", score)

# =========================================================
# RECOMMENDATIONS
# =========================================================
elif page == "Recommendations":

    users = pd.DataFrame(st.session_state.users)
    if users.empty:
        st.stop()

    uid = st.selectbox("User", users.id)
    user = users[users.id==uid].iloc[0].to_dict()

    recs, wear = recommend(user, uid)

    st.subheader("Wearable Data")
    st.write(wear)

    for r in recs:

        st.markdown("---")
        st.subheader(f"{r['food']} — Grade {r['grade']}")

        st.write(r["description"])
        st.write(f"Integrity Score: {r['integrity']}")
        st.write(r["story"])

        st.write("Why this works:")
        for e in r["explanations"]:
            st.write("•", e)

        st.write("Nutrients:")
        for n, v in r["nutrients"].items():
            st.write(f"{n}: {v['value']} ({v['retention']}%)")
            st.progress(v["retention"]/100)
