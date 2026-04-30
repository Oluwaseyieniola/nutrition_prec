import streamlit as st
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="Food Intelligence System", layout="wide")

# =========================================================
# INIT STATE
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
# DOMAIN DATA
# =========================================================
FOODS = ["Salmon","Oats","Eggs","Spinach","Chicken Breast","Avocado","Blueberries"]

FOOD_LIBRARY = {
    "Salmon": {"good_for": ["fitness","glucose_control"], "long_term": "Improves inflammation & muscle recovery."},
    "Oats": {"good_for": ["glucose_control"], "long_term": "Improves gut health."},
    "Eggs": {"good_for": ["fitness"], "long_term": "Supports muscle repair."},
    "Spinach": {"good_for": ["glucose_control"], "long_term": "Supports metabolism."},
    "Chicken Breast": {"good_for": ["fitness","fat_loss"], "long_term": "Supports lean muscle."},
    "Avocado": {"good_for": ["fat_loss"], "long_term": "Stabilizes appetite."},
    "Blueberries": {"good_for": ["glucose_control"], "long_term": "Supports brain health."},
}

# =========================================================
# DEMO NUTRITION
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
# SUPPLY CHAIN DATA
# =========================================================
SUPPLY_CHAIN_DATA = {
    "Salmon": {"freshness": 0.8, "processing": 0.2, "risk": 0.3, "stores": ["Carrefour", "Spinneys"]},
    "Oats": {"freshness": 0.95, "processing": 0.4, "risk": 0.1, "stores": ["Lulu Hypermarket", "Union Coop"]},
    "Eggs": {"freshness": 0.9, "processing": 0.1, "risk": 0.2, "stores": ["Carrefour", "Choithrams"]},
    "Spinach": {"freshness": 0.85, "processing": 0.1, "risk": 0.25, "stores": ["Organic Foods & Café", "Union Coop"]},
    "Chicken Breast": {"freshness": 0.88, "processing": 0.3, "risk": 0.35, "stores": ["Carrefour", "Lulu Hypermarket"]},
    "Avocado": {"freshness": 0.75, "processing": 0.05, "risk": 0.4, "stores": ["Spinneys", "Waitrose UAE"]},
    "Blueberries": {"freshness": 0.7, "processing": 0.05, "risk": 0.45, "stores": ["Waitrose UAE", "Carrefour"]},
}

def get_supply_chain(food):
    return SUPPLY_CHAIN_DATA.get(food, {"freshness": 0.5, "processing": 0.5, "risk": 0.5, "stores": []})

def supply_score(s):
    return round((s["freshness"]*40) + ((1-s["processing"])*30) + ((1-s["risk"])*30), 1)

# =========================================================
# UTIL FUNCTIONS
# =========================================================
def safe_get_user(users_df, user_id):
    return users_df[users_df["id"] == user_id].iloc[0].to_dict()

def safe_mean(series):
    return float(series.mean()) if len(series) > 0 else None

# =========================================================
# SERVICES
# =========================================================
def generate_wearable_data(user_id):
    rng = np.random.default_rng(user_id)
    return pd.DataFrame([{
        "sleep": round(rng.uniform(5,8),2),
        "steps": int(rng.integers(3000,12000)),
        "recovery": int(rng.integers(30,90))
    } for _ in range(7)])

def aggregate_metrics(df):
    return {
        "sleep": safe_mean(df["sleep"]),
        "steps": int(df["steps"].mean()),
        "recovery": int(df["recovery"].mean()),
    }

def calculate_bmi(w,h):
    return round(w/(h**2),1)

def metabolic_score(user):
    score = 0
    if user["bmi"]>27: score+=2
    if user["sleep"]<6: score+=2
    if user["steps"]<6000: score+=2
    return "high" if score>=4 else "moderate" if score>=2 else "low"

# =========================================================
# FEEDBACK SYSTEM
# =========================================================
def log_decision(user_id, food, decision):
    st.session_state["history"].append({
        "user_id": user_id,
        "food": food,
        "decision": decision
    })

def get_user_history(user_id):
    df = pd.DataFrame(st.session_state["history"])
    return df[df["user_id"]==user_id] if not df.empty else pd.DataFrame()

def behavior_patterns(df):
    if df.empty: return {}
    prefs={}
    for food, g in df.groupby("food"):
        prefs[food]=len(g[g["decision"]=="accepted"])/len(g)
    return prefs

# =========================================================
# SCORING ENGINE
# =========================================================
def food_score(food,user,prefs):
    base=50
    nutrients=get_demo_nutrition(food)
    supply=get_supply_chain(food)

    if user["goal"] in FOOD_LIBRARY[food]["good_for"]:
        base+=20

    base+=nutrients["protein"]*0.8
    base+=nutrients["fiber"]*1.5

    if user["goal"]=="fat_loss":
        base-=nutrients["calories"]*0.05

    if food in prefs:
        base+=(prefs[food]-0.5)*40

    sc=supply_score(supply)
    base+=(sc-50)*0.5

    return round(base,1), nutrients, supply, sc

def generate_recommendations(user,user_id):
    prefs=behavior_patterns(get_user_history(user_id))
    rows=[]
    for food in FOODS:
        score,n,s,sc=food_score(food,user,prefs)
        rows.append({
            "food":food,"score":score,
            "protein":n["protein"],"fiber":n["fiber"],
            "freshness":s["freshness"],
            "risk":s["risk"],
            "stores":", ".join(s["stores"]),
            "supply_score":sc
        })
    return pd.DataFrame(rows).sort_values("score",ascending=False)

# =========================================================
# CREATE USER
# =========================================================
def create_user(w,h,goal):
    uid=len(st.session_state["users"])+1
    wearable=generate_wearable_data(uid)
    m=aggregate_metrics(wearable)

    user={
        "id":uid,"weight":w,"height":h,
        "bmi":calculate_bmi(w,h),
        "sleep":m["sleep"],
        "steps":m["steps"],
        "recovery":m["recovery"],
        "goal":goal
    }

    st.session_state["users"].append(user)

# =========================================================
# UI
# =========================================================
st.title("🥗 Food Intelligence System")

page=st.sidebar.radio("Navigation",["Create User","View Health","Recommendations"])

if page=="Create User":
    w=st.number_input("Weight",40.0,150.0,75.0)
    h=st.number_input("Height",1.4,2.2,1.75)
    goal=st.selectbox("Goal",["fitness","fat_loss","glucose_control"])

    if st.button("Create"):
        create_user(w,h,goal)
        st.success("User created")

elif page=="View Health":
    users=pd.DataFrame(st.session_state["users"])
    if users.empty: st.stop()

    uid=st.selectbox("User",users["id"])
    user=safe_get_user(users,uid)

    c1,c2,c3=st.columns(3)
    c1.metric("BMI",user["bmi"])
    c2.metric("Sleep",round(user["sleep"],2))
    c3.metric("Steps",user["steps"])

    st.write("Risk:",metabolic_score(user))

elif page=="Recommendations":
    users=pd.DataFrame(st.session_state["users"])
    if users.empty: st.stop()

    uid=st.selectbox("User",users["id"])
    user=safe_get_user(users,uid)

    recs=generate_recommendations(user,uid)

    for _,row in recs.iterrows():
        food=row["food"]
        with st.container(border=True):
            c1,c2=st.columns([1,2])

            with c1:
                st.image(FOOD_IMAGES[food])

            with c2:
                st.subheader(food)
                st.write("Score:",row["score"])
                st.write("Protein:",row["protein"])
                st.write("Fiber:",row["fiber"])
                st.write("Freshness:",row["freshness"])
                st.write("Supply Risk:",row["risk"])
                st.write("Supply Score:",row["supply_score"])
                st.write("Stores:",row["stores"])

                b1,b2=st.columns(2)

                if b1.button(f"👍 {food}",key=f"a{uid}{food}"):
                    log_decision(uid,food,"accepted")
                    st.rerun()

                if b2.button(f"👎 {food}",key=f"r{uid}{food}"):
                    log_decision(uid,food,"rejected")
                    st.rerun()
