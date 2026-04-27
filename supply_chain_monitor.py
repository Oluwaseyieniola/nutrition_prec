import streamlit as st
import pandas as pd
import numpy as np
import datetime

# =========================================================
# INIT (Safe State)
# =========================================================
def init_state():
    if "users" not in st.session_state:
        st.session_state["users"] = []
    if "history" not in st.session_state:
        st.session_state["history"] = []

init_state()

# =========================================================
# DOMAIN
# =========================================================
FOODS = ["Salmon","Oats","Eggs","Spinach","Chicken Breast","Avocado","Blueberries"]

FOOD_LIBRARY = {
    "Salmon": {"good_for": ["fitness","glucose_control"], "protein": 25},
    "Oats": {"good_for": ["glucose_control"], "fiber": 8},
    "Eggs": {"good_for": ["fitness"], "protein": 12},
    "Spinach": {"good_for": ["glucose_control"], "fiber": 4},
    "Chicken Breast": {"good_for": ["fitness","fat_loss"], "protein": 30},
    "Avocado": {"good_for": ["fat_loss"], "fiber": 6},
    "Blueberries": {"good_for": ["glucose_control"], "fiber": 5},
}

# =========================================================
# UTILS
# =========================================================
def safe_get_user(users_df, user_id):
    filtered = users_df[users_df["id"] == user_id]
    if filtered.empty:
        raise ValueError("User not found")
    return filtered.iloc[0].to_dict()

def safe_mean(series):
    return float(series.mean()) if len(series) > 0 else None

# =========================================================
# SERVICES
# =========================================================

# --- Wearable ---
def generate_wearable_data(user_id, days=7):
    rng = np.random.default_rng(user_id)
    rows = []
    for i in range(days):
        rows.append({
            "date": datetime.date.today() - datetime.timedelta(days=i),
            "sleep": round(rng.uniform(5, 8), 2),
            "steps": int(rng.integers(3000, 12000)),
            "recovery": int(rng.integers(30, 90)),
        })
    return pd.DataFrame(rows)

def aggregate_metrics(df):
    if df is None or df.empty:
        return {}
    return {
        "sleep": safe_mean(df["sleep"]),
        "steps": int(df["steps"].mean()),
        "recovery": int(df["recovery"].mean()),
    }

# --- Health ---
def calculate_bmi(w, h):
    return round(w / (h ** 2), 1)

def metabolic_score(user):
    score = 0
    if user["bmi"] > 27: score += 2
    if user["sleep"] and user["sleep"] < 6: score += 2
    if user["steps"] and user["steps"] < 6000: score += 2

    if score >= 4:
        return "high"
    elif score >= 2:
        return "moderate"
    return "low"

# --- Behavior ---
def behavior_patterns(history_df):
    if history_df.empty:
        return {"accept_rate": 0}

    accepted = len(history_df[history_df["decision"] == "accepted"])
    total = len(history_df)

    return {"accept_rate": accepted / total if total else 0}

# --- Supply (Deterministic) ---
def simulate_supply(food):
    seed = abs(hash(food)) % 100000
    rng = np.random.default_rng(seed)

    return {
        "protein": round(rng.uniform(5, 30), 1),
        "fiber": round(rng.uniform(1, 10), 1)
    }

# --- Recommendation ---
def food_score(food, user):
    base = 50
    lib = FOOD_LIBRARY.get(food, {})

    if user["goal"] == "fitness" and "fitness" in lib.get("good_for", []):
        base += 20
    if user["goal"] == "glucose_control" and "glucose_control" in lib.get("good_for", []):
        base += 20
    if user["goal"] == "fat_loss" and "fat_loss" in lib.get("good_for", []):
        base += 20

    nutrients = simulate_supply(food)
    base += nutrients.get("protein", 0) / 2
    base += nutrients.get("fiber", 0)

    return round(base, 1), nutrients

def generate_recommendations(user):
    rows = []

    for food in FOODS:
        score, nutrients = food_score(food, user)

        rows.append({
            "food": food,
            "score": score,
            "protein": nutrients["protein"],
            "fiber": nutrients["fiber"]
        })

    df = pd.DataFrame(rows).sort_values("score", ascending=False)
    return df

# =========================================================
# DATA OPERATIONS
# =========================================================
def create_user(weight, height, goal):
    user_id = len(st.session_state["users"]) + 1

    wearable = generate_wearable_data(user_id)
    metrics = aggregate_metrics(wearable)

    user = {
        "id": user_id,
        "weight": weight,
        "height": height,
        "bmi": calculate_bmi(weight, height),
        "sleep": metrics.get("sleep"),
        "steps": metrics.get("steps"),
        "recovery": metrics.get("recovery"),
        "goal": goal
    }

    st.session_state["users"].append(user)
    st.session_state[f"wearable_{user_id}"] = wearable

# =========================================================
# UI
# =========================================================
st.title("Food Intelligence System (Refactored)")

page = st.sidebar.radio("Navigation", [
    "Create User",
    "View Health",
    "Recommendations"
])

# --- CREATE USER ---
if page == "Create User":
    w = st.number_input("Weight", 40.0, 150.0, 75.0)
    h = st.number_input("Height", 1.4, 2.2, 1.75)
    goal = st.selectbox("Goal", ["fitness","fat_loss","glucose_control"])

    if st.button("Create"):
        create_user(w, h, goal)
        st.success("User created")

# --- VIEW HEALTH ---
elif page == "View Health":
    users = pd.DataFrame(st.session_state["users"])

    if users.empty:
        st.info("No users yet")
        st.stop()

    user_id = st.selectbox("User", users["id"])

    try:
        user = safe_get_user(users, user_id)
    except Exception as e:
        st.error(str(e))
        st.stop()

    st.write("### Health Overview")
    st.write(user)

    risk = metabolic_score(user)
    st.write(f"Metabolic Risk: **{risk.upper()}**")

# --- RECOMMENDATIONS ---
elif page == "Recommendations":
    users = pd.DataFrame(st.session_state["users"])

    if users.empty:
        st.info("No users yet")
        st.stop()

    user_id = st.selectbox("User", users["id"])

    try:
        user = safe_get_user(users, user_id)
    except Exception as e:
        st.error(str(e))
        st.stop()

    st.write("### Recommendations")

    recs = generate_recommendations(user)

    for _, row in recs.iterrows():
        with st.container(border=True):
            st.markdown(f"### {row['food']}")
            st.write(f"Score: {row['score']}")
            st.write(f"Protein: {row['protein']} | Fiber: {row['fiber']}")
