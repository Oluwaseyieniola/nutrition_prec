import streamlit as st
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="Food Intelligence System", layout="wide")

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
# IMAGE MAP
# =========================================================
FOOD_IMAGES = {
    "Salmon": "https://images.unsplash.com/photo-1599084993091-1cb5c0721cc6?w=800",
    "Oats": "https://images.unsplash.com/photo-1517673400267-0251440c45dc?w=800",
    "Eggs": "https://images.unsplash.com/photo-1506976785307-8732e854ad03?w=800",
    "Spinach": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=800",
    "Chicken Breast": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=800",
    "Avocado": "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=800",
    "Blueberries": "https://images.unsplash.com/photo-1498557850523-fd3d118b962e?w=800"
}

# =========================================================
# DOMAIN
# =========================================================
FOODS = ["Salmon","Oats","Eggs","Spinach","Chicken Breast","Avocado","Blueberries"]

FOOD_LIBRARY = {
    "Salmon": {"good_for": ["fitness","glucose_control"], "long_term": "Improves inflammation & muscle recovery."},
    "Oats": {"good_for": ["glucose_control"], "long_term": "Lowers glucose spikes & improves gut health."},
    "Eggs": {"good_for": ["fitness"], "long_term": "Provides complete proteins & supports muscle repair."},
    "Spinach": {"good_for": ["glucose_control"], "long_term": "Strong in magnesium; supports metabolism."},
    "Chicken Breast": {"good_for": ["fitness","fat_loss"], "long_term": "High satiety protein; supports lean muscle."},
    "Avocado": {"good_for": ["fat_loss"], "long_term": "Healthy fats stabilize appetite & hormones."},
    "Blueberries": {"good_for": ["glucose_control"], "long_term": "Antioxidants support vascular & brain health."},
}

# =========================================================
# DEMO NUTRITION (Deterministic)
# =========================================================
DEMO_NUTRITION = {
    "Salmon": {"protein": 25.0, "fiber": 0.0, "calories": 208},
    "Oats": {"protein": 16.9, "fiber": 10.6, "calories": 389},
    "Eggs": {"protein": 12.6, "fiber": 0.0, "calories": 155},
    "Spinach": {"protein": 2.9, "fiber": 2.2, "calories": 23},
    "Chicken Breast": {"protein": 31.0, "fiber": 0.0, "calories": 165},
    "Avocado": {"protein": 2.0, "fiber": 6.7, "calories": 160},
    "Blueberries": {"protein": 0.7, "fiber": 2.4, "calories": 57},
}

def get_demo_nutrition(food):
    return DEMO_NUTRITION.get(food, {"protein": 0, "fiber": 0, "calories": 0})

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

# =========================================================
# FEEDBACK SYSTEM
# =========================================================
def log_decision(user_id, food, decision):
    st.session_state["history"].append({
        "user_id": user_id,
        "food": food,
        "decision": decision,
        "time": datetime.datetime.now()
    })

def get_user_history(user_id):
    df = pd.DataFrame(st.session_state["history"])
    if df.empty:
        return pd.DataFrame()
    return df[df["user_id"] == user_id]

def behavior_patterns(history_df):
    if history_df.empty:
        return {}

    prefs = {}
    grouped = history_df.groupby("food")

    for food, group in grouped:
        accepted = len(group[group["decision"] == "accepted"])
        total = len(group)
        prefs[food] = accepted / total if total else 0

    return prefs

# =========================================================
# RECOMMENDATION ENGINE
# =========================================================
def food_score(food, user, prefs):
    base = 50
    lib = FOOD_LIBRARY.get(food, {})
    nutrients = get_demo_nutrition(food)

    if user["goal"] in lib.get("good_for", []):
        base += 20

    base += nutrients["protein"] * 0.8
    base += nutrients["fiber"] * 1.5

    if user["goal"] == "fat_loss":
        base -= nutrients["calories"] * 0.05

    preference = prefs.get(food, None)
    if preference is not None:
        base += (preference - 0.5) * 40

    return round(base, 1), nutrients

def generate_recommendations(user, user_id):
    history_df = get_user_history(user_id)
    prefs = behavior_patterns(history_df)

    rows = []

    for food in FOODS:
        score, nutrients = food_score(food, user, prefs)

        rows.append({
            "food": food,
            "score": score,
            "protein": nutrients["protein"],
            "fiber": nutrients["fiber"]
        })

    return pd.DataFrame(rows).sort_values("score", ascending=False)

# =========================================================
# DATA OPS
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
st.title("🥗 Food Intelligence System")

page = st.sidebar.radio("Navigation", [
    "Create User",
    "View Health",
    "Recommendations"
])

# ---------------- CREATE USER ----------------
if page == "Create User":
    w = st.number_input("Weight (kg)", 40.0, 150.0, 75.0)
    h = st.number_input("Height (m)", 1.4, 2.2, 1.75)
    goal = st.selectbox("Goal", ["fitness","fat_loss","glucose_control"])

    if st.button("Create User"):
        create_user(w, h, goal)
        st.success("User created successfully.")

# ---------------- VIEW HEALTH ----------------
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
    c2.metric("Sleep", round(user["sleep"],2))
    c3.metric("Steps", user["steps"])

    risk = metabolic_score(user)
    st.write(f"**Metabolic Risk:** {risk.upper()}")

# ---------------- RECOMMENDATIONS ----------------
elif page == "Recommendations":
    users = pd.DataFrame(st.session_state["users"])

    if users.empty:
        st.info("No users yet")
        st.stop()

    user_id = st.selectbox("Select User", users["id"])
    user = safe_get_user(users, user_id)

    st.subheader("🍽 Personalized Food Recommendations")

    recs = generate_recommendations(user, user_id)

    for _, row in recs.iterrows():
        food = row["food"]
        img = FOOD_IMAGES.get(food)
        info = FOOD_LIBRARY.get(food, {})

        with st.container(border=True):
            cols = st.columns([1,2])

            with cols[0]:
                if img:
                    st.image(img, use_container_width=True)

            with cols[1]:
                st.markdown(f"### {food}")
                st.write(f"Score: {row['score']}")
                st.write(f"Protein: {row['protein']} g")
                st.write(f"Fiber: {row['fiber']} g")
                st.write(f"Good for: {', '.join(info.get('good_for', []))}")
                st.write(f"{info.get('long_term','')}")

                c1, c2 = st.columns(2)

                if c1.button(f"👍 Accept {food}", key=f"a_{user_id}_{food}"):
                    log_decision(user_id, food, "accepted")
                    st.rerun()

                if c2.button(f"👎 Reject {food}", key=f"r_{user_id}_{food}"):
                    log_decision(user_id, food, "rejected")
                    st.rerun()

    # Show learned preferences
    history_df = get_user_history(user_id)
    if not history_df.empty:
        st.subheader("🧠 Learned Preferences")
        st.write(behavior_patterns(history_df))
