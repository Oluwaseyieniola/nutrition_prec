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

PRICE_MAP = {
    "Salmon": 15, "Oats": 3, "Blueberries": 6,
    "Lentils": 2, "Spinach": 4,
    "Chicken Breast": 10, "Avocado": 5,
    "Eggs": 4, "Brown Rice": 3, "Yogurt": 5
}

# =========================================================
# 🇦🇪 UAE ENVIRONMENT MODEL
# =========================================================
UAE_ENVIRONMENT = {
    "availability": {"healthy": 0.7, "processed": 0.9},
    "price_sensitivity": 0.6,
    "convenience_bias": 0.8
}

# =========================================================
# SESSION STATE
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
# HEALTH
# =========================================================
def calculate_bmi(w, h):
    return round(w / (h**2), 1)

# =========================================================
# SUPPLY CHAIN
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
# EXPLANATION ENGINE
# =========================================================
def explain_supply_chain(df):
    explanations = []
    for _, row in df.iterrows():
        if row["Vitamin C"] < 30:
            state = "significant nutrient loss"
        elif row["Vitamin C"] < 60:
            state = "moderate nutrient reduction"
        else:
            state = "nutrients well preserved"

        explanations.append(
            f"At the {row['Stage']} stage, the food experienced {state}. "
            f"Vitamin C ≈ {row['Vitamin C']} and protein ≈ {row['Protein']}."
        )
    return explanations

def interpret_health(user):
    messages = []
    if user["sleep_hours"] < 6:
        messages.append("Low sleep may lead to fatigue and weaker immunity.")
    if user["recovery"] < 50:
        messages.append("Low recovery suggests your body is under stress.")
    if user["bmi"] > 27:
        messages.append("BMI indicates elevated metabolic risk.")
    return messages

def disease_risk(user):
    risks = []
    if user["sleep_hours"] < 6:
        risks.append("Fatigue and metabolic imbalance risk")
    if user["bmi"] > 28:
        risks.append("Type 2 diabetes and heart disease risk")
    if user["strain"] > 15:
        risks.append("Chronic stress and inflammation risk")
    return risks

# =========================================================
# BEHAVIOR ENGINE
# =========================================================
def extract_behavior_patterns(history):
    if history.empty:
        return {"accept_rate": 0, "top_foods": []}

    accept_rate = len(history[history["decision"]=="accepted"]) / len(history)
    food_counts = history["food_name"].value_counts().to_dict()

    return {
        "accept_rate": round(accept_rate, 2),
        "top_foods": list(food_counts.keys())[:3]
    }

def behavior_stage(patterns):
    if patterns["accept_rate"] < 0.3:
        return "resistant"
    elif patterns["accept_rate"] < 0.6:
        return "transitional"
    else:
        return "optimized"

ADJACENT_FOODS = {
    "Chicken Breast": ["Salmon"],
    "Brown Rice": ["Oats"],
    "Yogurt": ["Blueberries"],
    "Oats": ["Lentils"],
}

def gradual_recommendation(patterns):
    stage = behavior_stage(patterns)

    if not patterns["top_foods"]:
        return ["Eggs", "Yogurt"]

    base = patterns["top_foods"][0]

    if stage == "resistant":
        return ADJACENT_FOODS.get(base, [base])

    elif stage == "transitional":
        return list(set(ADJACENT_FOODS.get(base, []) + ["Spinach","Avocado"]))

    else:
        return ["Salmon","Spinach","Blueberries"]

def explain_behavior(stage):
    if stage == "resistant":
        return "We are making small, easy improvements based on your current habits."
    elif stage == "transitional":
        return "You are improving. We are introducing better foods gradually."
    else:
        return "Your habits are strong. Now optimizing for long-term health."

# =========================================================
# DATA FUNCTIONS
# =========================================================
def create_user(w, h, goal):
    user_id = len(st.session_state["users"]) + 1
    df = WearableEngine.simulate(user_id)
    m = WearableEngine.aggregate(df)

    user = {
        "id": user_id,
        "weight_kg": w,
        "height_m": h,
        "bmi": calculate_bmi(w,h),
        "sleep_hours": m["avg_sleep"],
        "hrv": m["avg_hrv"],
        "recovery": m["avg_recovery"],
        "strain": m["avg_strain"],
        "goal": goal
    }

    st.session_state["users"].append(user)

def load_users():
    return pd.DataFrame(st.session_state["users"])

def save_decision(user_id, food, decision):
    st.session_state["history"].append({
        "user_id": user_id,
        "food_name": food,
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
    "Health Insights",
    "Behavior Engine",
    "Decision Engine",
    "Habit Tracker"
])

# CREATE USER
if page == "Create User":
    w = st.number_input("Weight (kg)", 40.0, 150.0, 75.0)
    h = st.number_input("Height (m)", 1.4, 2.2, 1.75)
    goal = st.selectbox("Goal", ["fitness","fat_loss","glucose_control"])

    if st.button("Save"):
        create_user(w,h,goal)
        st.success("User created")

# WEARABLE
elif page == "Wearable Data":
    users = load_users()
    if users.empty:
        st.stop()

    user_id = st.selectbox("User", users["id"])
    df = WearableEngine.simulate(user_id)

    st.dataframe(df)
    st.line_chart(df.set_index("date")[["hrv","sleep_hours","strain"]])

# FOOD
elif page == "Food Deep Dive":
    food = st.selectbox("Food", FOODS)
    df = simulate_supply(food)

    st.dataframe(df)
    for line in explain_supply_chain(df):
        st.write(line)

# HEALTH
elif page == "Health Insights":
    users = load_users()
    if users.empty:
        st.stop()

    user_id = st.selectbox("User", users["id"])
    user = users[users["id"] == user_id].iloc[0]

    for msg in interpret_health(user):
        st.write("•", msg)

    for r in disease_risk(user):
        st.write("⚠️", r)

# BEHAVIOR ENGINE
elif page == "Behavior Engine":
    users = load_users()
    if users.empty:
        st.stop()

    user_id = st.selectbox("User", users["id"])
    history = load_history(user_id)

    patterns = extract_behavior_patterns(history)
    stage = behavior_stage(patterns)

    st.subheader("Behavior Stage")
    st.write(stage.upper())

    st.write(explain_behavior(stage))

    recs = gradual_recommendation(patterns)

    st.subheader("Next Best Foods")
    for r in recs:
        st.write("→", r)

# DECISION
elif page == "Decision Engine":
    users = load_users()
    if users.empty:
        st.stop()

    user_id = st.selectbox("User", users["id"])
    food = st.selectbox("Food", FOODS)

    if st.button("Accept"):
        save_decision(user_id, food, "accepted")

    if st.button("Reject"):
        save_decision(user_id, food, "rejected")

# HABIT TRACKER
elif page == "Habit Tracker":
    users = load_users()
    if users.empty:
        st.stop()

    user_id = st.selectbox("User", users["id"])
    history = load_history(user_id)

    if not history.empty:
        st.dataframe(history)
