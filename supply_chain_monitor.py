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

# =====================================================================
# WEARABLE SIMULATION
# =====================================================================
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
# 🔬 SUPPLY CHAIN MODEL
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
    "Vitamin C": ("Collagen synthesis", "Reduces inflammation & supports tissue repair"),
    "Protein": ("Muscle protein synthesis", "Builds and repairs muscle tissue"),
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
# 🧾 SUPPLY CHAIN NARRATIVE ENGINE
# =====================================================================
def build_supply_chain_story(food, df):
    story = []

    story.append(f"🌱 {food} begins its lifecycle in agricultural environments where soil quality, climate, and farming practices define its baseline nutrient density.")

    for _, row in df.iterrows():
        stage = row["Stage"]

        if stage == "Farm Cultivation":
            story.append(f"Farm stage: environmental conditions shape initial nutrient profile at {row['Temperature (°C)']}°C.")
        elif stage == "Harvest":
            story.append("Harvest stage: mechanical handling introduces oxidative stress and nutrient loss.")
        elif stage == "Post-Harvest Handling":
            story.append(f"Post-harvest: humidity at {row['Humidity (%)']}% influences microbial activity and degradation.")
        elif stage == "Cold Storage":
            story.append("Cold storage slows but does not stop enzymatic nutrient decay.")
        elif stage == "Transportation":
            story.append("Transport introduces thermal fluctuations that accelerate nutrient breakdown.")
        elif stage == "Retail Shelf":
            story.append("Retail shelf exposure determines final nutrient availability at consumption.")

    story.append("🥗 Final nutritional value is the cumulative result of all upstream losses.")

    return "\n\n".join(story)

# =====================================================================
# 🧠 HEALTH IMPACT ENGINE
# =====================================================================
def health_impact_engine(food, df, condition):
    final = df.iloc[-1]

    if condition == "prediabetic_risk":
        return f"""
🧠 Prediabetes Risk Impact:

- Polyphenols: supports insulin sensitivity
- {food}: reduces glucose spikes and metabolic stress
"""

    elif condition == "inflammation":
        return f"""
🧠 Inflammation & Pain Impact:

- Vitamin C supports tissue repair
- Polyphenols reduce inflammatory pathways
- {food} helps reduce muscle soreness and systemic inflammation
"""

    else:
        return f"""
🧠 Performance Impact:

- Protein supports muscle synthesis
- Balanced micronutrients improve recovery
- {food} enhances metabolic efficiency
"""

# =====================================================================
# 🏪 DUBAI STORE INTELLIGENCE
# =====================================================================
def dubai_store_intelligence(food):
    stores = [
        {"Store": "Carrefour UAE", "Type": "Hypermarket", "Quality": "Medium", "Best For": "Affordable groceries"},
        {"Store": "Spinneys Dubai", "Type": "Premium supermarket", "Quality": "High", "Best For": "Fresh produce & organic foods"},
        {"Store": "Waitrose Dubai", "Type": "Imported premium", "Quality": "Very High", "Best For": "Specialty foods & imports"}
    ]

    return pd.DataFrame(stores)

# =====================================================================
# UI
# =====================================================================
st.title("🥗 Precision Nutrition + Supply Chain Intelligence")

page = st.sidebar.radio(
    "Navigation",
    ["1️⃣ Profile & Wearables","2️⃣ Supply Chain Deep Dive","3️⃣ Smart Recommendations"]
)

# ---------------------------------------------------------------------
# PAGE 1
# ---------------------------------------------------------------------
if page.startswith("1️⃣"):
    st.header("User Profile")

    with st.form("profile"):
        age = st.number_input("Age",18,80,35)
        sex = st.selectbox("Sex",["F","M"])
        BMI = st.number_input("BMI",15.0,40.0,25.0)
        goal = st.selectbox("Goal",["weight_loss","energy_boost","glucose_control"])
        sleep = st.number_input("Sleep Hours",4.0,9.0,7.0)
        submit = st.form_submit_button("Generate")

    if submit:
        w = gen_wearable()

        st.session_state["user"] = {
            "age": age,
            "sex": sex,
            "BMI": BMI,
            "goal": goal,
            "sleep": sleep,
            "strain": float(w.strain.mean())
        }

        st.dataframe(w)
        st.line_chart(w.set_index("date")[["steps","HRV","sleep_eff"]])

# ---------------------------------------------------------------------
# PAGE 2 (UPGRADED)
# ---------------------------------------------------------------------
elif page.startswith("2️⃣"):
    st.header("🔬 Farm → Plate Intelligence System")

    food = st.selectbox("Select Food", ["Salmon","Oats","Blueberries","Lentils","Spinach"])

    df = simulate_supply_detailed(food)

    st.subheader("📦 Supply Chain Data")
    st.dataframe(df)

    st.subheader("📉 Nutrient Degradation")
    st.line_chart(df.set_index("Stage")[["Vitamin C","Protein","Polyphenols"]])

    st.subheader("🧾 Food Journey Narrative")
    story = build_supply_chain_story(food, df)
    st.write(story)

    user = st.session_state.get("user", {})
    condition = detect_condition(user) if user else "general_fitness"

    st.subheader("🧠 Health Impact")
    st.write(health_impact_engine(food, df, condition))

    st.subheader("🏪 Dubai Store Availability")
    st.dataframe(dubai_store_intelligence(food))

# ---------------------------------------------------------------------
# PAGE 3
# ---------------------------------------------------------------------
elif page.startswith("3️⃣"):
    user = st.session_state.get("user")

    if not user:
        st.warning("Complete profile first")
        st.stop()

    condition = detect_condition(user)
    protocol = condition_protocols[condition]

    st.header("🧠 Personalized Nutrition")

    st.write(f"Condition: {condition}")
    st.write(f"Focus: {protocol['focus']}")

    for food in protocol["foods"]:
        st.markdown(f"### {food}")

        st.write(
            f"{food} is recommended based on your biological state and supports metabolic regulation."
        )

    st.success("System is now adapting nutrition to your physiology + food supply chain quality.")
