import streamlit as st
import pandas as pd
import numpy as np
import datetime
import hashlib
import os

st.set_page_config(page_title="Food Intelligence System", layout="wide")

# =========================================================
# SESSION STATE
# =========================================================
if "users" not in st.session_state:
    st.session_state["users"] = []

if "history" not in st.session_state:
    st.session_state["history"] = []

if "food_logs" not in st.session_state:
    st.session_state["food_logs"] = []

if "glucose_responses" not in st.session_state:
    st.session_state["glucose_responses"] = []

# =========================================================
# CONSTANTS
# =========================================================
FOODS = ["Salmon","Oats","Blueberries","Chicken Breast","Avocado","Eggs","Brown Rice","Greek Yogurt","Lentils","Spinach"]

FOOD_LIBRARY = {
    "Oats": {"category": "whole_grain", "good_for": ["glucose_control"]},
    "Brown Rice": {"category": "whole_grain", "good_for": ["energy"], "watch_for": ["diabetes_risk"]},
    "Lentils": {"category": "legume", "good_for": ["glucose_control"]},
    "Chicken Breast": {"category": "protein", "good_for": ["fitness"]},
    "Salmon": {"category": "fatty_fish", "good_for": ["fitness"]},
    "Avocado": {"category": "healthy_fat", "good_for": ["glucose_control"]},
    "Eggs": {"category": "protein", "good_for": ["fitness"]},
    "Greek Yogurt": {"category": "protein", "good_for": ["fitness"]},
    "Blueberries": {"category": "fruit", "good_for": ["glucose_control"]},
    "Spinach": {"category": "leafy_green", "good_for": ["glucose_control"]}
}

# =========================================================
# USER + HEALTH
# =========================================================
def calculate_bmi(w, h):
    return round(w / (h ** 2), 1)

def create_user(w, h, goal):
    user_id = len(st.session_state["users"]) + 1
    user = {
        "id": user_id,
        "weight": w,
        "height": h,
        "bmi": calculate_bmi(w, h),
        "goal": goal,
        "sleep_hours": np.random.uniform(5, 8),
        "steps": np.random.randint(3000, 12000)
    }
    st.session_state["users"].append(user)

def load_users():
    return pd.DataFrame(st.session_state["users"])

# =========================================================
# FOOD LOGGING
# =========================================================
def log_food_intake(user_id, food):
    st.session_state["food_logs"].append({
        "user_id": user_id,
        "food": food,
        "time": datetime.datetime.now()
    })

def load_food_logs(user_id):
    df = pd.DataFrame(st.session_state["food_logs"])
    if df.empty:
        return df
    return df[df["user_id"] == user_id]

# =========================================================
# GLUCOSE ENGINE
# =========================================================
def simulate_glucose_response(user, food):
    base = 85
    lib = FOOD_LIBRARY.get(food, {})
    cat = lib.get("category", "")

    spike = 0

    if cat in ["whole_grain", "fruit"]:
        spike += np.random.uniform(25, 50)
    elif cat in ["legume"]:
        spike += np.random.uniform(15, 30)
    else:
        spike += np.random.uniform(5, 15)

    if user["bmi"] > 27:
        spike *= 1.2
    if user["sleep_hours"] < 6:
        spike *= 1.15
    if user["steps"] < 6000:
        spike *= 1.1

    return {
        "peak": round(base + spike, 1),
        "delta": round(spike, 1)
    }

def record_glucose_response(user_id, food, response):
    st.session_state["glucose_responses"].append({
        "user_id": user_id,
        "food": food,
        "delta": response["delta"]
    })

def get_personal_glucose_profile(user_id):
    df = pd.DataFrame(st.session_state["glucose_responses"])
    if df.empty:
        return {}
    df = df[df["user_id"] == user_id]
    return df.groupby("food")["delta"].mean().to_dict()

# =========================================================
# RECOMMENDATION ENGINE
# =========================================================
def food_score(food, user):
    score = 50
    lib = FOOD_LIBRARY.get(food, {})

    if user["goal"] in lib.get("good_for", []):
        score += 20

    profile = get_personal_glucose_profile(user["id"])

    if food in profile:
        impact = profile[food]
        if impact > 35:
            score -= 20
        elif impact > 25:
            score -= 10
        else:
            score += 5

    return score

def generate_recommendations(user):
    rows = []
    for food in FOODS:
        score = food_score(food, user)
        rows.append({"food": food, "score": score})
    return pd.DataFrame(rows).sort_values("score", ascending=False)

# =========================================================
# UI
# =========================================================
st.title("🥗 Precision Food Intelligence System")

page = st.sidebar.radio("Navigation", [
    "Create User",
    "Food Logger",
    "Glucose Lab",
    "Recommendations"
])

# =========================================================
# CREATE USER
# =========================================================
if page == "Create User":
    w = st.number_input("Weight", 40.0, 150.0, 75.0)
    h = st.number_input("Height", 1.4, 2.2, 1.75)
    goal = st.selectbox("Goal", ["fitness", "fat_loss", "glucose_control"])

    if st.button("Create"):
        create_user(w, h, goal)
        st.success("User created")

# =========================================================
# FOOD LOGGER
# =========================================================
elif page == "Food Logger":
    users = load_users()
    if users.empty:
        st.stop()

    user_id = st.selectbox("User", users["id"])
    food = st.selectbox("Food", FOODS)

    if st.button("Log Food"):
        log_food_intake(user_id, food)
        st.success("Logged")

    logs = load_food_logs(user_id)
    if not logs.empty:
        st.dataframe(logs)

# =========================================================
# GLUCOSE LAB
# =========================================================
elif page == "Glucose Lab":
    users = load_users()
    if users.empty:
        st.stop()

    user_id = st.selectbox("User", users["id"])
    user = users[users["id"] == user_id].iloc[0].to_dict()

    food = st.selectbox("Food", FOODS)

    if st.button("Test Glucose"):
        response = simulate_glucose_response(user, food)
        record_glucose_response(user_id, food, response)

        st.metric("Peak", response["peak"])
        st.metric("Spike", response["delta"])

    profile = get_personal_glucose_profile(user_id)
    if profile:
        st.bar_chart(pd.Series(profile))

# =========================================================
# RECOMMENDATIONS
# =========================================================
elif page == "Recommendations":
    users = load_users()
    if users.empty:
        st.stop()

    user_id = st.selectbox("User", users["id"])
    user = users[users["id"] == user_id].iloc[0].to_dict()

    df = generate_recommendations(user)

    st.subheader("Top Foods")
    st.dataframe(df.head(5))

    st.bar_chart(df.set_index("food"))
