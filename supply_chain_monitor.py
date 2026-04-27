import streamlit as st
import pandas as pd
import numpy as np
import datetime
import hashlib
import os

st.set_page_config(page_title="Precision Nutrition Engine", layout="wide")

# ---------------------------------------------------------------
# CSS for nicer visuals
# ---------------------------------------------------------------
st.markdown("""
<style>
img {border-radius: 14px;}
.card {
    padding: 1rem;
    border-radius: 10px;
    border: 1px solid #e1e1e1;
    margin-bottom: 1rem;
}
.card-title {
    font-size: 1.2rem;
    font-weight: 600;
}
.timelist {
    text-align: center;
    padding: 0.4rem;
}
.metric-small {font-size: 0.95rem !important;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# FOOD IMAGES
# ---------------------------------------------------------------
FOOD_IMAGES = {
    "Salmon": "[images.unsplash.com](https://images.unsplash.com/photo-1599084993091-1cb5c0721cc6)",
    "Oats": "[images.unsplash.com](https://images.unsplash.com/photo-1517673400267-0251440c45dc)",
    "Blueberries": "[images.unsplash.com](https://images.unsplash.com/photo-1498557850523-fd3d118b962e)",
    "Lentils": "[images.unsplash.com](https://images.unsplash.com/photo-1603048297172-c92544798d5a)",
    "Spinach": "[images.unsplash.com](https://images.unsplash.com/photo-1576045057995-568f588f82fb)",
    "Chicken Breast": "[images.unsplash.com](https://images.unsplash.com/photo-1604503468506-a8da13d82791)",
    "Avocado": "[images.unsplash.com](https://images.unsplash.com/photo-1523049673857-eb18f1d7b578)",
    "Eggs": "[images.unsplash.com](https://images.unsplash.com/photo-1506976785307-8732e854ad03)",
    "Broccoli": "[images.unsplash.com](https://images.unsplash.com/photo-1459411621453-7b03977f4bfc)",
    "Tomatoes": "[images.unsplash.com](https://images.unsplash.com/photo-1546094096-0df4bcaaa337)",
    "Walnuts": "[images.unsplash.com](https://images.unsplash.com/photo-1508747703725-719777637510)",
    "Oranges": "[images.unsplash.com](https://images.unsplash.com/photo-1547514701-42782101795e)",
    "Bananas": "[images.unsplash.com](https://images.unsplash.com/photo-1574226516831-e1dff420e37f)",
    "Pomegranate": "[images.unsplash.com](https://images.unsplash.com/photo-1541344999733-83eca272f6fc)",
}

# ---------------------------------------------------------------
# FOOD LIBRARY (truncated for conciseness, can expand anytime)
# ---------------------------------------------------------------
FOOD_LIBRARY = {
    "Salmon": {
        "category": "fatty_fish",
        "key_nutrients": ["Omega‑3 EPA/DHA", "Protein", "Vitamin D"],
        "good_for": ["pain","fitness","glucose_control"],
        "body_effect": "Anti-inflammatory, supports muscle recovery & cardiometabolic health."
    },
    "Oats": {
        "category": "whole_grain",
        "key_nutrients": ["Beta-glucan fiber","Magnesium"],
        "good_for": ["glucose_control","fat_loss"],
        "body_effect": "Slows digestion, reduces glucose spikes, improves fullness."
    },
    "Blueberries": {
        "category": "berry",
        "key_nutrients": ["Polyphenols","Vitamin C","Fiber"],
        "good_for": ["inflammation","glucose_control"],
        "body_effect": "Antioxidants support vascular health & lower oxidative stress."
    },
    "Chicken Breast": {
        "category": "lean_protein",
        "key_nutrients": ["Protein","B6"],
        "good_for": ["fitness","muscle_support"],
        "body_effect": "Supports muscle repair & lean mass maintenance."
    },
    "Spinach": {
        "category": "leafy_green",
        "key_nutrients": ["Magnesium","Vitamin K","Nitrates"],
        "good_for": ["fitness","glucose_control"],
        "body_effect": "Improves oxygen flow & muscle efficiency."
    }
}

FOODS = list(FOOD_LIBRARY.keys())

# ---------------------------------------------------------------
# Wearable Providers (Sim + WHOOP Demo)
# ---------------------------------------------------------------
class WearableProvider:
    def fetch(self, days=7):
        raise NotImplementedError

class SimProvider(WearableProvider):
    def __init__(self, seed=42): self.seed = seed
    def fetch(self, days=7):
        np.random.seed(self.seed)
        rows = []
        for i in range(days):
            rows.append({
                "date": datetime.date.today() - datetime.timedelta(days=i),
                "hrv": np.random.randint(45,95),
                "sleep": round(np.random.uniform(5.5,8.2),2),
                "strain": round(np.random.uniform(6,17),1),
                "recovery": np.random.randint(40,90),
                "steps": np.random.randint(4000,13000)
            })
        return pd.DataFrame(rows)

class WhoopDemoProvider(WearableProvider):
    def __init__(self, token=None): self.token = token
    def fetch(self, days=7):
        # Demo data (no real WHOOP API calls)
        np.random.seed(202)
        rows=[]
        for i in range(days):
            rows.append({
                "date": datetime.date.today() - datetime.timedelta(days=i),
                "hrv": np.random.randint(50,90),
                "sleep": round(np.random.uniform(5.8,8.4),2),
                "strain": round(np.random.uniform(7,16),1),
                "recovery": np.random.randint(45,90),
                "steps": np.random.randint(5000,11000)
            })
        return pd.DataFrame(rows)

def aggregate(df):
    return {
        "sleep": df["sleep"].mean(),
        "hrv": df["hrv"].mean(),
        "strain": df["strain"].mean(),
        "recovery": df["recovery"].mean(),
        "steps": df["steps"].mean()
    }

# ---------------------------------------------------------------
# Supply Chain Simulation (visual)
# ---------------------------------------------------------------
def supply_chain(food):
    np.random.seed(int(hashlib.md5(food.encode()).hexdigest(),16)%10**6)
    base = {"Vitamin C":np.random.uniform(40,90),
            "Protein":np.random.uniform(5,25),
            "Polyphenols":np.random.uniform(30,80)}
    stages=[]
    timeline=[
        ("Farm","🌱","field growth & sunlight"),
        ("Harvest","🧺","picking & washing"),
        ("Storage","❄️","cold holding"),
        ("Transport","🚚","cold-chain logistics"),
        ("Retail","🏪","shelf display"),
        ("Home","🍽️","consumer storage")
    ]
    for name,icon,desc in timeline:
        temp=np.random.uniform(2,30)
        days=np.random.uniform(0.3,3.5)
        decay=np.exp(-0.05*days*(temp/25))
        for k in base: base[k]*=decay
        stages.append({
            "Stage":name,"Icon":icon,"Description":desc,
            "Temp":round(temp,1),"Days":round(days,1),
            "Vitamin C":round(base["Vitamin C"],1),
            "Protein":round(base["Protein"],1),
            "Polyphenols":round(base["Polyphenols"],1)
        })
    return pd.DataFrame(stages)

# ---------------------------------------------------------------
# Environment Learning Layer
# ---------------------------------------------------------------
class EnvironmentModel:
    def __init__(self):
        self.state={}

    def update(self,user,wearable,supply):
        self.state={
            "temp":np.random.uniform(25,42),
            "humidity":np.random.uniform(40,90),
            "sleep":user["sleep"],
            "strain":user["strain"],
            "steps":user["steps"],
            "supply_quality":supply[["Vitamin C","Protein"]].mean().mean()
        }

    def get(self,key): return self.state.get(key)

env = EnvironmentModel()

def adjust_score(base,food):
    score=base
    if env.get("temp")>38 and food in ["Oranges","Pomegranate","Spinach"]:
        score+=6
    if env.get("humidity")>70 and FOOD_LIBRARY[food]["category"] in ["leafy_green","berry"]:
        score-=4
    if env.get("strain")>15 and "glucose_control" in FOOD_LIBRARY[food]["good_for"]:
        score+=5
    if env.get("sleep")<6:
        if "glucose_control" in FOOD_LIBRARY[food]["good_for"]:
            score+=7
    return score

# ---------------------------------------------------------------
# Store Suggestions
# ---------------------------------------------------------------
def store_options(food):
    rows=[]
    for s in ["Carrefour Dubai Marina","Spinneys Abu Dhabi","Lulu Hypermarket Dubai"]:
        rows.append({
            "Store":s,
            "Quality":np.random.choice(["High","Standard","Variable"],p=[0.5,0.3,0.2]),
            "Stock":np.random.choice(["In Stock","Low Stock"],p=[0.8,0.2]),
            "Price (AED)":np.random.randint(4,20)
        })
    return pd.DataFrame(rows)

# ---------------------------------------------------------------
# User storage
# ---------------------------------------------------------------
if "users" not in st.session_state:
    st.session_state["users"] = {}

def create_user(weight,height,goal,src):
    uid=len(st.session_state["users"])+1
    provider=SimProvider(uid) if src=="Simulated" else WhoopDemoProvider("demo")
    wear=provider.fetch()
    agg=aggregate(wear)
    user={
        "id":uid,"weight":weight,"height":height,
        "bmi":round(weight/(height**2),1),
        "goal":goal,
        "sleep":agg["sleep"],"hrv":agg["
