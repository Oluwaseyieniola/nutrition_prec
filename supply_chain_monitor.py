import streamlit as st
import pandas as pd
import numpy as np
import datetime
import hashlib

st.set_page_config(page_title="Food Intelligence System", layout="centered")

# =========================================================
# 🌍 FOOD DATA
# =========================================================
FOODS = [
    "Salmon","Oats","Blueberries","Lentils","Spinach",
    "Chicken Breast","Avocado","Eggs","Brown Rice","Yogurt"
]

FOOD_FEATURES = {
    "Salmon": [25, 0, 13, 2, 15],
    "Oats": [13, 1, 7, 2, 3],
    "Blueberries": [1, 10, 0, 1, 6],
    "Lentils": [9, 2, 0.5, 1, 2],
    "Spinach": [3, 1, 0, 1, 4],
    "Chicken Breast": [31, 0, 3, 2, 10],
    "Avocado": [2, 1, 15, 1, 5],
    "Eggs": [13, 1, 10, 1, 4],
    "Brown Rice": [3, 1, 1, 2, 3],
    "Yogurt": [10, 5, 4, 3, 5]
}

PRICE_MAP = {
    "Salmon": 15, "Oats": 3, "Blueberries": 6,
    "Lentils": 2, "Spinach": 4,
    "Chicken Breast": 10, "Avocado": 5,
    "Eggs": 4, "Brown Rice": 3, "Yogurt": 5
}

# =========================================================
# 🧠 SESSION STATE (IN-MEMORY)
# =========================================================
if "users" not in st.session_state:
    st.session_state["users"] = []

if "history" not in st.session_state:
    st.session_state["history"] = []

# =========================================================
# 🧠 HEALTH
# =========================================================
def calculate_bmi(w, h):
    return round(w / (h**2), 1)

# =========================================================
# 🔬 SUPPLY CHAIN SIMULATION
# =========================================================
def simulate_supply(food):
    seed = int(hashlib.md5(food.encode()).hexdigest(), 16) % 10**6
    np.random.seed(seed)

    nutrients = {
        "Vitamin C": np.random.uniform(40, 100),
        "Protein": np.random.uniform(5, 30),
        "Polyphenols": np.random.uniform(50, 120)
    }

    data = []
    for stage in ["Farm","Harvest","Storage","Transport","Retail"]:
        temp = np.random.uniform(2, 35)
        days = np.random.uniform(0.5, 5)

        decay = np.exp(-0.05 * days * (temp / 25))
        for k in nutrients:
            nutrients[k] *= decay

        data.append({
            "Stage": stage,
            **{k: round(v,1) for k,v in nutrients.items()}
        })

    return pd.DataFrame(data)

# =========================================================
# 🧠 SCORING
# =========================================================
def compute_score(df):
    last = df.iloc[-1]
    return round(
        (last["Vitamin C"] + last["Protein"] + last["Polyphenols"]) / 300, 2
    )

# =========================================================
# 🧠 BEHAVIOR + RECOMMENDER
# =========================================================
def decision_engine(score, price):
    return round(0.4*np.random.random() + 0.3*(1/price) + 0.3*score, 2)

def build_user_profile(history):
    if history.empty:
        return np.zeros(5)

    profile = np.zeros(5)

    for _, row in history.iterrows():
        vec = np.array(FOOD_FEATURES.get(row["food_name"], [0]*5))

        if row["decision"] == "accepted":
            profile += vec
        else:
            profile -= vec * 0.5

    return profile / (len(history) + 1)

def cosine_similarity(a, b):
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0
    return np.dot(a, b) / (np.linalg.norm(a)*np.linalg.norm(b))

def recommend_foods(user_id):
    history = load_history(user_id)
    user_vec = build_user_profile(history)

    scores = []
    for food, vec in FOOD_FEATURES.items():
        sim = cosine_similarity(user_vec, np.array(vec))
        scores.append((food, round(sim,3)))

    return sorted(scores, key=lambda x: x[1], reverse=True)[:5]

# =========================================================
# 🗄️ LOCAL DATA FUNCTIONS
# =========================================================
def create_user(w, h, sleep, goal):
    user_id = len(st.session_state["users"]) + 1

    user = {
        "id": user_id,
        "weight_kg": w,
        "height_m": h,
        "bmi": calculate_bmi(w,h),
        "sleep_hours": sleep,
        "goal": goal
    }

    st.session_state["users"].append(user)

def load_users():
    return pd.DataFrame(st.session_state["users"])

def save_decision(user_id, food, score, decision):
    st.session_state["history"].append({
        "user_id": user_id,
        "food_name": food,
        "score": score,
        "decision": decision,
        "created_at": datetime.datetime.now()
    })

def load_history(user_id):
    df = pd.DataFrame(st.session_state["history"])
    if df.empty:
        return df
    return df[df["user_id"] == user_id]

# =========================================================
# UI
# =========================================================
st.title("🥗 Food Intelligence System")

page = st.sidebar.radio("Navigation", [
    "Create User",
    "Food Deep Dive",
    "Decision Engine",
    "Habit Tracker"
])

# =========================================================
# CREATE USER
# =========================================================
if page == "Create User":
    st.header("👤 Create User")

    w = st.number_input("Weight (kg)", 40.0, 150.0, 75.0)
    h = st.number_input("Height (m)", 1.4, 2.2, 1.75)
    sleep = st.number_input("Sleep (hours)", 3.0, 10.0, 7.0)
    goal = st.selectbox("Goal", ["fitness","fat_loss","glucose_control"])

    if st.button("Save"):
        create_user(w,h,sleep,goal)
        st.success("User created")

# =========================================================
# FOOD DEEP DIVE
# =========================================================
elif page == "Food Deep Dive":
    food = st.selectbox("Food", FOODS)

    df = simulate_supply(food)

    st.dataframe(df)
    st.line_chart(df.set_index("Stage"))

    st.metric("Food Score", compute_score(df))

# =========================================================
# DECISION ENGINE
# =========================================================
elif page == "Decision Engine":
    users = load_users()

    if users.empty:
        st.warning("Create a user first")
        st.stop()

    user_id = st.selectbox("User", users["id"])
    food = st.selectbox("Food", FOODS)

    df = simulate_supply(food)
    score = compute_score(df)

    decision_score = decision_engine(score, PRICE_MAP[food])

    st.write(f"Food Score: {score}")
    st.write(f"Decision Score: {decision_score}")

    if decision_score > 0.6:
        st.success("Likely to choose")
    else:
        st.warning("May reject")

    if st.button("Accept"):
        save_decision(user_id, food, score, "accepted")
        st.success("Saved")

    if st.button("Reject"):
        save_decision(user_id, food, score, "rejected")
        st.warning("Saved")

# =========================================================
# HABIT TRACKER + RECOMMENDER
# =========================================================
elif page == "Habit Tracker":
    users = load_users()

    if users.empty:
        st.warning("No users")
        st.stop()

    user_id = st.selectbox("User", users["id"])

    history = load_history(user_id)

    if not history.empty:
        st.dataframe(history)
        st.line_chart(history["score"])

        st.subheader("🧠 Recommendations")

        recs = recommend_foods(user_id)

        for food, score in recs:
            st.write(f"{food} → Match: {score}")

    else:
        st.info("No history yet → explore foods first")
