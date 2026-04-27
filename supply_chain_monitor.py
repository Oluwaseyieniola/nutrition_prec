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
# IMAGE MAP (NEW – adds visuals to your foods)
# =========================================================
FOOD_IMAGES = {
    "Salmon": "[images.unsplash.com](https://images.unsplash.com/photo-1599084993091-1cb5c0721cc6)",
    "Oats": "[images.unsplash.com](https://images.unsplash.com/photo-1517673400267-0251440c45dc)",
    "Eggs": "[images.unsplash.com](https://images.unsplash.com/photo-1506976785307-8732e854ad03)",
    "Spinach": "[images.unsplash.com](https://images.unsplash.com/photo-1576045057995-568f588f82fb)",
    "Chicken Breast": "[images.unsplash.com](https://images.unsplash.com/photo-1604503468506-a8da13d82791)",
    "Avocado": "[images.unsplash.com](https://images.unsplash.com/photo-1523049673857-eb18f1d7b578)",
    "Blueberries": "[images.unsplash.com](https://images.unsplash.com/photo-1498557850523-fd3d118b962e)"
}

# =========================================================
# DOMAIN
# =========================================================
FOODS = ["Salmon","Oats","Eggs","Spinach","Chicken Breast","Avocado","Blueberries"]

FOOD_LIBRARY = {
    "Salmon": {"good_for": ["fitness","glucose_control"], "protein": 25, "long_term": "Improves inflammation & muscle recovery."},
    "Oats": {"good_for": ["glucose_control"], "fiber": 8, "long_term": "Lowers glucose spikes & improves gut health."},
    "Eggs": {"good_for": ["fitness"], "protein": 12, "long_term": "Provides complete proteins & supports muscle repair."},
    "Spinach": {"good_for": ["glucose_control"], "fiber": 4, "long_term": "Strong in magnesium; supports glucose & metabolism."},
    "Chicken Breast": {"good_for": ["fitness","fat_loss"], "protein": 30, "long_term": "High satiety protein; supports lean muscle."},
    "Avocado": {"good_for": ["fat_loss"], "fiber": 6, "long_term": "Healthy fats help stabilize appetite & hormones."},
    "Blueberries": {"good_for": ["glucose_control"], "fiber": 5, "long_term": "Antioxidants support vascular & brain health."},
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
# PAGE UI
# =========================================================
st.title("🥗 Food Intelligence System (Visual Upgrade)")

page = st.sidebar.radio("Navigation", [
    "Create User",
    "View Health",
    "Recommendations"
])

# =========================================================
# PAGE 1 — CREATE USER
# =========================================================
if page == "Create User":
    w = st.number_input("Weight (kg)", 40.0, 150.0, 75.0)
    h = st.number_input("Height (m)", 1.4, 2.2, 1.75)
    goal = st.selectbox("Goal", ["fitness","fat_loss","glucose_control"])

    if st.button("Create User"):
        create_user(w, h, goal)
        st.success("User created successfully.")

# =========================================================
# PAGE 2 — VIEW HEALTH
# =========================================================
elif page == "View Health":
    users = pd.DataFrame(st.session_state["users"])

    if users.empty:
        st.info("No users yet.")
        st.stop()

    user_id = st.selectbox("Select User", users["id"])
    user = safe_get_user(users, user_id)

    st.subheader("🏥 Health Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("BMI", user["bmi"])
    c2.metric("Sleep (hrs)", round(user["sleep"],2))
    c3.metric("Steps/day", user["steps"])

    risk = metabolic_score(user)
    st.write(f"**Metabolic Risk:** :red[{risk.upper()}]")

# =========================================================
# PAGE 3 — RECOMMENDATIONS (enhanced visuals)
# =========================================================
elif page == "Recommendations":
    users = pd.DataFrame(st.session_state["users"])
    if users.empty:
        st.info("No users yet")
        st.stop()

    user_id = st.selectbox("Select User", users["id"])
    user = safe_get_user(users, user_id)

    st.subheader("🍽 Personalized Food Recommendations")

    recs = generate_recommendations(user)

    for _, row in recs.iterrows():
        food = row['food']
        img = FOOD_IMAGES.get(food, None)
        info = FOOD_LIBRARY.get(food, {})

        with st.container(border=True):
            cols = st.columns([1, 2])

            with cols[0]:
                if img:
                    st.image(img, use_container_width=True)

            with cols[1]:
                st.markdown(f"### {food}")
                st.write(f"**Score:** {row['score']}")
                st.write(f"**Protein:** {row['protein']} g")
                st.write(f"**Fiber:** {row['fiber']} g")
                st.write(f"**Good for:** {', '.join(info.get('good_for', []))}")
                st.write(f"**Long-term effect:** {info.get('long_term','')}")

            st.markdown("---")
