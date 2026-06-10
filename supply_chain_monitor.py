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
# WEARABLE DATA SIMULATION
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
# LIFESTYLE INFERENCE ENGINE (WEARABLE-BASED)
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
# SUPPLY CHAIN SIMULATION
# =========================================================
def simulate_supply(food):
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

    data = []
    state = nutrients.copy()

    for stage in stages:
        temp = np.random.uniform(2, 35)
        humidity = np.random.uniform(40, 95)
        days = np.random.uniform(0.5, 5)

        decay = np.exp(-0.05 * days * (temp / 25))

        for k in state:
            state[k] *= decay

        data.append({
            "Stage": stage,
            "Temperature": round(temp, 1),
            "Humidity": round(humidity, 1),
            "Vitamin C": round(state["Vitamin C"], 1),
            "Protein": round(state["Protein"], 1),
            "Polyphenols": round(state["Polyphenols"], 1)
        })

    return pd.DataFrame(data)

# =========================================================
# SUPPLY CHAIN NARRATIVE ENGINE
# =========================================================
def build_story(food, df):
    story = [f"🌱 {food} begins its lifecycle in controlled agricultural systems."]

    for _, r in df.iterrows():
        if r["Stage"] == "Farm Cultivation":
            story.append("Farm conditions determine baseline nutrient density.")
        elif r["Stage"] == "Harvest":
            story.append("Harvest introduces oxidative nutrient loss.")
        elif r["Stage"] == "Post-Harvest Handling":
            story.append("Handling increases microbial exposure risk.")
        elif r["Stage"] == "Cold Storage":
            story.append("Cold storage slows enzymatic degradation.")
        elif r["Stage"] == "Transportation":
            story.append("Transport causes temperature-driven nutrient decay.")
        elif r["Stage"] == "Retail Shelf":
            story.append("Shelf time defines final nutrient availability.")

    story.append("🥗 Final nutrition is cumulative across all stages.")
    return "\n\n".join(story)

# =========================================================
# HEALTH ENGINE
# =========================================================
def detect_condition(user):
    if user["BMI"] > 28:
        return "prediabetic_risk"
    if user["stress_level"] == "high" and user["sleep_quality"] == "poor":
        return "inflammation"
    return "general_fitness"

def health_engine(food, condition):
    if condition == "prediabetic_risk":
        return f"{food} improves insulin sensitivity and reduces glucose spikes."
    if condition == "inflammation":
        return f"{food} reduces inflammation and supports recovery."
    return f"{food} supports general metabolic performance."

# =========================================================
# MEAL ENGINE (WHOLE MEALS)
# =========================================================
def meal_plan(condition):
    if condition == "prediabetic_risk":
        return [
            {
                "meal": "🥣 Glycemic Stability Breakfast",
                "time": "08:00",
                "macro": "40C / 30P / 30F",
                "items": "Oats + chia + Greek yogurt + blueberries"
            },
            {
                "meal": "🥗 Metabolic Control Lunch",
                "time": "13:00",
                "macro": "30C / 40P / 30F",
                "items": "Chicken + quinoa + spinach + olive oil"
            },
            {
                "meal": "🍲 Low Glycemic Dinner",
                "time": "19:00",
                "macro": "10C / 45P / 45F",
                "items": "Salmon + avocado + greens"
            }
        ]

    if condition == "inflammation":
        return [
            {
                "meal": "🥤 Anti-Inflammatory Breakfast",
                "time": "08:00",
                "macro": "45C / 25P / 30F",
                "items": "Spinach smoothie + berries + flaxseed"
            },
            {
                "meal": "🍛 Recovery Lunch",
                "time": "13:00",
                "macro": "35C / 35P / 30F",
                "items": "Salmon + brown rice + broccoli"
            },
            {
                "meal": "🍵 Healing Dinner",
                "time": "19:00",
                "macro": "20C / 40P / 40F",
                "items": "Bone broth + lentils + garlic"
            }
        ]

    return [
        {
            "meal": "🍳 Balanced Breakfast",
            "time": "08:00",
            "macro": "35C / 35P / 30F",
            "items": "Eggs + oats + avocado"
        },
        {
            "meal": "🥗 Performance Lunch",
            "time": "13:00",
            "macro": "40C / 35P / 25F",
            "items": "Chicken + rice + vegetables"
        },
        {
            "meal": "🍲 Light Dinner",
            "time": "19:00",
            "macro": "20C / 40P / 40F",
            "items": "Fish + greens + olive oil"
        }
    ]

# =========================================================
# DUBAI STORES
# =========================================================
def dubai_stores():
    return pd.DataFrame([
        {"Store": "Carrefour UAE", "Type": "Hypermarket", "Quality": "Medium"},
        {"Store": "Spinneys Dubai", "Type": "Premium", "Quality": "High"},
        {"Store": "Waitrose Dubai", "Type": "Imported", "Quality": "Very High"}
    ])

# =========================================================
# UI
# =========================================================
st.title("🥗 Precision Nutrition Intelligence System")

page = st.sidebar.radio("Navigation",
    ["1️⃣ Profile","2️⃣ Supply Chain","3️⃣ Meals"]
)

# =========================================================
# PAGE 1
# =========================================================
if page.startswith("1️⃣"):
    st.header("User Profile")

    with st.form("profile"):
        age = st.number_input("Age", 18, 80, 30)
        sex = st.selectbox("Sex", ["Male","Female"])
        height = st.number_input("Height (cm)", 120, 220, 170)
        weight = st.number_input("Weight (kg)", 40, 200, 70)
        goal = st.selectbox("Goal", ["weight_loss","energy_boost","glucose_control"])
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

        st.subheader("Inferred Lifestyle")
        st.json(lifestyle)

# =========================================================
# PAGE 2
# =========================================================
elif page.startswith("2️⃣"):
    st.header("Farm → Plate Intelligence")

    food = st.selectbox("Select Food", ["Salmon","Oats","Blueberries","Lentils","Spinach"])

    df = simulate_supply(food)

    st.subheader("Supply Chain Data")
    st.dataframe(df)

    st.subheader("Nutrient Trend")
    st.line_chart(df.set_index("Stage")[["Vitamin C","Protein","Polyphenols"]])

    st.subheader("Food Narrative")
    st.write(build_story(food, df))

    user = st.session_state.get("user", {})
    condition = detect_condition(user) if user else "general_fitness"

    st.subheader("Health Impact")
    st.write(health_engine(food, condition))

    st.subheader("Dubai Stores")
    st.dataframe(dubai_stores())

# =========================================================
# PAGE 3
# =========================================================
elif page.startswith("3️⃣"):
    user = st.session_state.get("user")

    if not user:
        st.warning("Complete profile first")
        st.stop()

    condition = detect_condition(user)

    st.header("Whole Meal Nutrition System")

    meals = meal_plan(condition)

    st.subheader(f"Condition: {condition}")

    for m in meals:
        st.markdown(f"## {m['meal']}")
        st.write(f"⏱ {m['time']} | ⚖ {m['macro']}")
        st.write(f"🍽 {m['items']}")
        st.divider()

    st.success("System is now operating as a physiological nutrition intelligence engine.")
