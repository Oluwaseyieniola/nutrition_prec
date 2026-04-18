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
# 🧠 SESSION STATE
# =========================================================
if "users" not in st.session_state:
    st.session_state["users"] = []

if "history" not in st.session_state:
    st.session_state["history"] = []

# =========================================================
# ⌚ WEARABLE ENGINE
# =========================================================
class WearableEngine:

    @staticmethod
    def simulate(user_id, days=7):
        np.random.seed(user_id)

        data = []
        for i in range(days):
            data.append({
                "date": datetime.date.today() - datetime.timedelta(days=i),
                "hrv": np.random.randint(40, 100),
                "resting_hr": np.random.randint(50, 75),
                "sleep_hours": round(np.random.uniform(4.5, 8.5), 2),
                "recovery": np.random.randint(30, 95),
                "strain": round(np.random.uniform(5, 18), 1)
            })

        return pd.DataFrame(data)

    @staticmethod
    def aggregate(df):
        return {
            "avg_hrv": int(df["hrv"].mean()),
            "avg_sleep": round(df["sleep_hours"].mean(), 2),
            "avg_strain": round(df["strain"].mean(), 1),
            "avg_recovery": int(df["recovery"].mean())
        }

# =========================================================
# 🧠 HEALTH
# =========================================================
def calculate_bmi(w, h):
    return round(w / (h**2), 1)

# =========================================================
# 🔬 SUPPLY CHAIN
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
# 🧠 DECISION ENGINE
# =========================================================
def decision_engine(user, score, price):
    recovery_factor = user["recovery"] / 100
    strain_penalty = 1 - (user["strain"] / 20)

    return round(
        0.3 * score +
        0.3 * (1 / price) +
        0.2 * recovery_factor +
        0.2 * strain_penalty,
        2
    )

# =========================================================
# 🗄️ DATA FUNCTIONS
# =========================================================
def create_user(w, h, goal):
    user_id = len(st.session_state["users"]) + 1

    wearable_df = WearableEngine.simulate(user_id)
    metrics = WearableEngine.aggregate(wearable_df)

    user = {
        "id": user_id,
        "weight_kg": w,
        "height_m": h,
        "bmi": calculate_bmi(w, h),
        "sleep_hours": metrics["avg_sleep"],
        "hrv": metrics["avg_hrv"],
        "recovery": metrics["avg_recovery"],
        "strain": metrics["avg_strain"],
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
    "Wearable Data",
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
    goal = st.selectbox("Goal", ["fitness","fat_loss","glucose_control"])

    if st.button("Save"):
        create_user(w, h, goal)
        st.success("User created with wearable data")

# =========================================================
# WEARABLE DATA
# =========================================================
elif page == "Wearable Data":
    users = load_users()

    if users.empty:
        st.warning("Create a user first")
        st.stop()

    user_id = st.selectbox("User", users["id"])

    df = WearableEngine.simulate(user_id)

    st.subheader("⌚ Wearable Data")
    st.dataframe(df)

    st.line_chart(df.set_index("date")[["hrv","sleep_hours","strain"]])

    st.subheader("Aggregated Metrics")
    st.json(WearableEngine.aggregate(df))

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
    user = users[users["id"] == user_id].iloc[0]

    food = st.selectbox("Food", FOODS)

    df = simulate_supply(food)
    score = compute_score(df)

    decision_score = decision_engine(user, score, PRICE_MAP[food])

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
# HABIT TRACKER
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
    else:
        st.write("No decisions recorded yet")
