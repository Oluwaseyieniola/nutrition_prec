import streamlit as st
import pandas as pd
import numpy as np
import datetime
import hashlib

st.set_page_config(page_title="Precision Nutrition Intelligence System", layout="centered")

# =========================================================
# UTILITIES
# =========================================================
def roundf(x, d=1):
    return round(float(x), d)

# =========================================================
# WEARABLE SIMULATION
# =========================================================
def gen_wearable(days=7, seed=42):
    np.random.seed(seed)
    base = datetime.date.today()

    rows = []
    for i in range(days):
        rows.append({
            "date": base - datetime.timedelta(days=i),
            "steps": np.random.randint(3000, 13000),
            "strain": roundf(np.random.uniform(5, 18)),
            "HRV": np.random.randint(30, 95),
            "sleep_eff": roundf(np.random.uniform(60, 98)),
            "resting_hr": np.random.randint(55, 85)
        })

    return pd.DataFrame(rows)

# =========================================================
# LIFESTYLE INFERENCE
# =========================================================
def infer_lifestyle_from_wearable(df):
    avg_hrv = df["HRV"].mean()
    avg_strain = df["strain"].mean()
    avg_sleep = df["sleep_eff"].mean()
    avg_steps = df["steps"].mean()

    sleep_quality = "good" if avg_sleep >= 85 else "average" if avg_sleep >= 70 else "poor"

    stress_score = (100 - avg_hrv) * 0.6 + avg_strain * 2
    stress_level = "low" if stress_score < 40 else "medium" if stress_score < 70 else "high"

    activity_level = "high" if avg_steps >= 9000 else "moderate" if avg_steps >= 5000 else "low"

    training_load = "high" if avg_strain >= 14 else "moderate" if avg_strain >= 8 else "low"

    return {
        "sleep_quality": sleep_quality,
        "stress_level": stress_level,
        "activity_level": activity_level,
        "training_load": training_load,
        "avg_hrv": avg_hrv,
        "avg_strain": avg_strain,
        "avg_sleep": avg_sleep,
        "avg_steps": avg_steps
    }

# =========================================================
# FOOD CATALOG
# =========================================================
FOOD_CATALOG = [
    "Salmon","Oats","Blueberries","Lentils","Spinach",
    "Chicken Breast","Eggs","Brown Rice","Quinoa",
    "Broccoli","Avocado","Greek Yogurt","Almonds",
    "Walnuts","Sweet Potato","Tomatoes","Garlic",
    "Ginger","Olive Oil","Bananas","Apples"
]

# =========================================================
# SUPPLY CHAIN BULK ENGINE
# =========================================================
def simulate_supply_detailed_bulk(food_list):
    all_data = []

    for food in food_list:
        seed = int(hashlib.md5(food.encode()).hexdigest(), 16) % 10**6
        np.random.seed(seed)

        stages = [
            "Farm Cultivation",
            "Harvest",
            "Post-Harvest Handling",
            "Cold Storage",
            "Transportation",
            "Retail Shelf"
        ]

        nutrients = {
            "Vitamin C": np.random.uniform(40, 100),
            "Protein": np.random.uniform(5, 30),
            "Polyphenols": np.random.uniform(50, 120)
        }

        state = nutrients.copy()

        for stage in stages:
            temp = np.random.uniform(2, 35)
            humidity = np.random.uniform(40, 95)
            days = np.random.uniform(0.5, 5)

            decay = np.exp(-0.05 * days * (temp / 25))

            for k in state:
                state[k] *= decay

            all_data.append({
                "Food": food,
                "Stage": stage,
                "Temperature": round(temp, 1),
                "Humidity": round(humidity, 1),
                "Vitamin C": round(state["Vitamin C"], 1),
                "Protein": round(state["Protein"], 1),
                "Polyphenols": round(state["Polyphenols"], 1)
            })

    return pd.DataFrame(all_data)

# =========================================================
# DUBAI RETAIL INTELLIGENCE
# =========================================================
def dubai_store_intelligence_bulk(food_list):
    stores = [
        "Carrefour UAE",
        "Spinneys Dubai",
        "Waitrose Dubai",
        "Union Coop",
        "Al Maya Supermarket",
        "Organic Foods & Cafe"
    ]

    rows = []

    for food in food_list:
        for store in stores:
            rows.append({
                "Food": food,
                "Store": store,
                "Availability": np.random.choice(["High","Medium","Low"], p=[0.6,0.3,0.1]),
                "Quality": np.random.choice(["Premium","Standard","Organic"], p=[0.4,0.4,0.2])
            })

    return pd.DataFrame(rows)

# =========================================================
# SUPPLY CHAIN STORY ENGINE
# =========================================================
def build_story(food, df):
    return "\n".join(
        [f"{food} originates from controlled agriculture."]
        + [f"{r['Stage']} influences nutrient stability." for _, r in df.iterrows()]
        + ["Final nutrition depends on full chain integrity."]
    )

# =========================================================
# HEALTH ENGINE
# =========================================================
def detect_condition(user):
    if user["BMI"] > 28:
        return "prediabetic_risk"
    if user["stress_level"] == "high" and user["sleep_quality"] == "poor":
        return "inflammation"
    return "general_fitness"

# =========================================================
# VISUAL LIFESTYLE DASHBOARD (FIXED)
# =========================================================
def render_lifestyle_dashboard(lifestyle):

    st.subheader("🧠 Lifestyle Intelligence Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Sleep", lifestyle["sleep_quality"].upper(), f"{round(lifestyle['avg_sleep'],1)}%")
    col2.metric("Stress", lifestyle["stress_level"].upper(), f"HRV {round(lifestyle['avg_hrv'],1)}")
    col3.metric("Activity", lifestyle["activity_level"].upper(), f"{round(lifestyle['avg_steps'],0)} steps")
    col4.metric("Load", lifestyle["training_load"].upper(), f"{round(lifestyle['avg_strain'],1)}")

    st.subheader("📊 Physiological Signature")

    df = pd.DataFrame({
        "Metric": ["HRV","Sleep","Steps","Strain"],
        "Value": [
            lifestyle["avg_hrv"],
            lifestyle["avg_sleep"],
            lifestyle["avg_steps"]/100,
            lifestyle["avg_strain"]*5
        ]
    })

    st.bar_chart(df.set_index("Metric"))

    st.subheader("🧬 Interpretation")

    if lifestyle["stress_level"] == "high":
        st.error("High stress load detected → recovery nutrition required.")
    elif lifestyle["stress_level"] == "medium":
        st.warning("Moderate stress load → balance recovery and performance.")
    else:
        st.success("Stable stress profile.")

    if lifestyle["sleep_quality"] == "poor":
        st.warning("Sleep deficit impacting metabolic recovery.")
    elif lifestyle["sleep_quality"] == "good":
        st.success("Sleep supports recovery and hormone balance.")

# =========================================================
# UI
# =========================================================
st.title("🥗 Precision Nutrition Intelligence System")

page = st.sidebar.radio("Navigation", ["1️⃣ Profile","2️⃣ Supply Chain","3️⃣ Meals"])

# =========================================================
# PAGE 1
# =========================================================
if page.startswith("1️⃣"):
    st.header("User Profile")

    with st.form("profile"):
        age = st.number_input("Age",18,80,30)
        sex = st.selectbox("Sex",["Male","Female"])
        height = st.number_input("Height (cm)",120,220,170)
        weight = st.number_input("Weight (kg)",40,200,70)
        goal = st.selectbox("Goal",["weight_loss","energy_boost","glucose_control"])
        submit = st.form_submit_button("Generate")

    if submit:
        w = gen_wearable()
        lifestyle = infer_lifestyle_from_wearable(w)

        BMI = weight / ((height/100)**2)

        user = {
            "age": age,
            "sex": sex,
            "height": height,
            "weight": weight,
            "BMI": BMI,
            "goal": goal,
            **lifestyle
        }

        st.session_state["user"] = user

        st.subheader("Wearable Data")
        st.dataframe(w)

        # ✅ FIXED: VISUAL DASHBOARD (NO JSON)
        render_lifestyle_dashboard(lifestyle)

# =========================================================
# PAGE 2
# =========================================================
elif page.startswith("2️⃣"):
    st.header("🔬 Multi-Food Supply Chain Intelligence")

    foods = st.multiselect(
        "Select Foods",
        FOOD_CATALOG,
        default=["Salmon","Oats","Blueberries"]
    )

    df = simulate_supply_detailed_bulk(foods)

    st.subheader("Supply Chain Data")
    st.dataframe(df)

    st.subheader("Nutrient Trends")

    for n in ["Vitamin C","Protein","Polyphenols"]:
        st.line_chart(df.pivot_table(index="Stage", columns="Food", values=n))

    st.subheader("Dubai Retail Intelligence")
    st.dataframe(dubai_store_intelligence_bulk(foods))

# =========================================================
# PAGE 3
# =========================================================
elif page.startswith("3️⃣"):
    user = st.session_state.get("user")

    if not user:
        st.warning("Complete profile first")
        st.stop()

    condition = detect_condition(user)

    st.header("🧠 Nutrition System Output")

    if condition == "prediabetic_risk":
        st.warning("Metabolic risk detected → glycemic control diet required.")
    elif condition == "inflammation":
        st.error("Inflammatory profile detected → recovery nutrition required.")
    else:
        st.success("Stable metabolic profile.")

    st.subheader("System Ready")
    st.write("Nutrition + physiology + supply chain intelligence active.")
