import streamlit as st
import pandas as pd
import numpy as np
import datetime

# ---------------------------------------------------------------------
# GENERIC FUNCTIONS
# ---------------------------------------------------------------------
def generate_synthetic_wearable_data(days=7):
    base_date = datetime.date.today()
    data = []
    np.random.seed(42)
    for i in range(days):
        data.append({
            "date": base_date - datetime.timedelta(days=i),
            "steps": np.random.randint(3000, 13000),
            "strain": np.random.uniform(5, 18).round(1),
            "HRV": np.random.randint(30, 100),
            "sleep_eff": np.random.uniform(70, 98).round(1),
            "protein": np.random.randint(50, 160),
            "meal_timing": np.random.uniform(0.6, 1.0).round(2),
        })
    return pd.DataFrame(data)

def simulate_supply_chain(food):
    np.random.seed(abs(hash(food)) % 10**6)
    stages = ["Farm","Processing","Storage","Transport","Retail","Home"]
    df = pd.DataFrame({
        "stage": stages,
        "temperature": np.random.uniform(0,25,len(stages)).round(1),
        "duration_days": np.random.uniform(0.5,6,len(stages)).round(1),
        "handling": np.random.uniform(5,10,len(stages)).round(1),
        "nutrient_loss": np.random.uniform(0,8,len(stages)).round(1)
    })
    df["validity"] = df.apply(lambda r: max(0,1 - r.nutrient_loss/100 + (r.handling/10)*0.05), axis=1)
    return df

def compute_food_validity(food):
    df = simulate_supply_chain(food)
    return round(df["validity"].mean()*100,1)

# ---------------------------------------------------------------------
# NAVIGATION
# ---------------------------------------------------------------------
page = st.sidebar.radio(
    "Navigation",
    ["🩺 Precision Nutrition", "🌾 Supply Chain Monitor", "🔗 Food Recommender"]
)

# ---------------------------------------------------------------------
# PAGE 1 — Precision Nutrition (Wearables + Profile)
# ---------------------------------------------------------------------
if page.startswith("🩺"):

    st.title("🩺 Precision Nutrition + Wearable Metrics")
    with st.form("profile"):
        age = st.number_input("Age",18,80,35)
        sex = st.selectbox("Sex",["F","M"])
        BMI = st.number_input("Body Mass Index (BMI)",15.,40.,25.)
        activity = st.selectbox("Activity Level",["low","moderate","high"])
        sleep = st.number_input("Average Sleep Hours",4.,9.5,7.)
        stress = st.selectbox("Stress Level",["low","medium","high"])
        glucose = st.slider("Fasting Glucose (mg/dL)",70,130,95)
        diversity = st.slider("Gut Microbiome Diversity Index",2.,5.,3.2)
        goal = st.selectbox("Main Goal",["weight_loss","energy_boost","glucose_control"])
        consent = st.checkbox("Consent to synthetic data use",True)
        submit = st.form_submit_button("Generate Insights")

    if submit and consent:
        wearable_df = generate_synthetic_wearable_data()
        st.session_state["user_summary"] = {
            "age":age,"BMI":BMI,"goal":goal,"activity":activity,
            "sleep":sleep,"stress":stress,"glucose":glucose,
            "diversity":diversity,"HRV":int(wearable_df.HRV.mean()),
            "strain":float(wearable_df.strain.mean()),"region":"UAE"
        }

        st.subheader("Synthetic Wearable Summary")
        st.dataframe(wearable_df)
        st.bar_chart(wearable_df[["steps","strain","sleep_eff"]].set_index("date"))

        st.success("Profile stored → open next pages from sidebar.")

# ---------------------------------------------------------------------
# PAGE 2 — Supply Chain Monitor
# ---------------------------------------------------------------------
elif page.startswith("🌾"):

    st.title("🌾 Food Supply‑Chain Monitor & Nutrient Integrity")
    foods = ["Broccoli","Chicken breast","Oats","Blueberries","Tomatoes","Eggs"]
    food_selected = st.selectbox("Select Food Item",foods)

    df = simulate_supply_chain(food_selected)
    total_val = round(df.validity.mean()*100,1)
    st.dataframe(df)
    st.bar_chart(df.set_index("stage")[["nutrient_loss","validity"]])
    st.metric("Estimated Nutrient Integrity %",100 - df.nutrient_loss.sum())
    st.metric("Overall Validity Index",total_val)

    st.session_state.setdefault("food_validity",{})[food_selected] = total_val
    st.success("Supply‑chain data saved → open final page for recommendations.")

# ---------------------------------------------------------------------
# PAGE 3 — Food Recommender (Link Both Systems)
# ---------------------------------------------------------------------
elif page.startswith("🔗"):

    st.title("🔗 Integrated Food Recommendation Engine")

    user = st.session_state.get("user_summary")
    validity_map = st.session_state.get("food_validity",{})

    if not user:
        st.warning("Please run the Precision Nutrition page first to create a user profile.")
        st.stop()

    # --------------------------- Dummy food data -----------------------
    np.random.seed(99)
    foods = ["Broccoli","Chicken breast","Oats","Blueberries","Tomatoes","Eggs","Lentils"]
    food_df = pd.DataFrame({
        "food":foods,
        "protein":np.random.randint(3,30,len(foods)),
        "fiber":np.random.uniform(1,10,len(foods)).round(1),
        "glycemic_index":np.random.randint(30,80,len(foods)),
        "antioxidants":np.random.randint(40,100,len(foods)),
        "validity": [validity_map.get(f,np.random.randint(70,95)) for f in foods]
    })

    # --------------------------- Scoring logic -------------------------
    def food_score(row,u):
        score = row.validity
        g = u["goal"]
        if g == "weight_loss":
            score += 0.3*(30-row.glycemic_index)+0.2*row.fiber
        elif g == "energy_boost":
            score += 0.3*row.protein+0.1*row.glycemic_index
        elif g == "glucose_control":
            score += 0.4*(50-row.glycemic_index)+0.2*row.fiber
        return round(score,2)

    food_df["relevance"] = food_df.apply(lambda r: food_score(r,user),axis=1)
    ordered = food_df.sort_values("relevance",ascending=False).reset_index(drop=True)

    st.subheader(f"Recommended Foods for Goal → **{user['goal'].replace('_',' ').title()}**")
    st.dataframe(ordered)

    best = ordered.iloc[0].food
    st.success(f"Top match: **{best}**, retaining {ordered.iloc[0].validity}% nutrient integrity.")

    # --------------------------- Mock store suggestions ----------------
    stores = pd.DataFrame({
        "food":np.repeat(foods,2),
        "store":np.tile(["Carrefour Dubai Marina","Lulu Hypermarket Abu Dhabi"],len(foods)),
        "quality":np.random.choice(["High Integrity","Standard"],len(foods)*2,p=[0.7,0.3]),
        "price_AED":np.random.randint(4,25,len(foods)*2)
    })
    st.subheader("🇦🇪 Stores Carrying High‑Integrity Foods")
    best3 = ordered.food.head(3)
    st.dataframe(stores[stores.food.isin(best3)])

    # --------------------------- Explanation --------------------------
    explain = {
        "weight_loss":"Selected foods combine low glycemic index, high fiber and verified integrity to sustain fat loss.",
        "energy_boost":"Protein‑dense and high‑validity foods maximize recovery and daily energy.",
        "glucose_control":"Low‑GI foods with verified supply‑chain integrity help stabilize blood glucose."
    }
    st.markdown("**Why these foods:** "+explain.get(user["goal"],""))
    st.caption("Synthetic prototype — for educational demonstration only.")
