import streamlit as st
import pandas as pd
import numpy as np

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Precision Nutrition MVP", layout="centered")
st.title("🥗 Precision Nutrition – MVP (Synthetic Data)")

st.markdown("""
This demo generates **synthetic nutrition recommendations** based on user‑entered data.  
_All data here is fictional. No health information is stored or transmitted._
""")

# -------------------- INPUT FORM --------------------
st.header("Enter Your Synthetic Profile")

with st.form("user_form"):
    age = st.number_input("Age", 18, 80, 35)
    sex = st.selectbox("Sex", ["F", "M"])
    BMI = st.number_input("Body Mass Index (BMI)", 15.0, 40.0, 25.0)
    activity_level = st.selectbox("Activity Level", ["low", "moderate", "high"])
    sleep = st.number_input("Average Sleep Hours", 4.0, 9.5, 7.0)
    stress = st.selectbox("Stress Level", ["low", "medium", "high"])
    fasting_glucose = st.slider("Fasting Glucose (mg/dL)", 70, 130, 95)
    diversity_index = st.slider("Gut Microbiome Diversity Index", 2.0, 5.0, 3.2)
    goal = st.selectbox("Wellness Goal", ["weight_loss", "energy_boost", "glucose_control"])
    consent = st.checkbox("I consent to synthetic data processing for demo purposes", True)

    submitted = st.form_submit_button("Generate Recommendation")

# -------------------- RECOMMENDER LOGIC --------------------
def nutrition_recommendation(BMI, glucose, activity, div, sleep, stress, goal):
    recs = []
    if BMI > 30:
        recs.append("Reduce calories by 10 % and increase fiber ≥30 g/day.")
    elif BMI < 20:
        recs.append("Increase calorie density and complex carbohydrates.")
    if glucose > 110:
        recs.append("Focus on low‑GI foods and even meal timing.")
    if activity == "low":
        recs.append("Add 20–30 min brisk walking 3×/week.")
    elif activity == "high":
        recs.append("Ensure ≥1.4 g/kg protein intake for recovery.")
    if div < 3.0:
        recs.append("Include fermented foods or prebiotics to support gut health.")
    if sleep < 6:
        recs.append("Aim for at least 7 h sleep for metabolic stability.")
    if stress == "high":
        recs.append("Incorporate mindfulness or relaxation 4× weekly.")
    if goal == "energy_boost":
        recs.append("Add slow‑release carbs (oats, quinoa) for sustained energy.")
    elif goal == "weight_loss":
        recs.append("Experiment with a 16:8 eating window and reduce added sugar.")
    elif goal == "glucose_control":
        recs.append("Pair carbs with protein/fat to blunt glucose spikes.")
    return recs or ["Maintain a balanced diet and active lifestyle."]

# -------------------- OUTPUT SECTION --------------------
if submitted:
    if not consent:
        st.warning("Consent required to generate recommendations (demo ethics simulation).")
    else:
        recs = nutrition_recommendation(BMI, fasting_glucose, activity_level, diversity_index, sleep, stress, goal)
        st.success("✅ Synthetic Personalized Nutrition Plan Generated")
        st.subheader("Your Recommendations")
        for r in recs:
            st.write("•", r)

        # mock "insights" visualization
        st.markdown("### Biomarker Snapshot (Synthetic)")
        st.bar_chart(pd.DataFrame({
            "Metric": ["BMI", "Glucose", "Microbiome Diversity"],
            "Values": [BMI, fasting_glucose, diversity_index]
        }).set_index("Metric"))

st.markdown("---")
st.caption("Prototype © 2025 | For educational demonstration only – not for medical use.")
