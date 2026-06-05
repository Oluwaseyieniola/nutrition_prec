import streamlit as st
import pandas as pd
import numpy as np
import datetime
from dataclasses import dataclass, asdict

# =========================================================
# APP CONFIG
# =========================================================
st.set_page_config(page_title="Precision Nutrition Intelligence v2", layout="wide")

# =========================================================
# STATE INITIALIZATION (SIMULATED DATABASE LAYERS)
# =========================================================
def init_state():
    defaults = {
        "users": {},
        "events": [],
        "wearable_cache": {},
        "food_logs": [],
        "inference_cache": {}
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# =========================================================
# FOOD INTELLIGENCE LAYER
# =========================================================
FOODS = ["Salmon", "Oats", "Eggs", "Spinach", "Chicken Breast", "Avocado", "Blueberries"]

FOOD_LIBRARY = {
    "Salmon": {"goal": ["fitness", "glucose_control"], "desc": "Omega-3 recovery food"},
    "Oats": {"goal": ["glucose_control"], "desc": "Stable carbs"},
    "Eggs": {"goal": ["fitness"], "desc": "Complete protein"},
    "Spinach": {"goal": ["glucose_control"], "desc": "Micronutrient dense greens"},
    "Chicken Breast": {"goal": ["fitness", "fat_loss"], "desc": "Lean protein"},
    "Avocado": {"goal": ["fat_loss"], "desc": "Healthy fats"},
    "Blueberries": {"goal": ["glucose_control"], "desc": "Antioxidants"}
}

BASE_NUTRITION = {
    "Salmon": {"protein": 25, "omega3": 100, "cal": 208},
    "Oats": {"fiber": 85, "protein": 17, "cal": 389},
    "Eggs": {"protein": 12, "b12": 70, "cal": 155},
    "Spinach": {"iron": 90, "magnesium": 95, "cal": 23},
    "Chicken Breast": {"protein": 31, "cal": 165},
    "Avocado": {"fat": 90, "fiber": 65, "cal": 160},
    "Blueberries": {"antioxidants": 100, "cal": 57}
}

# =========================================================
# DATAMODELS (PRODUCTION STYLE)
# =========================================================
@dataclass
class UserProfile:
    id: int
    static: dict
    lifestyle: dict
    behavioral: dict
    physiology: dict

@dataclass
class WearableSnapshot:
    sleep_duration: float
    hrv: float
    resting_hr: float
    steps: int
    glucose_variability: float
    recovery: float

# =========================================================
# EVENT SYSTEM (SIMULATED KAFKA)
# =========================================================
def emit_event(event_type, payload):
    st.session_state.events.append({
        "type": event_type,
        "payload": payload,
        "timestamp": datetime.datetime.utcnow()
    })

# =========================================================
# USER SERVICE
# =========================================================
def create_user(data):
    uid = len(st.session_state.users) + 1

    user = UserProfile(
        id=uid,
        static={
            "age": data["age"],
            "sex": data["sex"],
            "weight": data["weight"],
            "height": data["height"],
            "waist": data["waist"],
            "bmi": round(data["weight"] / (data["height"] ** 2), 1)
        },
        lifestyle={
            "goal": data["goal"],
            "activity": data["activity"],
            "diet": data["diet"],
            "sleep_reported": data["sleep"],
            "stress": data["stress"]
        },
        behavioral={
            "meal_timing": None,
            "snacking_frequency": None,
            "adherence_score": None,
            "late_night_eating": None
        },
        physiology={
            "metabolic_adjustment": 1.0,
            "insulin_sensitivity": None,
            "circadian_stability": None
        }
    )

    st.session_state.users[uid] = user
    emit_event("USER_CREATED", asdict(user))
    return uid

# =========================================================
# WEARABLE ENGINE (SIMULATED REAL DATA LAYER)
# =========================================================
def get_wearable(uid):
    rng = np.random.default_rng(uid)

    wearable = WearableSnapshot(
        sleep_duration=round(rng.uniform(5, 8), 2),
        hrv=round(rng.uniform(20, 90), 1),
        resting_hr=round(rng.uniform(55, 85), 1),
        steps=int(rng.integers(3000, 12000)),
        glucose_variability=round(rng.uniform(10, 45), 1),
        recovery=round(rng.uniform(30, 95), 1)
    )

    st.session_state.wearable_cache[uid] = wearable
    return wearable

# =========================================================
# USER INFERENCE ENGINE (KEY UPGRADE)
# =========================================================
def infer_user_state(user: UserProfile, wear: WearableSnapshot):
    physiology = user.physiology

    # metabolic adjustment
    if wear.steps < 5000:
        physiology["metabolic_adjustment"] = 0.95
    elif wear.steps > 9000:
        physiology["metabolic_adjustment"] = 1.1

    # recovery proxy
    physiology["circadian_stability"] = round(
        (wear.sleep_duration / 8 + wear.hrv / 100) / 2, 2
    )

    # insulin sensitivity proxy
    physiology["insulin_sensitivity"] = round(
        max(0, 1 - wear.glucose_variability / 50), 2
    )

    return user

# =========================================================
# FOOD SCORING ENGINE
# =========================================================
def score_food(food, user: UserProfile, wear: WearableSnapshot):

    base = BASE_NUTRITION[food]

    nutrient_score = sum(base.values())

    health_modifier = (
        wear.recovery / 100 +
        user.physiology.get("insulin_sensitivity", 0.5)
    )

    goal_bonus = 10 if user.lifestyle["goal"] in FOOD_LIBRARY[food]["goal"] else 0

    final_score = nutrient_score * health_modifier + goal_bonus

    return round(final_score, 2)

# =========================================================
# RECOMMENDATION ENGINE
# =========================================================
def recommend(uid):
    user = st.session_state.users[uid]
    wear = get_wearable(uid)

    user = infer_user_state(user, wear)

    results = []

    for food in FOODS:
        score = score_food(food, user, wear)

        results.append({
            "food": food,
            "score": score,
            "desc": FOOD_LIBRARY[food]["desc"]
        })

    return sorted(results, key=lambda x: x["score"], reverse=True), wear

# =========================================================
# HEALTH INSIGHTS ENGINE
# =========================================================
def health_insights(user: UserProfile, wear: WearableSnapshot):

    bmi = user.static["bmi"]

    risk = 0
    risk += max(0, bmi - 25) * 0.6
    risk += max(0, 6 - wear.sleep_duration) * 1.5
    risk += max(0, wear.glucose_variability - 30) * 0.4

    if risk > 10:
        level = "HIGH"
    elif risk > 5:
        level = "MODERATE"
    else:
        level = "LOW"

    return level, round(risk, 2)

# =========================================================
# ======================= UI =============================
# =========================================================
st.title("🧠 Precision Nutrition Intelligence v2")

page = st.sidebar.radio("Navigation", ["Create User", "Health Insights", "Recommendations"])

# =========================================================
# CREATE USER
# =========================================================
if page == "Create User":

    st.subheader("User Profile (Enhanced Model)")

    data = {
        "age": st.number_input("Age", 18, 100, 30),
        "sex": st.selectbox("Sex", ["Male", "Female"]),
        "weight": st.number_input("Weight", 40.0, 200.0, 70.0),
        "height": st.number_input("Height", 1.2, 2.5, 1.7),
        "waist": st.number_input("Waist", 40, 200, 85),
        "goal": st.selectbox("Goal", ["fitness", "fat_loss", "glucose_control"]),
        "activity": st.selectbox("Activity", ["low", "moderate", "high"]),
        "sleep": st.slider("Sleep Quality", 3, 10, 7),
        "stress": st.slider("Stress", 1, 10, 5),
        "diet": st.selectbox("Diet", ["omnivore", "vegetarian", "vegan", "keto"])
    }

    if st.button("Create User"):
        uid = create_user(data)
        st.success(f"User {uid} created")

# =========================================================
# HEALTH INSIGHTS
# =========================================================
elif page == "Health Insights":

    if not st.session_state.users:
        st.warning("No users yet")
        st.stop()

    uid = st.selectbox("Select User", list(st.session_state.users.keys()))

    user = st.session_state.users[uid]
    wear = get_wearable(uid)

    level, score = health_insights(user, wear)

    st.metric("Risk Level", level)
    st.metric("Health Score", score)

    st.write("Physiology Model")
    st.json(user.physiology)

# =========================================================
# RECOMMENDATIONS
# =========================================================
elif page == "Recommendations":

    if not st.session_state.users:
        st.warning("No users yet")
        st.stop()

    uid = st.selectbox("Select User", list(st.session_state.users.keys()))

    recs, wear = recommend(uid)

    st.subheader("Wearable Snapshot")
    st.json(wear.__dict__)

    st.subheader("Top Foods")

    for r in recs:
        st.markdown("---")
        st.write(f"### {r['food']} — Score {r['score']}")
        st.write(r["desc"])
