import streamlit as st
import pandas as pd
import numpy as np
import datetime
import hashlib

st.set_page_config(page_title="Food Intelligence System MVP", layout="centered")

# =========================================================
# 🌍 REAL-WORLD DATA
# =========================================================

FOOD_DB = {
    "Salmon": {"category": "protein", "origin": "Norway"},
    "Oats": {"category": "grain", "origin": "Canada"},
    "Blueberries": {"category": "fruit", "origin": "USA"},
    "Lentils": {"category": "legume", "origin": "India"},
    "Spinach": {"category": "vegetable", "origin": "Netherlands"},
    "Chicken Breast": {"category": "protein", "origin": "Brazil"},
    "Avocado": {"category": "fat", "origin": "Mexico"},
    "Eggs": {"category": "protein", "origin": "UAE"},
    "Brown Rice": {"category": "grain", "origin": "Thailand"},
    "Yogurt": {"category": "dairy", "origin": "France"}
}

FARMS = [
    {"name": "Green Valley Farm", "location": "Netherlands"},
    {"name": "Al Rawabi Farms", "location": "UAE"},
    {"name": "Blue River Aquaculture", "location": "Norway"},
    {"name": "Golden Prairie Farms", "location": "Canada"}
]

RETAILERS = [
    {"name": "Carrefour", "location": "UAE"},
    {"name": "Lulu Hypermarket", "location": "UAE"},
    {"name": "Spinneys", "location": "UAE"},
    {"name": "Waitrose", "location": "UAE"}
]

# =========================================================
# 🧠 HEALTH METRICS
# =========================================================

def calculate_bmi(weight_kg, height_m):
    return round(weight_kg / (height_m ** 2), 1)

def gen_user_realistic():
    weight = np.random.uniform(60, 110)
    height = np.random.uniform(1.55, 1.95)

    return {
        "weight_kg": round(weight, 1),
        "height_m": round(height, 2),
        "BMI": calculate_bmi(weight, height),
        "sleep_hours": round(np.random.uniform(4.5, 8.5), 2),
        "strain": round(np.random.uniform(5, 18), 1),
        "goal": np.random.choice(["fitness", "glucose_control", "fat_loss"]),
        "activity_level": np.random.choice(["low", "moderate", "high"])
    }

# =========================================================
# 🔬 SUPPLY CHAIN ENGINE
# =========================================================

class SupplyChainEngine:
    def simulate(food):
        seed = int(hashlib.md5(food.encode()).hexdigest(), 16) % 10**6
        np.random.seed(seed)

        stages = ["Farm", "Harvest", "Storage", "Transport", "Retail"]

        nutrients = {
            "Vitamin C": np.random.uniform(40, 100),
            "Protein": np.random.uniform(5, 30),
            "Polyphenols": np.random.uniform(50, 120)
        }

        data = []
        for stage in stages:
            temp = np.random.uniform(2, 35)
            days = np.random.uniform(0.5, 5)

            decay = np.exp(-0.05 * days * (temp / 25))
            for k in nutrients:
                nutrients[k] *= decay

            data.append({
                "Stage": stage,
                "Temperature (°C)": round(temp, 1),
                "Duration (days)": round(days, 1),
                **{k: round(v,1) for k,v in nutrients.items()}
            })

        return pd.DataFrame(data)

def simulate_supply_real(food):
    farm = np.random.choice(FARMS)
    retailer = np.random.choice(RETAILERS)

    df = SupplyChainEngine.simulate(food)
    df["Farm"] = farm["name"]
    df["Origin"] = farm["location"]
    df["Retailer"] = retailer["name"]

    return df

# =========================================================
# 🌱 FOOD SYSTEM ENGINE
# =========================================================

class FoodSystemEngine:

    price_map = {
        "Salmon": 15, "Oats": 3, "Blueberries": 6,
        "Lentils": 2, "Spinach": 4,
        "Chicken Breast": 10, "Avocado": 5,
        "Eggs": 4, "Brown Rice": 3, "Yogurt": 5
    }

    processing_map = {
        "Salmon": 2, "Oats": 2, "Blueberries": 1,
        "Lentils": 1, "Spinach": 1,
        "Chicken Breast": 2, "Avocado": 1,
        "Eggs": 1, "Brown Rice": 2, "Yogurt": 3
    }

    def environmental_impact(food):
        return {
            "carbon": round(np.random.uniform(1, 10), 2),
            "water": round(np.random.uniform(50, 500), 1),
            "biodiversity": round(np.random.uniform(0, 1), 2)
        }

# =========================================================
# 🧠 SCORING ENGINE
# =========================================================

class ScoringEngine:

    def nutrition_score(df):
        latest = df.iloc[-1]
        return (latest["Vitamin C"] + latest["Protein"] + latest["Polyphenols"]) / 300

    def compute(food, df):
        nutrition = ScoringEngine.nutrition_score(df)
        processing = FoodSystemEngine.processing_map[food]
        env = FoodSystemEngine.environmental_impact(food)

        score = (
            0.5 * nutrition +
            0.3 * (1 / processing) +
            0.2 * (1 / env["carbon"])
        )

        return round(score, 2), env, processing

# =========================================================
# 🧠 BEHAVIOR ENGINE
# =========================================================

def decision_engine(user, food_score, price):
    convenience = np.random.uniform(0.3, 1.0)
    price_factor = 1 / price
    health_weight = food_score

    decision_score = (
        0.4 * convenience +
        0.3 * price_factor +
        0.3 * health_weight
    )

    return round(decision_score, 2)

# =========================================================
# 📊 SESSION STATE
# =========================================================

if "history" not in st.session_state:
    st.session_state["history"] = []

if "habit_score" not in st.session_state:
    st.session_state["habit_score"] = 0

def log_decision(user, food, score, decision):
    st.session_state["history"].append({
        "time": datetime.datetime.now(),
        "food": food,
        "score": score,
        "decision": decision
    })

    if decision == "accepted":
        st.session_state["habit_score"] += 1
    else:
        st.session_state["habit_score"] -= 0.5

# =========================================================
# UI
# =========================================================

st.title("🥗 Food Intelligence System")

page = st.sidebar.radio("Navigation",
    ["User Profile","Food Deep Dive","Decision Engine","Habit Tracker"]
)

foods = list(FOOD_DB.keys())

# =========================================================
# USER PROFILE
# =========================================================

if page == "User Profile":
    st.header("👤 User Profile")

    user = gen_user_realistic()
    st.json(user)

# =========================================================
# FOOD DEEP DIVE
# =========================================================

elif page == "Food Deep Dive":
    food = st.selectbox("Select Food", foods)

    df = simulate_supply_real(food)

    st.subheader("📦 Supply Chain Trace")
    st.dataframe(df)

    st.subheader("📉 Nutrient Degradation")
    st.line_chart(df.set_index("Stage")[["Vitamin C","Protein","Polyphenols"]])

    score, env, processing = ScoringEngine.compute(food, df)

    st.subheader("🧠 Food Intelligence")
    st.write(f"Unified Score: {score}")
    st.write(f"Processing Level: {processing}")

    st.subheader("🌍 Environmental Impact")
    st.json(env)

    st.write(f"💰 Price: ${FoodSystemEngine.price_map[food]}")

# =========================================================
# DECISION ENGINE
# =========================================================

elif page == "Decision Engine":
    food = st.selectbox("Choose Food", foods)

    df = simulate_supply_real(food)
    score, env, _ = ScoringEngine.compute(food, df)

    user = gen_user_realistic()

    decision_score = decision_engine(user, score, FoodSystemEngine.price_map[food])

    st.subheader("👤 User")
    st.json(user)

    st.subheader("🧠 Decision Intelligence")
    st.write(f"Food Score: {score}")
    st.write(f"Decision Score: {decision_score}")

    if decision_score > 0.6:
        st.success("User likely to choose this food")
    else:
        st.warning("User may reject this food")

    if st.button("✅ Choose Food"):
        log_decision(user, food, score, "accepted")
        st.success("Decision logged")

    if st.button("❌ Reject Food"):
        log_decision(user, food, score, "rejected")
        st.warning("Decision logged")

# =========================================================
# HABIT TRACKER
# =========================================================

elif page == "Habit Tracker":
    st.header("📊 Habit Tracking")

    history_df = pd.DataFrame(st.session_state["history"])

    if not history_df.empty:
        st.dataframe(history_df)
        st.line_chart(history_df.set_index("time")["score"])
        st.metric("Habit Score", round(st.session_state["habit_score"],2))
    else:
        st.write("No decisions recorded yet")
