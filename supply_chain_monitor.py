import streamlit as st
import pandas as pd
import numpy as np
import datetime
import hashlib

st.set_page_config(page_title="Food Intelligence System", layout="centered")

# =========================================================
# 🌍 FOOD DATA
# =========================================================
FOODS = [
    "Salmon","Oats","Blueberries","Lentils","Spinach",
    "Chicken Breast","Avocado","Eggs","Brown Rice","Yogurt"
]

FOOD_FEATURES = {
    "Salmon": ["protein","fat"],
    "Oats": ["carb","fiber"],
    "Blueberries": ["antioxidant"],
    "Lentils": ["protein","fiber"],
    "Spinach": ["micronutrient"],
    "Chicken Breast": ["protein"],
    "Avocado": ["fat"],
    "Eggs": ["protein","fat"],
    "Brown Rice": ["carb"],
    "Yogurt": ["protein","probiotic"]
}

PRICE_MAP = {
    "Salmon": 15, "Oats": 3, "Blueberries": 6,
    "Lentils": 2, "Spinach": 4,
    "Chicken Breast": 10, "Avocado": 5,
    "Eggs": 4, "Brown Rice": 3, "Yogurt": 5
}

# =========================================================
# SESSION
# =========================================================
if "users" not in st.session_state:
    st.session_state["users"] = []

if "history" not in st.session_state:
    st.session_state["history"] = []

# =========================================================
# WEARABLE ENGINE
# =========================================================
class WearableEngine:
    @staticmethod
    def simulate(user_id):
        np.random.seed(user_id)
        return {
            "sleep": round(np.random.uniform(4.5, 8.5),2),
            "hrv": np.random.randint(40,100),
            "recovery": np.random.randint(30,95),
            "strain": round(np.random.uniform(5,18),1)
        }

# =========================================================
# HEALTH + LIFESTYLE
# =========================================================
def calculate_bmi(w,h):
    return round(w/(h**2),1)

def lifestyle_score(user):
    score = 0

    if user["sleep"] >= 7:
        score += 1
    if user["activity"] == "high":
        score += 1
    if user["stress"] == "low":
        score += 1

    return score

# =========================================================
# SUPPLY CHAIN
# =========================================================
def simulate_supply(food):
    seed = int(hashlib.md5(food.encode()).hexdigest(),16)%10**6
    np.random.seed(seed)

    data=[]
    for stage in ["Farm","Transport","Retail"]:
        loss = np.random.uniform(0.7,1.0)
        data.append({
            "Stage":stage,
            "Quality":round(loss,2)
        })

    return pd.DataFrame(data)

def explain_supply(df):
    msgs=[]
    for _,r in df.iterrows():
        if r["Quality"]<0.8:
            state="lost a noticeable amount of nutrients"
        else:
            state="remained mostly fresh"

        msgs.append(f"At the {r['Stage']} stage, the food {state}.")
    return msgs

# =========================================================
# BEHAVIOR ENGINE
# =========================================================
def behavior_pattern(user_id):
    df = pd.DataFrame(st.session_state["history"])
    if df.empty:
        return {}

    df = df[df["user_id"]==user_id]

    pattern={}
    for _,r in df.iterrows():
        f = r["food"]
        if f not in pattern:
            pattern[f]=0

        if r["decision"]=="accepted":
            pattern[f]+=1
        else:
            pattern[f]-=1

    return pattern

# =========================================================
# MEAL ENGINE
# =========================================================
def recommend_meal(user, pattern):
    meal = []

    needed = ["protein","carb","fat","fiber"]

    for nutrient in needed:
        for food,features in FOOD_FEATURES.items():
            if nutrient in features:
                if pattern.get(food,0)>=0:
                    meal.append(food)
                    break

    return list(set(meal))

def explain_meal(meal):
    explanation = "This meal is designed to support your body by combining "

    for food in meal:
        explanation += f"{food}, "

    explanation += "which together provide balanced nutrition for energy, recovery, and long-term health."

    return explanation

# =========================================================
# HEALTH INTERPRETATION
# =========================================================
def interpret_health(user):
    msgs=[]

    if user["sleep"]<6:
        msgs.append("Your sleep is low, which may lead to fatigue and weaker immunity over time.")

    if user["recovery"]<50:
        msgs.append("Your body is under stress and may not recover properly.")

    if user["bmi"]>27:
        msgs.append("Your BMI suggests a higher risk of metabolic diseases.")

    return msgs

# =========================================================
# USER DATA
# =========================================================
def create_user(w,h,goal,activity,stress):
    user_id=len(st.session_state["users"])+1
    wearable = WearableEngine.simulate(user_id)

    user={
        "id":user_id,
        "weight":w,
        "height":h,
        "bmi":calculate_bmi(w,h),
        "goal":goal,
        "activity":activity,
        "stress":stress,
        **wearable
    }

    st.session_state["users"].append(user)

def load_users():
    return pd.DataFrame(st.session_state["users"])

def save_decision(user_id,food,decision):
    st.session_state["history"].append({
        "user_id":user_id,
        "food":food,
        "decision":decision,
        "time":datetime.datetime.now()
    })

# =========================================================
# UI
# =========================================================
st.title("🥗 Food Intelligence System")

page = st.sidebar.radio("Navigation",[
    "Create User",
    "Health Insights",
    "Decision Engine",
    "Habit Tracker"
])

# =========================================================
# CREATE USER
# =========================================================
if page=="Create User":
    w=st.number_input("Weight",40.0,150.0,75.0)
    h=st.number_input("Height",1.4,2.2,1.75)
    goal=st.selectbox("Goal",["fitness","fat_loss","glucose_control"])
    activity=st.selectbox("Activity",["low","moderate","high"])
    stress=st.selectbox("Stress",["low","medium","high"])

    if st.button("Create"):
        create_user(w,h,goal,activity,stress)
        st.success("User created")

# =========================================================
# HEALTH INSIGHTS (MAIN FEATURE)
# =========================================================
elif page=="Health Insights":
    users=load_users()
    if users.empty:
        st.warning("Create user first")
        st.stop()

    user_id=st.selectbox("User",users["id"])
    user=users[users["id"]==user_id].iloc[0]

    food=st.selectbox("Food",FOODS)

    st.subheader("🌍 Food Journey")
    df=simulate_supply(food)
    for msg in explain_supply(df):
        st.write(msg)

    st.subheader("🧠 Your Health")
    for msg in interpret_health(user):
        st.write(f"- {msg}")

    st.subheader("🧠 Behavior Pattern")
    pattern=behavior_pattern(user_id)
    st.json(pattern)

    st.subheader("🥗 Recommended Meal")
    meal=recommend_meal(user,pattern)
    st.write(meal)
    st.write(explain_meal(meal))

# =========================================================
# DECISION ENGINE
# =========================================================
elif page=="Decision Engine":
    users=load_users()
    if users.empty:
        st.warning("Create user first")
        st.stop()

    user_id=st.selectbox("User",users["id"])
    food=st.selectbox("Food",FOODS)

    if st.button("Accept"):
        save_decision(user_id,food,"accepted")
        st.success("Saved")

    if st.button("Reject"):
        save_decision(user_id,food,"rejected")
        st.warning("Saved")

# =========================================================
# HABIT TRACKER
# =========================================================
elif page=="Habit Tracker":
    df=pd.DataFrame(st.session_state["history"])
    if not df.empty:
        st.dataframe(df)
    else:
        st.write("No data yet")
