import streamlit as st
import pandas as pd
import numpy as np
import datetime
import hashlib
import requests
import os

st.set_page_config(page_title="Food Intelligence System", layout="wide")

# =========================================================
# PHYSIOLOGY SIMULATOR (REPLACES WHOOP/FITBIT)
# =========================================================
class PhysiologySimulator:
    def fetch_data(self, user_id=None, days=7):

        seed = user_id or 42
        np.random.seed(seed)

        base_hrv = np.random.randint(45, 85)
        base_sleep = np.random.uniform(5.5, 8.2)
        base_strain = np.random.uniform(6, 16)

        rows = []

        for i in range(days):
            recovery_signal = np.clip(np.random.normal(65, 18), 10, 100)

            rows.append({
                "date": datetime.date.today() - datetime.timedelta(i),

                "hrv": int(np.random.normal(base_hrv, 6)),
                "sleep_hours": round(np.random.normal(base_sleep, 0.8), 2),
                "strain": round(np.random.normal(base_strain, 2), 1),
                "recovery": int(recovery_signal),

                "energy_state": np.random.choice(
                    ["Low", "Moderate", "High"],
                    p=[0.3, 0.5, 0.2]
                ),

                "stress_state": np.random.choice(
                    ["Calm", "Elevated", "High"],
                    p=[0.4, 0.4, 0.2]
                ),

                "readiness": int(np.clip(recovery_signal - np.random.randint(10, 30), 0, 100))
            })

        return pd.DataFrame(rows)


def get_provider():
    return PhysiologySimulator()


# =========================================================
# CORE ENGINE
# =========================================================
def aggregate_wearable(df):
    return {
        "avg_hrv": int(df["hrv"].mean()),
        "avg_sleep": round(df["sleep_hours"].mean(), 2),
        "avg_strain": round(df["strain"].mean(), 1),
        "avg_recovery": int(df["recovery"].mean()),
    }


def calculate_bmi(w, h):
    return round(w / (h ** 2), 1)


def estimate_metabolic_status(user):
    score = 0
    if user["bmi"] > 27:
        score += 2
    if user["sleep_hours"] < 6:
        score += 2
    if user["strain"] > 14:
        score += 2
    if user["recovery"] < 50:
        score += 1

    return "high" if score >= 5 else "moderate" if score >= 3 else "low"


# =========================================================
# USER CREATION
# =========================================================
def create_user(w, h, goal):

    user_id = len(st.session_state["users"]) + 1

    provider = get_provider()
    df = provider.fetch_data(user_id=user_id, days=7)

    m = aggregate_wearable(df)

    user = {
        "id": user_id,
        "weight_kg": w,
        "height_m": h,
        "bmi": calculate_bmi(w, h),

        "sleep_hours": m["avg_sleep"],
        "hrv": m["avg_hrv"],
        "recovery": m["avg_recovery"],
        "strain": m["avg_strain"],

        "goal": goal,
    }

    st.session_state["users"].append(user)
    st.session_state[f"wearable_{user_id}"] = df


# =========================================================
# STATE INTERPRETATION LAYER (IMPORTANT UX SHIFT)
# =========================================================
def interpret_body_state(row):

    if row["recovery"] > 75:
        return "🟢 Fully recovered — high performance readiness"
    elif row["recovery"] > 50:
        return "🟡 Moderate recovery — stable but not optimal"
    else:
        return "🔴 High fatigue — prioritize recovery"


def physiology_context(row):

    if row["recovery"] < 40:
        return "recovery_debt"
    if row["strain"] > 14:
        return "high_stress"
    if row["sleep_hours"] < 6:
        return "sleep_deficit"
    return "balanced"


# =========================================================
# SESSION STATE
# =========================================================
if "users" not in st.session_state:
    st.session_state["users"] = []


# =========================================================
# UI
# =========================================================
st.title("🥗 Food Intelligence System (Physiology AI Mode)")

page = st.sidebar.radio("Navigation", ["Create User", "Health Insights"])

# =========================================================
# CREATE USER
# =========================================================
if page == "Create User":

    w = st.number_input("Weight (kg)", 40.0, 150.0, 75.0)
    h = st.number_input("Height (m)", 1.4, 2.2, 1.75)
    goal = st.selectbox("Goal", ["fitness", "fat_loss", "glucose_control"])

    if st.button("Create User"):
        create_user(w, h, goal)
        st.success("User created successfully")


# =========================================================
# HEALTH INSIGHTS (VISUAL-FIRST UX)
# =========================================================
elif page == "Health Insights":

    users = st.session_state.get("users", [])

    if not users:
        st.warning("No users yet")
        st.stop()

    user = users[-1]
    df = st.session_state[f"wearable_{user['id']}"]

    latest = df.iloc[0]

    st.subheader("🧠 Body State Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Recovery", latest["recovery"])
    col2.metric("Sleep", latest["sleep_hours"])
    col3.metric("Strain", latest["strain"])

    st.markdown("### 🔥 Physiological Interpretation")
    st.info(interpret_body_state(latest))

    st.markdown("### ⚡ Energy State")
    st.success(f"{latest['energy_state']}")

    st.markdown("### 🧘 Stress State")
    st.warning(f"{latest['stress_state']}")

    st.markdown("### 🧭 Body Context Mode")
    st.code(physiology_context(latest))

    st.markdown("### 📊 Trend View")
    st.line_chart(df.set_index("date")[["recovery", "strain"]])
