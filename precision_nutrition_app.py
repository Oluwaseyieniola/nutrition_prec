import streamlit as st
import pandas as pd
import numpy as np
import datetime

# ----------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------
st.set_page_config(page_title="Precision Nutrition + Wearable MVP", layout="centered")
st.title("🥗 Precision Nutrition + Wearable Data MVP")

st.markdown("""
This demo integrates **synthetic wearable and nutrition‑app data** to enrich recommendations.
_All data is randomly generated for demonstration and does not represent real health metrics._
""")

# ----------------------------------------------------------
# STEP 1 — USER INPUT: BIO + GOAL
# ----------------------------------------------------------
st.header("1️⃣  Basic Profile")
with st.form("user_form"):
    age = st.number_input("Age", 18, 80, 35)
    sex = st.selectbox("Sex", ["F", "M"])
    BMI = st.number_input("Body Mass Index (BMI)", 15.0, 40.0, 25.0)
    activity_level = st.selectbox("Activity Level", ["low", "moderate", "high"])
    sleep = st.number_input("Average Sleep Hours (Last 7d)", 4.0, 9.5, 7.0)
    stress_level = st.selectbox("Stress Level", ["low", "medium", "high"])
    fasting_glucose = st.slider("Fasting Glucose (mg/dL)", 70, 130, 95)
    diversity_index = st.slider("Gut Microbiome Diversity Index", 2.0, 5.0, 3.2)
    goal = st.selectbox("Goal", ["weight_loss", "energy_boost", "glucose_control"])
    consent = st.checkbox("I consent to synthetic data processing", True)
    submitted = st.form_submit_button("Generate Insights")

# ----------------------------------------------------------
# STEP 2 — SYNTHETIC WEARABLE & APP DATA
# ----------------------------------------------------------
def generate_synthetic_wearable_data(days=7):
    """Simulate last 7 days of data from WHOOP/Fitbit/MyFitnessPal."""
    base_date = datetime.date.today()
    records = []
    np.random.seed(42)
    for i in range(days):
        date = base_date - datetime.timedelta(days=i)
        record = {
            "date": date,
            "steps": np.random.randint(3000, 13000),
            "strain_score": np.random.uniform(5, 18).round(1),
            "HRV": np.random.randint(30, 100),  # ms
            "resting_heart_rate": np.random.randint(50, 80),
            "sleep_efficiency": np.random.uniform(70, 98).round(1),
            "calories_logged": np.random.randint(1500, 3000),
            "protein_grams": np.random.randint(50, 160),
            "meal_timing_score": np.random.uniform(0.6, 1.0).round(2)
        }
        records.append(record)
    return pd.DataFrame(records)

def summarize_recent_data(df):
    """Aggregate 7‑day averages for decision logic."""
    return {
        "steps_avg": int(df["steps"].mean()),
        "strain_avg": round(df["strain_score"].mean(), 1),
        "HRV_avg": int(df["HRV"].mean()),
        "sleep_eff": round(df["sleep_efficiency"].mean(), 1),
        "protein_avg": int(df["protein_grams"].mean()),
        "meal_timing": round(df["meal_timing_score"].mean(), 2)
    }

# ----------------------------------------------------------
# STEP 3 — RECOMMENDATION ENGINE
# ----------------------------------------------------------
def nutrition_recommendation(row, wearable):
    recs = []

    # --- BODY & GOAL ---
    if row["BMI"] > 30:
        recs.append("Reduce energy intake by ~10 % and boost fiber ≥30 g/day.")
    elif row["BMI"] < 20:
        recs.append("Increase calorie density with complex carbohydrates.")

    if row["fasting_glucose"] > 110:
        recs.append("Emphasize low‑GI foods and even meal timing.")

    # --- ACTIVITY & WEARABLE METRICS ---
    if wearable["steps_avg"] < 5000:
        recs.append("Increase daily steps to ≥7500 for metabolic flexibility.")
    if wearable["strain_avg"] > 15:
        recs.append("Prioritize recovery meals rich in carbs and electrolytes.")
    if wearable["HRV_avg"] < 50:
        recs.append("Schedule lighter training; focus on sleep and hydration.")
    if wearable["sleep_eff"] < 80:
        recs.append("Aim for ≥7.5 h sleep with consistent bedtime.")
    if wearable["meal_timing"] < 0.8:
        recs.append("Eat earlier in the day to support circadian glucose control.")

    # --- MICROBIOME & LIFESTYLE ---
    if row["diversity_index"] < 3.0:
        recs.append("Add fermented foods or prebiotics to meals.")
    if row["stress_level"] == "high":
        recs.append("Practice mindfulness or relaxation ≥4× weekly.")

    # --- GOAL‑SPECIFIC ---
    if row["goal"] == "energy_boost":
        recs.append("Include slow‑release carbs (oats, quinoa) for sustained energy.")
    elif row["goal"] == "weight_loss":
        recs.append("Experiment with 16:8 feeding window and reduce added sugar.")
    elif row["goal"] == "glucose_control":
        recs.append("Pair carbs with protein/fat to blunt glucose spikes.")

    return recs if recs else ["Maintain current balanced diet."]

# ----------------------------------------------------------
# STEP 4 — PROCESS REQUEST
# ----------------------------------------------------------
if submitted:
    if not consent:
        st.error("Consent required to generate insights.")
    else:
        # collect wearable mock data
        wearable_df = generate_synthetic_wearable_data()
        wearable_summary = summarize_recent_data(wearable_df)

        user_row = {
            "BMI": BMI,
            "fasting_glucose": fasting_glucose,
            "diversity_index": diversity_index,
            "stress_level": stress_level,
            "goal": goal
        }

        recs = nutrition_recommendation(user_row, wearable_summary)

        # display results
        st.header("✅ Personalized Insights")
        for r in recs:
            st.write("•", r)

        # charts
        st.subheader("Your Synthetic Wearable Summary (last 7 days)")
        st.dataframe(wearable_df.sort_values("date", ascending=False))

        st.bar_chart(
            wearable_df[["steps", "strain_score", "sleep_efficiency"]].set_index(wearable_df["date"])
        )

        st.markdown("---")
        st.json(wearable_summary)

st.markdown("\n\n---\nPrototype © 2025 | Synthetic demonstration only – no medical use.")
