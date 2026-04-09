import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="🔗 Precision Nutrition Recommender", layout="wide")
st.title("🔗 Integrated Food Recommendation System")

st.markdown("Combine **user needs** + **food quality** to suggest optimal foods and stores (UAE demo).")

# ----------------------------------------------------------
# STEP 1 — Gather prior-session info
user = st.session_state.get("user_summary", {})
food_validity = st.session_state.get("food_validity", {})

if not user or not food_validity:
    st.warning("Run the main app and supply‑chain page first to generate data.")
    st.stop()

# ----------------------------------------------------------
# STEP 2 — dummy food‑nutrient profiles
np.random.seed(99)
foods = ["Broccoli","Chicken breast","Oats","Blueberries","Tomatoes","Eggs","Lentils"]
nutrient_df = pd.DataFrame({
    "food": foods,
    "protein": np.random.randint(3,30,len(foods)),
    "fiber": np.random.uniform(1,10,len(foods)).round(1),
    "glycemic_index": np.random.randint(30,80,len(foods)),
    "antioxidants": np.random.randint(40,100,len(foods)),
    "validity_index": [food_validity.get(f, np.random.randint(70,95)) for f in foods]
})

# ----------------------------------------------------------
# STEP 3 — simple rules linking user goal ↔ nutrients ↔ validity
def assess_food(row, user):
    score = row["validity_index"]
    if user["goal"] == "weight_loss":
        score += 0.3*(30-row["glycemic_index"])
        score += 0.2*row["fiber"]
    elif user["goal"] == "energy_boost":
        score += 0.3*row["protein"] + 0.1*row["glycemic_index"]
    elif user["goal"] == "glucose_control":
        score += 0.4*(50-row["glycemic_index"]) + 0.2*row["fiber"]
    return round(score,1)

nutrient_df["relevance_score"] = nutrient_df.apply(lambda r: assess_food(r,user), axis=1)
top_choices = nutrient_df.sort_values("relevance_score",ascending=False)

# ----------------------------------------------------------
# STEP 4 — simulate UAE store availability
stores_df = pd.DataFrame({
    "food": np.repeat(foods, 2),
    "store": np.tile(["Carrefour Dubai Marina", "Lulu Hypermarket Abu Dhabi"], len(foods)),
    "stock_quality": np.random.choice(["High Integrity","Standard"], len(foods)*2, p=[0.7,0.3]),
    "price_AED": np.random.randint(4,25,len(foods)*2)
})

# ----------------------------------------------------------
# STEP 5 — display results
st.subheader(f"Recommended Foods for Goal → **{user['goal'].replace('_',' ').title()}**")
st.dataframe(top_choices[["food","protein","fiber","glycemic_index","validity_index","relevance_score"]])

best_food = top_choices.iloc[0]["food"]
st.success(f"🏆 Top Match: **{best_food}** — suits your {user['goal']} plan and maintains {top_choices.iloc[0]['validity_index']} % nutrient integrity.")

st.subheader("UAE Stores Carrying Your Recommended Foods")
merged = pd.merge(top_choices[["food"]].head(3), stores_df, on="food")
st.dataframe(merged)

# Explain reasoning
explanations = {
    "weight_loss": "Chosen foods balance low glycemic index, higher fiber, and high integrity to aid slow glucose release.",
    "energy_boost": "High‑validity protein sources support recovery and sustained energy across training days.",
    "glucose_control": "Low‑GI foods with strong supply‑chain integrity help flatten post‑meal glucose peaks."
}
st.markdown("**Why These Foods?** " + explanations.get(user["goal"], ""))

st.caption("All metrics synthetic – for prototype illustration only – data can link to real Nutritionix / GS1 / blockchain networks later.")
