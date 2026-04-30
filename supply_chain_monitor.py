import streamlit as st
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="Food Intelligence System", layout="wide")

# =========================================================
# INIT STATE
# =========================================================
def init():
    for k in ["users","history","habits"]:
        if k not in st.session_state:
            st.session_state[k]=[]
init()

# =========================================================
# DOMAIN
# =========================================================
FOODS=["Salmon","Oats","Eggs","Spinach","Chicken Breast","Avocado","Blueberries"]

FOOD_LIBRARY={
    "Salmon":{"goal":["fitness","glucose_control"],"desc":"Omega-3 recovery"},
    "Oats":{"goal":["glucose_control"],"desc":"Stable energy carbs"},
    "Eggs":{"goal":["fitness"],"desc":"Complete protein"},
    "Spinach":{"goal":["glucose_control"],"desc":"Micronutrient dense"},
    "Chicken Breast":{"goal":["fitness","fat_loss"],"desc":"Lean protein"},
    "Avocado":{"goal":["fat_loss"],"desc":"Healthy fats"},
    "Blueberries":{"goal":["glucose_control"],"desc":"Antioxidants"}
}

NUTRITION={
    "Salmon":{"protein":25,"fiber":0,"cal":208},
    "Oats":{"protein":17,"fiber":10,"cal":389},
    "Eggs":{"protein":12,"fiber":0,"cal":155},
    "Spinach":{"protein":3,"fiber":2,"cal":23},
    "Chicken Breast":{"protein":31,"fiber":0,"cal":165},
    "Avocado":{"protein":2,"fiber":7,"cal":160},
    "Blueberries":{"protein":1,"fiber":2,"cal":57}
}

SUPPLY={
    "Salmon":{"fresh":0.8,"risk":0.3,"proc":0.2,"stores":["Carrefour","Spinneys"]},
    "Oats":{"fresh":0.95,"risk":0.1,"proc":0.4,"stores":["Lulu","Union Coop"]},
    "Eggs":{"fresh":0.9,"risk":0.2,"proc":0.1,"stores":["Carrefour"]},
    "Spinach":{"fresh":0.85,"risk":0.25,"proc":0.1,"stores":["Organic Store"]},
    "Chicken Breast":{"fresh":0.88,"risk":0.35,"proc":0.3,"stores":["Carrefour"]},
    "Avocado":{"fresh":0.75,"risk":0.4,"proc":0.05,"stores":["Spinneys"]},
    "Blueberries":{"fresh":0.7,"risk":0.45,"proc":0.05,"stores":["Waitrose"]}
}

# =========================================================
# USER
# =========================================================
def create_user(w,h,goal):
    uid=len(st.session_state.users)+1
    st.session_state.users.append({
        "id":uid,"w":w,"h":h,
        "bmi":round(w/(h**2),1),
        "goal":goal
    })

# =========================================================
# WEARABLE (WHOOP STYLE)
# =========================================================
def wearable(uid):
    rng=np.random.default_rng(uid)
    return {
        "sleep":round(rng.uniform(5,8),2),
        "strain":round(rng.uniform(5,18),1),
        "recovery":int(rng.uniform(30,95))
    }

# =========================================================
# HEALTH ENGINE
# =========================================================
def health_score(user,wear):
    score=0
    reasons=[]

    if user["bmi"]>27:
        score+=2
        reasons.append("High BMI")

    if wear["sleep"]<6:
        score+=2
        reasons.append("Low sleep")

    if wear["recovery"]<50:
        score+=2
        reasons.append("Low recovery")

    risk="LOW"
    if score>=4: risk="HIGH"
    elif score>=2: risk="MODERATE"

    return risk,reasons

# =========================================================
# BEHAVIOR ENGINE
# =========================================================
def prefs(uid):
    df=pd.DataFrame(st.session_state.history)
    if df.empty: return {}

    df=df[df.user==uid]
    if df.empty: return {}

    p={}
    for f,g in df.groupby("food"):
        p[f]=len(g[g.decision=="yes"])/len(g)
    return p

# =========================================================
# HABITS
# =========================================================
def log_habit(uid,food):
    st.session_state.habits.append({
        "user":uid,"food":food,"date":datetime.date.today()
    })

def habit_score(uid):
    df=pd.DataFrame(st.session_state.habits)
    if df.empty: return 0
    return len(df[df.user==uid])

# =========================================================
# SUPPLY SCORE
# =========================================================
def supply_score(s):
    return (s["fresh"]*40)+((1-s["risk"])*30)+((1-s["proc"])*30)

# =========================================================
# FOOD CHAIN SIMULATION (NEW)
# =========================================================
def simulate_food_chain(food):
    base = SUPPLY.get(food, {})

    stages = [
        {"stage":"Farm","time":"Day 0","temp":5,"event":"Harvest","quality":100},
        {"stage":"Processing","time":"Day 1","temp":8,"event":"Packaging","quality":95-base.get("proc",0)*20},
        {"stage":"Transport","time":"Day 2-4","temp":np.random.choice([4,10,15]),
         "event":np.random.choice(["Smooth","Delay","Temp fluctuation"]), "quality":85},
        {"stage":"Retail","time":"Day 5-7","temp":np.random.choice([4,12]),
         "event":np.random.choice(["Optimal","Overstock","Cold chain break"]), "quality":75},
        {"stage":"Consumer","time":"Day 8","temp":22,"event":"Consumption","quality":70}
    ]

    quality=100
    timeline=[]

    for s in stages:
        penalty=0
        if s["temp"]>10: penalty+=5
        if "Delay" in s["event"]: penalty+=5
        if "Cold" in s["event"]: penalty+=10

        quality-=penalty
        s["final"]=max(quality,0)
        timeline.append(s)

    return timeline,quality

# =========================================================
# RECOMMENDER
# =========================================================
def score(food,user,p,wear):
    base=50
    n=NUTRITION[food]
    s=SUPPLY[food]

    if user["goal"] in FOOD_LIBRARY[food]["goal"]:
        base+=20

    base+=n["protein"]*0.8
    base+=n["fiber"]*1.5

    if user["goal"]=="fat_loss":
        base-=n["cal"]*0.05

    if food in p:
        base+=(p[food]-0.5)*40

    base+=(supply_score(s)-50)*0.5

    if wear["recovery"]<50:
        base+=5

    return round(base,1)

def recommend(user,uid):
    p=prefs(uid)
    wear=wearable(uid)

    rows=[]
    for f in FOODS:
        rows.append({
            "food":f,
            "score":score(f,user,p,wear),
            "stores":", ".join(SUPPLY[f]["stores"])
        })

    return pd.DataFrame(rows).sort_values("score",ascending=False),wear

# =========================================================
# UI
# =========================================================
st.title("🧠 Food Intelligence System")

page=st.sidebar.radio("Pages",[
    "Create User",
    "Health Insights",
    "Recommendations",
    "Habit Tracker",
    "Food Chain Monitoring"
])

# ---------------- CREATE USER ----------------
if page=="Create User":
    w=st.number_input("Weight",50.0,150.0,75.0)
    h=st.number_input("Height",1.4,2.2,1.75)
    goal=st.selectbox("Goal",["fitness","fat_loss","glucose_control"])

    if st.button("Create"):
        create_user(w,h,goal)
        st.success("User created")

# ---------------- HEALTH ----------------
elif page=="Health Insights":
    users=pd.DataFrame(st.session_state.users)
    if users.empty: st.stop()

    uid=st.selectbox("User",users.id)
    user=users[users.id==uid].iloc[0].to_dict()

    wear=wearable(uid)
    risk,reasons=health_score(user,wear)

    st.metric("BMI",user["bmi"])
    st.metric("Recovery",wear["recovery"])
    st.metric("Sleep",wear["sleep"])

    st.write("Risk:",risk)
    st.write("Reasons:",reasons)

# ---------------- RECOMMEND ----------------
elif page=="Recommendations":
    users=pd.DataFrame(st.session_state.users)
    if users.empty: st.stop()

    uid=st.selectbox("User",users.id)
    user=users[users.id==uid].iloc[0].to_dict()

    recs,wear=recommend(user,uid)

    st.subheader("WHOOP Recovery")
    st.write(wear)

    for _,r in recs.iterrows():
        with st.container(border=True):
            st.subheader(r.food)
            st.write("Score:",r.score)
            st.write("Stores:",r.stores)

            c1,c2=st.columns(2)

            if c1.button(f"Accept {r.food}",key=f"a{uid}{r.food}"):
                st.session_state.history.append({"user":uid,"food":r.food,"decision":"yes"})
                log_habit(uid,r.food)
                st.rerun()

            if c2.button(f"Reject {r.food}",key=f"r{uid}{r.food}"):
                st.session_state.history.append({"user":uid,"food":r.food,"decision":"no"})
                st.rerun()

# ---------------- HABITS ----------------
elif page=="Habit Tracker":
    users=pd.DataFrame(st.session_state.users)
    if users.empty: st.stop()

    uid=st.selectbox("User",users.id)
    st.metric("Healthy Actions",habit_score(uid))

# ---------------- FOOD CHAIN ----------------
elif page=="Food Chain Monitoring":
    st.subheader("🚜 Farm → Fork Monitoring")

    food=st.selectbox("Food",FOODS)
    timeline,final=simulate_food_chain(food)

    for step in timeline:
        with st.container(border=True):
            st.write(step["stage"],"|",step["time"])
            st.write("Temp:",step["temp"],"Event:",step["event"])
            st.progress(step["final"]/100)
            st.write("Quality:",step["final"])

    st.metric("Final Quality",final)
