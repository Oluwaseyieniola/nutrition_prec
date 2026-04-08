import streamlit as st
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="Food Supply‑Chain Monitor", layout="wide")
st.title("🌾 Food Supply‑Chain & Nutrient Validity Monitor")

st.markdown("""
Track **every stage** of a food item's journey — from farm to plate —  
then evaluate expected **nutrient integrity** on arrival.
All numbers below are synthetic for demonstration.
""")

# ----------------------------------------------------------
# STEP 1 — select food
foods = ["Broccoli", "Chicken breast", "Oats", "Blueberries", "Tomatoes", "Eggs"]
food_selected = st.selectbox("Select a food to inspect:", foods)

# ----------------------------------------------------------
# STEP 2 — generate synthetic supply‑chain data
np.random.seed(abs(hash(food_selected)) % (10**6))
stages = ["Farm Harvest", "Processing", "Cold Storage", "Transport", "Retail Shelf", "Home Storage"]
records = []
base_date = datetime.date.today()

def simulate_loss():
    """Return nutrient‑loss % for the stage."""
    return np.random.uniform(0, 8)

for i, stage in enumerate(stages):
    record = {
        "stage": stage,
        "temperature_°C": round(np.random.uniform(-1, 25), 1),
        "duration_days": round(np.random.uniform(0.5, 6), 1),
        "humidity_%": round(np.random.uniform(40, 95), 1),
        "handling_score_(1‑10)": round(np.random.uniform(5, 10), 1),
        "nutrient_loss_%": simulate_loss()
    }
    records.append(record)

df = pd.DataFrame(records)

# ----------------------------------------------------------
# STEP 3 — compute validity index
def compute_validity(row):
    freshness_penalty = (row["temperature_°C"] - 4) * 0.02 if row["temperature_°C"] > 4 else 0
    handling_bonus = (row["handling_score_(1‑10)"] / 10) * 0.05
    return max(0, 1 - (row["nutrient_loss_%"]/100) - freshness_penalty + handling_bonus)

df["validity_index"] = df.apply(compute_validity, axis=1)

total_validity = round(df["validity_index"].mean() * 100, 1)
nutrient_loss_total = round(df["nutrient_loss_%"].sum(), 1)

# ----------------------------------------------------------
# STEP 4 — display report
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader(f"Supply‑Chain Conditions for {food_selected}")
    st.dataframe(df.set_index("stage"), use_container_width=True)
with col2:
    st.metric("Estimated FG Nutrient Integrity (%)", 100 - nutrient_loss_total)
    st.metric("Overall Validity Index (0–100)", total_validity)

st.bar_chart(df.set_index("stage")[["nutrient_loss_%", "validity_index"]])

# ----------------------------------------------------------
# STEP 5 — Food‑quality insights
st.subheader("Actionable Food & Nutrition Insights")

if total_validity < 75:
    st.warning(f"⚠️ This batch of {food_selected} experienced several quality losses — "
               f"expect reduced vitamin or amino‑acid content.")
else:
    st.success(f"✅ {food_selected} retains most of its nutritional value.")

# Personalized suggestions
personal_messages = [
    f"If your wearable data shows high strain this week, "
    f"prioritize **fresh {food_selected.lower()}** from local suppliers for higher micronutrient content.",
    f"Select {food_selected.lower()} with sealed cold‑chain history to maintain above‑80% nutrient integrity.",
    f"Combine {food_selected.lower()} with vitamin C‑rich foods to offset small storage losses."
]
st.markdown("<br>".join(f"• {m}" for m in personal_messages), unsafe_allow_html=True)

st.caption("Synthetic demo – not based on actual supply‑chain tracking.")
