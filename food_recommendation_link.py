import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="🔗 Precision Nutrition Recommender", layout="wide")
st.title("🔗 Integrated Food Recommendation System")

st.markdown("Combines user goals + nutrition density + supply chain integrity + store availability")

# =========================================================
# STEP 1 — VALIDATE INPUT CONTRACT
# =========================================================
user = st.session_state.get("user_summary")
food_validity = st.session_state.get("food_validity")

if not isinstance(user, dict) or not food_validity:
    st.warning("Missing required context. Run main system first.")
    st.stop()

goal = user.get("goal", "balanced")

# =========================================================
# STEP 2 — FOOD NUTRITION BASE (NORMALIZED MODEL)
# =========================================================
np.random.seed(99)

foods = ["Broccoli","Chicken breast","Oats","Blueberries","Tomatoes","Eggs","Lentils"]

nutrient_df = pd.DataFrame({
    "food": foods,
    "protein": np.random.randint(3,30,len(foods)),
    "fiber": np.random.uniform(1,10,len(foods)).round(1),
    "glycemic_index": np.random.randint(30,80,len(foods)),
    "antioxidants": np.random.randint(40,100,len(foods)),

    # normalize validity into 0–1 range (IMPORTANT FIX)
    "validity_index": [
        food_validity.get(f, np.random.randint(70,95)) / 100
        for f in foods
    ]
})

# =========================================================
# STEP 3 — NORMALIZED SCORING ENGINE (FIXED SCALE MIXING)
# =========================================================
def assess_food(row, user):

    score = row["validity_index"] * 100  # normalize base

    goal = user.get("goal")

    if goal == "weight_loss":
        score += (30 - row["glycemic_index"]) * 0.5
        score += row["fiber"] * 2

    elif goal == "energy_boost":
        score += row["protein"] * 1.5
        score += row["glycemic_index"] * 0.2

    elif goal == "glucose_control":
        score += (50 - row["glycemic_index"]) * 0.6
        score += row["fiber"] * 2.2

    # stability bonus
    score += row["antioxidants"] * 0.3

    return round(max(score, 0), 2)

nutrient_df["relevance_score"] = nutrient_df.apply(
    lambda r: assess_food(r, user),
    axis=1
)

top_choices = nutrient_df.sort_values("relevance_score", ascending=False)

# =========================================================
# STEP 4 — STORE SYSTEM (QUALITY-AWARE MODEL)
# =========================================================
stores_df = pd.DataFrame({
    "food": np.repeat(foods, 2),
    "store": np.tile(
        ["Carrefour Dubai Marina", "Lulu Hypermarket Abu Dhabi"],
        len(foods)
    ),
    "stock_quality_score": np.random.uniform(0.6, 1.0, len(foods)*2).round(2),
    "price_AED": np.random.randint(4, 25, len(foods)*2)
})

# attach food score influence to stores (IMPORTANT FIX)
store_score_map = top_choices.set_index("food")["relevance_score"].to_dict()
stores_df["recommendation_score"] = stores_df.apply(
    lambda r: store_score_map.get(r["food"], 0) * r["stock_quality_score"],
    axis=1
)

# =========================================================
# STEP 5 — OUTPUT
# =========================================================
st.subheader(f"Recommended Foods → {goal.replace('_',' ').title()}")

st.dataframe(
    top_choices[[
        "food",
        "protein",
        "fiber",
        "glycemic_index",
        "validity_index",
        "relevance_score"
    ]]
)

best_food = top_choices.iloc[0]

st.success(
    f"🏆 Top Match: {best_food['food']} "
    f"(Score: {best_food['relevance_score']})"
)

# =========================================================
# STEP 6 — STORE RECOMMENDATION (NOW SORTED PROPERLY)
# =========================================================
st.subheader("UAE Store Availability (Ranked)")

merged = stores_df.sort_values("recommendation_score", ascending=False)

st.dataframe(
    merged[["food", "store", "stock_quality_score", "price_AED", "recommendation_score"]]
)

# =========================================================
# STEP 7 — EXPLANATION LAYER (IMPROVED)
# =========================================================
explanations = {
    "weight_loss": "Low glycemic load + fiber density + supply chain integrity reduce caloric spikes.",
    "energy_boost": "Protein-rich foods with moderate GI support sustained energy output.",
    "glucose_control": "Low GI + high fiber + antioxidant density improves glycemic stability."
}

st.markdown(
    "**Why this ranking works:** "
    + explanations.get(goal, "Balanced nutrition optimization across macro + micro nutrients.")
)

st.caption(
    "Prototype recommender: future upgrade path includes ML ranking, real supply chain feeds, and personalization embeddings."
)
