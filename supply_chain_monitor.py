import streamlit as st
import pandas as pd
import numpy as np
import datetime
import hashlib

st.set_page_config(page_title="Precision Nutrition Unified MVP", layout="centered")

# =====================================================================
# UTILITIES
# =====================================================================
def roundf(x, d=1): 
    return round(float(x), d)

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
# SUPPLY CHAIN MODEL
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
# BIOLOGICAL MAPPING
# =====================================================================
bio_map = {
    "Vitamin C": ("Collagen synthesis", "Reduces inflammation & supports tissue repair"),
    "Protein": ("Muscle protein synthesis", "Builds and repairs muscle tissue"),
    "Polyphenols": ("Antioxidant + insulin regulation", "Improves insulin sensitivity")
}

# =====================================================================
# CONDITION DETECTION
# =====================================================================
def detect_condition(user):
    if user["goal"] == "glucose_control" or user["BMI"] > 28:
        return "prediabetic_risk"
    elif user["strain"] > 14 and user["sleep"] < 6:
        return "inflammation"
    else:
        return "general_fitness"

# =====================================================================
# SUPPLY CHAIN STORY ENGINE
# =====================================================================
def build_supply_chain_story(food, df):
    story = []

    story.append(f"🌱 {food} begins its lifecycle in controlled agricultural environments.")

    for _, row in df.iterrows():
        stage = row["Stage"]

        if stage == "Farm Cultivation":
            story.append(f"Farm stage: temperature {row['Temperature (°C)']}°C influences nutrient formation.")
        elif stage == "Harvest":
            story.append("Harvest introduces oxidative stress affecting nutrient stability.")
        elif stage == "Post-Harvest Handling":
            story.append("Handling increases exposure to oxygen and microbial activity.")
        elif stage == "Cold Storage":
            story.append("Cold storage slows enzymatic nutrient breakdown.")
        elif stage == "Transportation":
            story.append("Transport introduces temperature variability affecting degradation.")
        elif stage == "Retail Shelf":
            story.append("Shelf time determines final nutrient availability at consumption.")

    story.append("🥗 Final nutritional value is cumulative across all stages.")
    return "\n\n".join(story)

# =====================================================================
# HEALTH IMPACT ENGINE
# =====================================================================
def health_impact_engine(food, condition):
    if condition == "prediabetic_risk":
        return f"""
🧠 Prediabetes Metabolic Impact:

- {food} improves insulin sensitivity via polyphenols
- Reduces post-meal glucose spikes
- Supports metabolic stabilization
"""

    elif condition == "inflammation":
        return f"""
🧠 Inflammation Impact:

- {food} reduces inflammatory cytokines
- Supports muscle recovery and tissue repair
- Lowers systemic oxidative stress
"""

    else:
        return f"""
🧠 Performance Impact:

- {food} supports energy stability and recovery
- Enhances metabolic efficiency and muscle maintenance
"""

# =====================================================================
# DUBAI STORE INTELLIGENCE
# =====================================================================
def dubai_store_intelligence(food):
    stores = [
        {"Store": "Carrefour UAE", "Type": "Hypermarket", "Quality": "Medium"},
        {"Store": "Spinneys Dubai", "Type": "Premium Supermarket", "Quality": "High"},
        {"Store": "Waitrose Dubai", "Type": "Imported Goods", "Quality": "Very High"}
    ]
    return pd.DataFrame(stores)

# =====================================================================
# MEAL GENERATION ENGINE (NEW CORE UPGRADE)
# =====================================================================
def generate_meal_plan(condition, goal):

    if condition == "prediabetic_risk":
        return [
            {
                "meal": "🥣 Morning Glycemic Control Bowl",
                "timing": "08:00 - 10:00",
                "macro": "40C / 30P / 30F",
                "components": {
                    "Base": "Steel-cut oats + chia seeds",
                    "Protein": "Greek yogurt",
                    "Fat": "Almonds + flaxseed",
                    "Fruit": "Blueberries"
                },
                "why": "Stabilizes blood glucose and reduces insulin spikes"
            },
            {
                "meal": "🥗 Midday Metabolic Stability Bowl",
                "timing": "13:00 - 15:00",
                "macro": "30C / 40P / 30F",
                "components": {
                    "Protein": "Grilled chicken or tofu",
                    "Carbs": "Quinoa",
                    "Veg": "Spinach, broccoli",
                    "Fat": "Olive oil"
                },
                "why": "Improves insulin sensitivity and sustained energy"
            },
            {
                "meal": "🍲 Evening Low-GI Dinner",
                "timing": "18:00 - 20:00",
                "macro": "10C / 45P / 45F",
                "components": {
                    "Protein": "Salmon",
                    "Veg": "Zucchini, kale",
                    "Fat": "Avocado"
                },
                "why": "Minimizes nighttime glucose load"
            }
        ]

    elif condition == "inflammation":
        return [
            {
                "meal": "🥤 Anti-Inflammatory Smoothie Bowl",
                "timing": "08:00 - 10:00",
                "macro": "45C / 25P / 30F",
                "components": {
                    "Base": "Spinach + kale",
                    "Fruit": "Blueberries + pineapple",
                    "Fat": "Walnuts + flaxseed",
                    "Liquid": "Almond milk"
                },
                "why": "Reduces systemic inflammation and oxidative stress"
            },
            {
                "meal": "🍛 Recovery Lunch Bowl",
                "timing": "13:00 - 15:00",
                "macro": "35C / 35P / 30F",
                "components": {
                    "Protein": "Salmon",
                    "Carbs": "Brown rice",
                    "Veg": "Broccoli, turmeric carrots",
                    "Fat": "Olive oil"
                },
                "why": "Supports recovery and reduces inflammation"
            },
            {
                "meal": "🍵 Healing Soup Dinner",
                "timing": "18:00 - 20:00",
                "macro": "20C / 40P / 40F",
                "components": {
                    "Base": "Bone broth",
                    "Protein": "Lentils",
                    "Veg": "Garlic, ginger, greens"
                },
                "why": "Supports overnight tissue repair"
            }
        ]

    else:
        return [
            {
                "meal": "🍳 Performance Breakfast",
                "timing": "07:00 - 09:00",
                "macro": "35C / 35P / 30F",
                "components": {
                    "Protein": "Eggs + yogurt",
                    "Carbs": "Oats",
                    "Fat": "Avocado"
                },
                "why": "Balanced energy and muscle support"
            },
            {
                "meal": "🥗 Balanced Lunch",
                "timing": "12:00 - 14:00",
                "macro": "40C / 35P / 25F",
                "components": {
                    "Protein": "Chicken",
                    "Carbs": "Brown rice",
                    "Veg": "Mixed greens"
                },
                "why": "Stable energy and cognitive performance"
            },
            {
                "meal": "🍲 Light Dinner",
                "timing": "18:00 - 20:00",
                "macro": "20C / 40P / 40F",
                "components": {
                    "Protein": "Fish",
                    "Veg": "Steamed vegetables",
                    "Fat": "Olive oil"
                },
                "why": "Supports overnight recovery"
            }
        ]

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

# ---------------------------------------------------------------------
# PAGE 2
# ---------------------------------------------------------------------
elif page.startswith("2️⃣"):
    st.header("🔬 Farm → Plate Intelligence")

    food = st.selectbox("Select Food", ["Salmon","Oats","Blueberries","Lentils","Spinach"])

    df = simulate_supply_detailed(food)

    st.subheader("Supply Chain Data")
    st.dataframe(df)

    st.subheader("Nutrient Degradation")
    st.line_chart(df.set_index("Stage")[["Vitamin C","Protein","Polyphenols"]])

    st.subheader("Narrative Explanation")
    st.write(build_supply_chain_story(food, df))

    user = st.session_state.get("user", {})
    condition = detect_condition(user) if user else "general_fitness"

    st.subheader("Health Impact")
    st.write(health_impact_engine(food, condition))

    st.subheader("Dubai Stores")
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

    st.header("🧠 Whole Meal Nutrition System")

    meals = generate_meal_plan(condition, user["goal"])

    st.subheader(f"Condition: {condition}")

    for m in meals:
        st.markdown(f"## {m['meal']}")
        st.write(f"⏱ {m['timing']}  |  ⚖ {m['macro']}")

        st.markdown("### Components")
        for k, v in m["components"].items():
            st.write(f"- {k}: {v}")

        st.markdown("### Why this meal works")
        st.write(m["why"])

        st.divider()

    st.success("Meals optimized for physiology + supply chain intelligence.")
