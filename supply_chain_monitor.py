import streamlit as st
import pandas as pd
import numpy as np
import datetime
import hashlib

st.set_page_config(page_title="Precision Nutrition Digital Twin", layout="centered")

# =========================================================
# UTILITIES
# =========================================================
def clamp(x, minv=0, maxv=100):
    return max(minv, min(x, maxv))

# =========================================================
# WEARABLE SIMULATION
# =========================================================
def gen_wearable(days=7, seed=42):
    np.random.seed(seed)
    base = datetime.date.today()

    data = []
    for i in range(days):
        data.append({
            "day": i,
            "HRV": np.random.randint(30, 90),
            "sleep": np.random.uniform(60, 98),
            "strain": np.random.uniform(5, 18),
            "steps": np.random.randint(3000, 12000)
        })
    return pd.DataFrame(data)

# =========================================================
# LIFESTYLE INFERENCE
# =========================================================
def infer_state(df):
    return {
        "hrv": df["HRV"].mean(),
        "sleep": df["sleep"].mean(),
        "strain": df["strain"].mean(),
        "steps": df["steps"].mean()
    }

# =========================================================
# INITIAL HEALTH STATE
# =========================================================
def initial_health(user, state):

    bmi = user["BMI"]

    return {
        "energy": 70,
        "inflammation": clamp(50 + state["strain"] * 2),
        "metabolic_health": clamp(100 - (bmi - 22) * 5),
        "recovery": clamp(state["sleep"]),
        "stress_load": clamp(100 - state["hrv"])
    }

# =========================================================
# FOOD EFFECT MODEL (CORE DIGITAL TWIN LOGIC)
# =========================================================
def apply_food_effects(health, food):

    effects = {
        "Salmon": {"inflammation": -6, "recovery": +5},
        "Oats": {"metabolic_health": +6, "stress_load": -3},
        "Blueberries": {"inflammation": -4, "metabolic_health": +3},
        "Lentils": {"metabolic_health": +5, "energy": +4},
        "Spinach": {"recovery": +4, "inflammation": -3},
        "Eggs": {"energy": +6, "recovery": +3},
        "Avocado": {"stress_load": -4, "recovery": +3}
    }

    if food not in effects:
        return health

    for k, v in effects[food].items():
        health[k] = clamp(health[k] + v)

    return health

# =========================================================
# DIGITAL TWIN SIMULATION ENGINE
# =========================================================
def run_digital_twin(user, state, foods, days=7):

    timeline = []

    health = initial_health(user, state)

    for d in range(days):

        # daily decay (natural physiology drift)
        health["energy"] = clamp(health["energy"] - 1 + np.random.randn())
        health["stress_load"] = clamp(health["stress_load"] + 1)
        health["recovery"] = clamp(health["recovery"] - 0.5)

        # apply foods daily
        for f in foods:
            health = apply_food_effects(health, f)

        # compute risk score
        risk = (
            0.3 * health["stress_load"] +
            0.3 * (100 - health["recovery"]) +
            0.2 * (100 - health["metabolic_health"]) +
            0.2 * health["inflammation"]
        )

        timeline.append({
            "Day": d,
            "Energy": health["energy"],
            "Stress": health["stress_load"],
            "Recovery": health["recovery"],
            "Inflammation": health["inflammation"],
            "Metabolic": health["metabolic_health"],
            "RiskScore": risk
        })

    return pd.DataFrame(timeline)

# =========================================================
# UI
# =========================================================
st.title("🧠 Precision Nutrition Digital Twin Engine")

page = st.sidebar.radio("Navigation", ["1️⃣ Profile", "2️⃣ Digital Twin Simulation"])

# =========================================================
# PAGE 1
# =========================================================
if page.startswith("1️⃣"):
    st.header("User Profile")

    with st.form("profile"):
        age = st.number_input("Age", 18, 80, 30)
        weight = st.number_input("Weight (kg)", 40, 200, 70)
        height = st.number_input("Height (cm)", 120, 220, 170)
        submit = st.form_submit_button("Generate Twin")

    if submit:
        bmi = weight / ((height / 100) ** 2)

        wearable = gen_wearable()
        state = infer_state(wearable)

        user = {
            "age": age,
            "BMI": bmi
        }

        st.session_state["user"] = user
        st.session_state["state"] = state

        st.subheader("Wearable Snapshot")
        st.dataframe(wearable)

        st.subheader("Inferred State")
        st.json(state)

# =========================================================
# PAGE 2
# =========================================================
elif page.startswith("2️⃣"):
    st.header("🧬 Digital Twin Simulation")

    user = st.session_state.get("user")
    state = st.session_state.get("state")

    if not user:
        st.warning("Create profile first")
        st.stop()

    foods = st.multiselect(
        "Select Nutrition Plan",
        ["Salmon","Oats","Blueberries","Lentils","Spinach","Eggs","Avocado"],
        default=["Salmon","Oats","Blueberries"]
    )

    st.subheader("Running Physiological Simulation...")

    df = run_digital_twin(user, state, foods, days=10)

    st.subheader("📈 Physiological Timeline")
    st.line_chart(df.set_index("Day")[["Energy","Stress","Recovery","Inflammation","Metabolic"]])

    st.subheader("⚠️ Risk Trajectory")
    st.line_chart(df.set_index("Day")[["RiskScore"]])

    st.subheader("Insight")
    if df["RiskScore"].iloc[-1] < df["RiskScore"].iloc[0]:
        st.success("Your nutrition plan improves physiological stability over time.")
    else:
        st.warning("Your current nutrition pattern increases system stress.")
