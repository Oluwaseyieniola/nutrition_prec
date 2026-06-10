import streamlit as st
import pandas as pd
import numpy as np
import datetime
import hashlib

st.set_page_config(page_title="Precision Nutrition Unified MVP", layout="centered")

# =====================================================================
# UTILITIES
# =====================================================================
def roundf(x, d=1): return round(float(x), d)

# ---------- wearable simulation ----------
def gen_wearable(days=7, seed=42):
    np.random.seed(seed)
    base = datetime.date.today()
    rows = []
    for i in range(days):
        rows.append({
            "date": base - datetime.timedelta(days=i),
            "steps": np.random.randint(3500, 12500),
            "strain": roundf(np.random.uniform(5, 18)),
            "HRV": np.random.randint(35, 90),
            "sleep_eff": roundf(np.random.uniform(70, 98)),
            "protein": np.random.randint(55, 160),
            "meal_timing": roundf(np.random.uniform(0.6, 1.0), 2)
        })
    return pd.DataFrame(rows)

# =====================================================================
# 🔬 DETAILED SUPPLY CHAIN MODEL
# =====================================================================
def simulate_supply_detailed(food):
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

    base_nutrients = {
        "Vitamin C": np.random.uniform(40, 100),
        "Protein": np.random.uniform(5, 30),
        "Polyphenols": np.random.uniform(50, 120)
    }

    nutrient_state = base_nutrients.copy()
    data = []

    for stage in stages:
        temp = np.random.uniform(2, 35)
        humidity = np.random.uniform(40, 95)
        days = np.random.uniform(0.5, 5)

        # exponential decay
        decay_factor = np.exp(-0.05 * days * (temp / 25))

        for k in nutrient_state:
            nutrient_state[k] *= decay_factor

        data.append({
            "Stage": stage,
            "Temperature (°C)": round(temp, 1),
            "Humidity (%)": round(humidity, 1),
            "Duration (days)": round(days, 1),
            "Vitamin C": round(nutrient_state["Vitamin C"], 1),
            "Protein": round(nutrient_state["Protein"], 1),
            "Polyphenols": round(nutrient_state["Polyphenols"], 1)
        })

    return pd.DataFrame(data)

# =====================================================================
# 🧠 BIOLOGICAL MAPPING
# =====================================================================
bio_map = {
    "Vitamin C": ("Collagen synthesis", "Reduces pain & inflammation, supports recovery"),
    "Protein": ("Muscle protein synthesis", "Builds muscle and repairs tissue"),
    "Polyphenols": ("Antioxidant + insulin regulation", "Improves insulin sensitivity")
}

# =====================================================================
# 🧬 CONDITION DETECTION
# =====================================================================
def detect_condition(user):
    if user["goal"] == "glucose_control" or user["BMI"] > 28:
        return "prediabetic_risk"
    elif user["strain"] > 14 and user["sleep"] < 6:
        return "inflammation"
    else:
        return "general_fitness"

condition_protocols = {
    "prediabetic_risk": {
        "focus": "Improve insulin sensitivity",
        "foods": ["Blueberries", "Oats", "Lentils"]
    },
    "inflammation": {
        "focus": "Reduce inflammation & pain",
        "foods": ["Salmon", "Spinach", "Blueberries"]
    },
    "general_fitness": {
        "focus": "Optimize performance & recovery",
        "foods": ["Eggs", "Chicken Breast", "Avocado"]
    }
}

# =====================================================================
# NAVIGATION
# =====================================================================
st.title("🥗 Precision Nutrition + Supply Chain Intelligence")
page = st.sidebar.radio("Navigation",
    ["1️⃣ Profile & Wearables","2️⃣ Supply Chain Deep Dive","3️⃣ Smart Recommendations"]
)

# ---------------------------------------------------------------------
# PAGE 1
# ---------------------------------------------------------------------
if page.startswith("1️⃣"):
    st.header("User Profile and Wearable Data")

    with st.form("profile"):
        age = st.number_input("Age",18,80,35)
        sex = st.selectbox("Sex",["F","M"])
        BMI = st.number_input("BMI",15.0,40.0,25.0)
        goal = st.selectbox("Goal",["weight_loss","energy_boost","glucose_control"])
        activity = st.selectbox("Activity Level",["low","moderate","high"])
        stress = st.selectbox("Stress",["low","medium","high"])
        sleep = st.number_input("Sleep Hours",4.0,9.0,7.0)
        submit = st.form_submit_button("Generate")

    if submit:
        w = gen_wearable()
        st.session_state["user"] = {
            "age":age,"sex":sex,"BMI":BMI,"goal":goal,
            "activity":activity,"stress":stress,"sleep":sleep,
            "HRV":int(w.HRV.mean()),"strain":float(w.strain.mean())
        }

        st.dataframe(w)
        st.line_chart(w.set_index("date")[["steps","HRV","sleep_eff"]])

# ---------------------------------------------------------------------
# PAGE 2 – 🔥 DETAILED TRACE
# ---------------------------------------------------------------------
elif page.startswith("2️⃣"):
    st.header("🔬 Full Food Journey: Farm → Plate")

    food = st.selectbox("Select Food", ["Salmon","Oats","Blueberries","Lentils","Spinach"])

    df = simulate_supply_detailed(food)

    st.subheader("📦 Supply Chain Trace Data")
    st.dataframe(df)

    st.subheader("📉 Nutrient Degradation Across Stages")
    st.line_chart(df.set_index("Stage")[["Vitamin C","Protein","Polyphenols"]])

    st.subheader("🌡 Environmental Exposure")
    st.bar_chart(df.set_index("Stage")[["Temperature (°C)","Humidity (%)"]])

    st.subheader("🧠 Biological Meaning")
    for nutrient, (func, impact) in bio_map.items():
        st.markdown(f"**{nutrient}**")
        st.write(f"- Function: {func}")
        st.write(f"- Effect: {impact}")

    st.session_state["last_food_trace"] = df

# ---------------------------------------------------------------------
# PAGE 3 – 🧬 INTELLIGENT RECOMMENDATIONS
# ---------------------------------------------------------------------
elif page.startswith("3️⃣"):
    user = st.session_state.get("user")

    if not user:
        st.warning("Please complete Profile first")
        st.stop()

    condition = detect_condition(user)
    protocol = condition_protocols[condition]

    st.header("🧠 Personalized Health Intelligence")

    st.subheader(f"Detected State: {condition.replace('_',' ').title()}")
    st.write(f"Focus: {protocol['focus']}")

    st.subheader("🍽 Recommended Foods")

    for food in protocol["foods"]:
        st.markdown(f"### {food}")

        if condition == "prediabetic_risk":
            st.write(
                f"{food} helps regulate blood sugar levels by improving insulin response "
                "and reducing glucose spikes."
            )

        elif condition == "inflammation":
            st.write(
                f"{food} reduces inflammation, helping relieve body pain and improve recovery."
            )

        else:
            st.write(
                f"{food} supports overall performance, muscle growth, and metabolic health."
            )

    st.success("Your nutrition is now tailored to your biological state and food quality.")
