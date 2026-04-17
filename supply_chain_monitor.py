import streamlit as st
import pandas as pd
import numpy as np
import datetime
import hashlib

st.set_page_config(page_title="Food Intelligence System MVP", layout="centered")

# =========================================================
# 🧠 CORE ENGINES
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
                "Temp": round(temp, 1),
                "Duration": round(days, 1),
                **{k: round(v,1) for k,v in nutrients.items()}
            })

        return pd.DataFrame(data)


class FoodSystemEngine:

    price_map = {
        "Salmon": 15, "Oats": 3, "Blueberries": 6,
        "Lentils": 2, "Spinach": 4
    }

    processing_map = {
        "Salmon": 2, "Oats": 2, "Blueberries": 1,
        "Lentils": 1, "Spinach": 1
    }

    def environmental_impact(food):
        return {
            "carbon": np.random.uniform(1, 10),
            "water": np.random.uniform(50, 500),
            "biodiversity": np.random.uniform(0, 1)
        }

    def actors():
        return {
            "farmer": {"power": 0.3, "profit": 0.1},
            "processor": {"power": 0.7, "profit": 0.4},
            "retailer": {"power": 0.9, "profit": 0.5}
        }


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

        return round(score,2), env, processing


class BehaviorEngine:

    def decision(user, score, price):
        return round(
            0.4*np.random.random() +   # convenience
            0.3*(1/price) +           # price sensitivity
            0.3*score, 2              # health
        )


# =========================================================
# 👤 USER SIMULATION
# =========================================================

def gen_user():
    return {
        "BMI": np.random.uniform(20, 32),
        "goal": np.random.choice(["fitness","glucose_control"]),
        "strain": np.random.uniform(5,18),
        "sleep": np.random.uniform(4,8)
    }

# =========================================================
# UI
# =========================================================

st.title("🥗 Food Intelligence System (Upgraded MVP)")

page = st.sidebar.radio("Navigation",
    ["System Overview","Food Deep Dive","Decision Engine"]
)

foods = ["Salmon","Oats","Blueberries","Lentils","Spinach"]

# =========================================================
# PAGE 1: SYSTEM VIEW
# =========================================================

if page == "System Overview":
    st.header("🌍 Food System Layers")

    st.markdown("""
    This system integrates:
    - 🌱 Production (Farm)
    - 🏭 Processing
    - 🚚 Supply Chain
    - 🛒 Retail
    - 👤 Consumer Behavior
    """)

    st.subheader("⚖️ Actor Power Distribution")
    st.json(FoodSystemEngine.actors())

# =========================================================
# PAGE 2: FOOD INTELLIGENCE
# =========================================================

elif page == "Food Deep Dive":
    food = st.selectbox("Select Food", foods)

    df = SupplyChainEngine.simulate(food)

    st.subheader("📦 Supply Chain Trace")
    st.dataframe(df)

    st.subheader("📉 Nutrient Degradation")
    st.line_chart(df.set_index("Stage")[["Vitamin C","Protein","Polyphenols"]])

    score, env, processing = ScoringEngine.compute(food, df)

    st.subheader("🧠 Food Intelligence")

    st.write(f"**Unified Score:** {score}")
    st.write(f"Processing Level: {processing}")

    st.write("🌍 Environmental Impact")
    st.json(env)

    st.write(f"💰 Price: ${FoodSystemEngine.price_map[food]}")

# =========================================================
# PAGE 3: DECISION ENGINE
# =========================================================

elif page == "Decision Engine":
    food = st.selectbox("Choose Food", foods)

    df = SupplyChainEngine.simulate(food)
    score, env, processing = ScoringEngine.compute(food, df)

    user = gen_user()

    decision_score = BehaviorEngine.decision(
        user,
        score,
        FoodSystemEngine.price_map[food]
    )

    st.subheader("👤 Simulated User")
    st.json(user)

    st.subheader("🧠 Decision Intelligence")

    st.write(f"Food Score: {score}")
    st.write(f"Decision Probability: {decision_score}")

    if decision_score > 0.6:
        st.success("User is likely to choose this food")
    else:
        st.warning("User may reject this option")

    st.caption("Decision influenced by convenience, price, and health")
