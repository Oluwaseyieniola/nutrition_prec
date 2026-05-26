import streamlit as st
import pandas as pd
import numpy as np
import datetime
from dataclasses import dataclass

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Precision Nutrition Intelligence System",
    layout="wide"
)

# =========================================================
# INIT SESSION
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
    "Salmon",
    "Oats",
    "Eggs",
    "Spinach",
    "Chicken Breast",
    "Avocado",
    "Blueberries"
]

# =========================================================
# FOOD LIBRARY
# =========================================================
FOOD_LIBRARY = {

    "Salmon": {
        "goal": ["fitness", "glucose_control"],
        "effects": ["recovery", "anti_inflammation"],
        "desc": "Omega-3 recovery support"
    },

    "Oats": {
        "goal": ["glucose_control"],
        "effects": ["stable_glucose"],
        "desc": "Slow digesting carbohydrates"
    },

    "Eggs": {
        "goal": ["fitness"],
        "effects": ["muscle_repair"],
        "desc": "Complete protein"
    },

    "Spinach": {
        "goal": ["glucose_control"],
        "effects": ["micronutrients"],
        "desc": "Magnesium + Iron"
    },

    "Chicken Breast": {
        "goal": ["fitness", "fat_loss"],
        "effects": ["lean_mass"],
        "desc": "Lean protein"
    },

    "Avocado": {
        "goal": ["fat_loss"],
        "effects": ["healthy_fats"],
        "desc": "Healthy fat profile"
    },

    "Blueberries": {
        "goal": ["glucose_control"],
        "effects": ["antioxidants"],
        "desc": "Polyphenol support"
    }
}

# =========================================================
# BASE NUTRITION DATABASE
# =========================================================
BASE_NUTRITION = {

    "Salmon": {
        "protein": 25,
        "fiber": 0,
        "cal": 208,
        "omega3": 100,
        "micronutrients": 80
    },

    "Oats": {
        "protein": 17,
        "fiber": 10,
        "cal": 389,
        "micronutrients": 70
    },

    "Eggs": {
        "protein": 12,
        "fiber": 0,
        "cal": 155,
        "micronutrients": 75
    },

    "Spinach": {
        "protein": 3,
        "fiber": 2,
        "cal": 23,
        "micronutrients": 100
    },

    "Chicken Breast": {
        "protein": 31,
        "fiber": 0,
        "cal": 165,
        "micronutrients": 65
    },

    "Avocado": {
        "protein": 2,
        "fiber": 7,
        "cal": 160,
        "micronutrients": 60
    },

    "Blueberries": {
        "protein": 1,
        "fiber": 2,
        "cal": 57,
        "micronutrients": 95
    }
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

# =========================================================
# MOCK REAL FARM TO PLATE DATA
# (Supposing Kibsons or another provider supplies this)
# =========================================================
def fetch_supply_chain_data(food):

    rng = np.random.default_rng(abs(hash(food)) % 1000)

    return SupplyTelemetry(

        farm_id=f"FARM-{rng.integers(100,999)}",

        harvest_date=datetime.date.today() -
        datetime.timedelta(days=int(rng.integers(1,10))),

        soil_quality=round(rng.uniform(0.6, 1.0),2),

        pesticide_score=round(rng.uniform(0.0, 0.5),2),

        avg_transport_temp=round(rng.uniform(2,15),1),

        transport_delay_hours=int(rng.integers(0,20)),

        warehouse_days=int(rng.integers(1,8)),

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

    bmi = round(weight / (height ** 2),1)

    st.session_state.users.append({

        "id": uid,
        "weight": weight,
        "height": height,
        "goal": goal,
        "bmi": bmi
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
# HEALTH RISK ENGINE
# =========================================================
def health_score(user, wear):

    score = 0
    reasons = []

    if user["bmi"] > 27:
        score += 2
        reasons.append("High BMI")

    if wear["sleep"] < 6:
        score += 2
        reasons.append("Poor sleep")

    if wear["recovery"] < 50:
        score += 2
        reasons.append("Low recovery")

    if wear["glucose_variability"] > 30:
        score += 2
        reasons.append("Glucose instability")

    risk = "LOW"

    if score >= 6:
        risk = "HIGH"

    elif score >= 3:
        risk = "MODERATE"

    return risk, reasons

# =========================================================
# NUTRIENT DECAY ENGINE
# =========================================================
def nutrient_decay_score(telemetry):

    score = 100

    # temperature degradation
    if telemetry.avg_transport_temp > 10:
        score -= 15

    # transport delay
    score -= telemetry.transport_delay_hours * 0.5

    # warehouse storage
    score -= telemetry.warehouse_days * 1.5

    # processing degradation
    score -= telemetry.processing_level * 20

    # contamination
    score -= telemetry.contamination_risk * 25

    # cold chain breaks
    score -= telemetry.cold_chain_breaks * 10

    return max(score, 10)

# =========================================================
# FOOD INTEGRITY ENGINE
# =========================================================
def compute_integrity_score(telemetry):

    freshness = nutrient_decay_score(telemetry)

    soil_bonus = telemetry.soil_quality * 15

    pesticide_penalty = telemetry.pesticide_score * 20

    integrity = freshness + soil_bonus - pesticide_penalty

    return round(max(min(integrity,100),0),1)

# =========================================================
# ADJUST NUTRIENTS
# =========================================================
def adjusted_nutrients(food, telemetry):

    decay = nutrient_decay_score(telemetry) / 100

    base = BASE_NUTRITION[food]

    adjusted = {}

    for k,v in base.items():

        adjusted[k] = round(v * decay,2)

    return adjusted

# =========================================================
# PREFERENCE ENGINE
# =========================================================
def preferences(uid):

    df = pd.DataFrame(st.session_state.history)

    if df.empty:
        return {}

    df = df[df.user == uid]

    if df.empty:
        return {}

    result = {}

    for food, g in df.groupby("food"):

        acceptance = len(g[g.decision == "yes"]) / len(g)

        result[food] = acceptance

    return result

# =========================================================
# HABITS
# =========================================================
def log_habit(uid, food):

    st.session_state.habits.append({

        "user": uid,
        "food": food,
        "date": datetime.date.today()
    })

def habit_score(uid):

    df = pd.DataFrame(st.session_state.habits)

    if df.empty:
        return 0

    return len(df[df.user == uid])

# =========================================================
# CONFIDENCE ENGINE
# =========================================================
def confidence_score(telemetry, integrity):

    confidence = 100

    confidence -= telemetry.contamination_risk * 30

    confidence -= telemetry.processing_level * 20

    confidence += integrity * 0.1

    return round(max(min(confidence,100),0),1)

# =========================================================
# AI RECOMMENDATION ENGINE
# =========================================================
def food_score(food, user, pref, wear):

    telemetry = fetch_supply_chain_data(food)

    integrity = compute_integrity_score(telemetry)

    nutrients = adjusted_nutrients(food, telemetry)

    confidence = confidence_score(telemetry, integrity)

    score = 50

    # Goal Alignment
    if user["goal"] in FOOD_LIBRARY[food]["goal"]:
        score += 20

    # Nutrition
    score += nutrients.get("protein",0) * 0.7

    score += nutrients.get("fiber",0) * 1.2

    score += nutrients.get("micronutrients",0) * 0.15

    # Fat Loss
    if user["goal"] == "fat_loss":
        score -= nutrients.get("cal",0) * 0.05

    # Recovery
    if wear["recovery"] < 50:
        score += 8

    # Glucose control
    if wear["glucose_variability"] > 30:
        if food in ["Oats","Spinach","Blueberries"]:
            score += 10

    # User preference learning
    if food in pref:
        score += (pref[food] - 0.5) * 40

    # Food integrity
    score += integrity * 0.3

    return {

        "food": food,

        "score": round(score,1),

        "integrity": integrity,

        "confidence": confidence,

        "telemetry": telemetry,

        "nutrients": nutrients
    }

# =========================================================
# RECOMMENDER
# =========================================================
def recommend(user, uid):

    pref = preferences(uid)

    wear = wearable(uid)

    recommendations = []

    for food in FOODS:

        recommendations.append(
            food_score(food, user, pref, wear)
        )

    df = pd.DataFrame(recommendations)

    return df.sort_values("score", ascending=False), wear

# =========================================================
# UI
# =========================================================
st.title("🧠 Precision Nutrition Intelligence Platform")

page = st.sidebar.radio(

    "Pages",

    [
        "Create User",
        "Health Insights",
        "Recommendations",
        "Habit Tracker",
        "Food Intelligence"
    ]
)

# =========================================================
# CREATE USER
# =========================================================
if page == "Create User":

    weight = st.number_input(
        "Weight (kg)",
        40.0,
        200.0,
        75.0
    )

    height = st.number_input(
        "Height (m)",
        1.2,
        2.5,
        1.75
    )

    goal = st.selectbox(

        "Goal",

        [
            "fitness",
            "fat_loss",
            "glucose_control"
        ]
    )

    if st.button("Create User"):

        create_user(weight, height, goal)

        st.success("User Created")

# =========================================================
# HEALTH INSIGHTS
# =========================================================
elif page == "Health Insights":

    users = pd.DataFrame(st.session_state.users)

    if users.empty:
        st.stop()

    uid = st.selectbox("User", users.id)

    user = users[users.id == uid].iloc[0].to_dict()

    wear = wearable(uid)

    risk, reasons = health_score(user, wear)

    st.subheader("Physiology")

    c1,c2,c3,c4,c5 = st.columns(5)

    c1.metric("BMI", user["bmi"])

    c2.metric("Sleep", wear["sleep"])

    c3.metric("Recovery", wear["recovery"])

    c4.metric("HRV", wear["hrv"])

    c5.metric(
        "Glucose Variability",
        wear["glucose_variability"]
    )

    st.subheader("Health Risk")

    st.write("Risk Level:", risk)

    st.write("Drivers:", reasons)

# =========================================================
# RECOMMENDATIONS
# =========================================================
elif page == "Recommendations":

    users = pd.DataFrame(st.session_state.users)

    if users.empty:
        st.stop()

    uid = st.selectbox("User", users.id)

    user = users[users.id == uid].iloc[0].to_dict()

    recs, wear = recommend(user, uid)

    st.subheader("Wearable Intelligence")

    st.write(wear)

    st.subheader("Precision Recommendations")

    for _, r in recs.iterrows():

        with st.container(border=True):

            st.subheader(r.food)

            st.write(
                FOOD_LIBRARY[r.food]["desc"]
            )

            c1,c2,c3 = st.columns(3)

            c1.metric("AI Score", r.score)

            c2.metric("Food Integrity", r.integrity)

            c3.metric("Confidence", r.confidence)

            st.write("Adjusted Nutrients")

            st.json(r.nutrients)

            telemetry = r.telemetry

            st.write("Supply Chain Intelligence")

            st.write({
                "Farm": telemetry.farm_id,
                "Harvest Date": str(telemetry.harvest_date),
                "Transport Temp":
                telemetry.avg_transport_temp,
                "Delay Hours":
                telemetry.transport_delay_hours,
                "Warehouse Days":
                telemetry.warehouse_days,
                "Cold Chain Breaks":
                telemetry.cold_chain_breaks
            })

            st.write("Recommendation Explanation")

            reasons = []

            if r.integrity > 80:
                reasons.append(
                    "High nutrient retention"
                )

            if wear["recovery"] < 50:
                reasons.append(
                    "Supports recovery state"
                )

            if user["goal"] == "glucose_control":
                reasons.append(
                    "Supports glucose stability"
                )

            st.write(reasons)

            b1,b2 = st.columns(2)

            if b1.button(
                f"Accept {r.food}",
                key=f"a{uid}{r.food}"
            ):

                st.session_state.history.append({

                    "user": uid,
                    "food": r.food,
                    "decision": "yes"
                })

                log_habit(uid, r.food)

                st.rerun()

            if b2.button(
                f"Reject {r.food}",
                key=f"r{uid}{r.food}"
            ):

                st.session_state.history.append({

                    "user": uid,
                    "food": r.food,
                    "decision": "no"
                })

                st.rerun()

# =========================================================
# HABIT TRACKER
# =========================================================
elif page == "Habit Tracker":

    users = pd.DataFrame(st.session_state.users)

    if users.empty:
        st.stop()

    uid = st.selectbox("User", users.id)

    st.metric(
        "Healthy Nutrition Actions",
        habit_score(uid)
    )

# =========================================================
# FOOD INTELLIGENCE
# =========================================================
elif page == "Food Intelligence":

    food = st.selectbox(
        "Food",
        FOODS
    )

    telemetry = fetch_supply_chain_data(food)

    integrity = compute_integrity_score(
        telemetry
    )

    nutrients = adjusted_nutrients(
        food,
        telemetry
    )

    st.subheader("Farm → Plate Intelligence")

    st.write({

        "Farm ID": telemetry.farm_id,

        "Harvest Date":
        str(telemetry.harvest_date),

        "Soil Quality":
        telemetry.soil_quality,

        "Pesticide Score":
        telemetry.pesticide_score,

        "Transport Temperature":
        telemetry.avg_transport_temp,

        "Delay Hours":
        telemetry.transport_delay_hours,

        "Warehouse Days":
        telemetry.warehouse_days,

        "Humidity Exposure":
        telemetry.humidity_exposure,

        "Processing Level":
        telemetry.processing_level,

        "Contamination Risk":
        telemetry.contamination_risk,

        "Cold Chain Breaks":
        telemetry.cold_chain_breaks
    })

    st.metric(
        "Food Integrity Score",
        integrity
    )

    st.subheader(
        "Effective Nutritional Value"
    )

    st.json(nutrients)

    st.subheader(
        "Biological Intelligence Insight"
    )

    if integrity > 80:

        st.success(
            "Food retained strong nutrient integrity."
        )

    elif integrity > 60:

        st.warning(
            "Moderate nutrient degradation detected."
        )

    else:

        st.error(
            "Significant nutrient degradation risk."
        )
