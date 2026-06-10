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

def clamp(x, minv=0, maxv=100):
    return max(minv, min(x, maxv))

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

    return {
        "sleep_quality": "good" if avg_sleep >= 85 else "average" if avg_sleep >= 70 else "poor",
        "stress_level": "low" if (100 - avg_hrv) < 40 else "medium" if (100 - avg_hrv) < 70 else "high",
        "activity_level": "high" if avg_steps >= 9000 else "moderate" if avg_steps >= 5000 else "low",
        "avg_hrv": avg_hrv,
        "avg_strain": avg_strain,
        "avg_sleep": avg_sleep,
        "avg_steps": avg_steps
    }

# =========================================================
# HEALTH SCORE
# =========================================================
def compute_health_score(user):
    bmi_score = max(0, 100 - abs(user["BMI"] - 22) * 6)

    sleep_score = {"good": 90, "average": 70, "poor": 40}[user["sleep_quality"]]
    stress_score = {"low": 90, "medium": 65, "high": 35}[user["stress_level"]]
    activity_score = {"high": 90, "moderate": 70, "low": 50}[user["activity_level"]]

    strain_penalty = max(0, 100 - user["avg_strain"] * 4)

    return round(
        bmi_score * 0.25 +
        sleep_score * 0.2 +
        stress_score * 0.2 +
        activity_score * 0.2 +
        strain_penalty * 0.15,
        1
    )

# =========================================================
# RISK DETECTION
# =========================================================
def detect_health_risks(user):
    risks = []

    if user["BMI"] > 30:
        risks.append("metabolic_syndrome_risk")

    if user["sleep_quality"] == "poor" and user["stress_level"] == "high":
        risks.append("chronic_inflammation_risk")

    if user["activity_level"] == "low":
        risks.append("insulin_resistance_risk")

    if user["avg_hrv"] < 45:
        risks.append("autonomic_dysregulation_risk")

    return risks if risks else ["healthy_baseline"]

# =========================================================
# NUTRITION PATHWAY
# =========================================================
def nutrition_pathway(risks):
    base = {
        "metabolic_syndrome_risk": {
            "phase": "Glycemic Stabilization",
            "foods": ["Oats", "Lentils", "Blueberries", "Quinoa"],
            "goal": "Lower insulin spikes"
        },
        "chronic_inflammation_risk": {
            "phase": "Inflammation Repair",
            "foods": ["Salmon", "Spinach", "Olive Oil", "Garlic"],
            "goal": "Reduce inflammation"
        },
        "insulin_resistance_risk": {
            "phase": "Metabolic Reactivation",
            "foods": ["Eggs", "Avocado", "Chicken Breast"],
            "goal": "Restore insulin sensitivity"
        },
        "autonomic_dysregulation_risk": {
            "phase": "Nervous System Recovery",
            "foods": ["Walnuts", "Bananas", "Greek Yogurt"],
            "goal": "Improve HRV balance"
        },
        "healthy_baseline": {
            "phase": "Maintenance",
            "foods": ["Balanced whole foods"],
            "goal": "Maintain health"
        }
    }

    return [base[r] for r in risks if r in base]

# =========================================================
# 🧬 DIGITAL TWIN ENGINE (NEW CORE LAYER)
# =========================================================
def initial_health_state(user):
    return {
        "energy": 70,
        "inflammation": clamp(50 + user["avg_strain"] * 2),
        "metabolic": clamp(100 - (user["BMI"] - 22) * 5),
        "recovery": clamp(user["avg_sleep"]),
        "stress": clamp(100 - user["avg_hrv"])
    }

def apply_food_effect(state, food):
    effects = {
        "Salmon": {"inflammation": -6, "recovery": +5},
        "Oats": {"metabolic": +6, "stress": -3},
        "Blueberries": {"inflammation": -4, "metabolic": +3},
        "Lentils": {"metabolic": +5, "energy": +4},
        "Spinach": {"recovery": +4, "inflammation": -3},
        "Eggs": {"energy": +5, "recovery": +3},
        "Avocado": {"stress": -4, "recovery": +3}
    }

    for k, v in effects.get(food, {}).items():
        state[k] = clamp(state[k] + v)

    return state

def run_digital_twin(user, foods, days=7):
    state = initial_health_state(user)
    timeline = []

    for d in range(days):

        # natural drift
        state["energy"] = clamp(state["energy"] - 1 + np.random.randn())
        state["stress"] = clamp(state["stress"] + 1)
        state["recovery"] = clamp(state["recovery"] - 0.5)

        # food effects
        for f in foods:
            state = apply_food_effect(state, f)

        risk_score = (
            0.3 * state["stress"] +
            0.3 * (100 - state["recovery"]) +
            0.2 * (100 - state["metabolic"]) +
            0.2 * state["inflammation"]
        )

        timeline.append({
            "Day": d,
            "Energy": state["energy"],
            "Stress": state["stress"],
            "Recovery": state["recovery"],
            "Inflammation": state["inflammation"],
            "Metabolic": state["metabolic"],
            "RiskScore": risk_score
        })

    return pd.DataFrame(timeline)

# =========================================================
# FOOD + STORE DATA (UNCHANGED)
# =========================================================
FOOD_CATALOG = [
    "Salmon","Oats","Blueberries","Lentils","Spinach",
    "Chicken Breast","Eggs","Brown Rice","Quinoa",
    "Broccoli","Avocado","Greek Yogurt","Almonds",
    "Walnuts","Sweet Potato","Tomatoes","Garlic",
    "Ginger","Olive Oil","Bananas","Apples"
]

def dubai_store_intelligence_bulk(food_list):
    stores = ["Carrefour UAE","Spinneys Dubai","Waitrose Dubai"]

    rows = []
    for food in food_list:
        for store in stores:
            rows.append({
                "Food": food,
                "Store": store,
                "Availability": np.random.choice(["High","Medium","Low"]),
                "Quality": np.random.choice(["Premium","Standard","Organic"])
            })

    return pd.DataFrame(rows)

# =========================================================
# UI
# =========================================================
st.title("🥗 Precision Nutrition Intelligence System + Digital Twin")

page = st.sidebar.radio(
    "Navigation",
    ["1️⃣ Profile","2️⃣ Supply Chain","3️⃣ Health Intelligence + Twin"]
)

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

        user = {
            "age": age,
            "sex": sex,
            "height": height,
            "weight": weight,
            "BMI": weight / ((height/100)**2),
            **lifestyle
        }

        st.session_state["user"] = user

        st.subheader("Lifestyle Snapshot")
        st.json(lifestyle)

# =========================================================
# PAGE 2
# =========================================================
elif page.startswith("2️⃣"):
    st.header("Supply Chain Intelligence")

    foods = st.multiselect("Select Foods", FOOD_CATALOG, default=["Salmon","Oats"])

    st.dataframe(dubai_store_intelligence_bulk(foods))

# =========================================================
# PAGE 3
# =========================================================
elif page.startswith("3️⃣"):
    user = st.session_state.get("user")

    if not user:
        st.warning("Complete profile first")
        st.stop()

    st.header("🧠 Health + Digital Twin Engine")

    health_score = compute_health_score(user)
    risks = detect_health_risks(user)
    pathway = nutrition_pathway(risks)

    st.metric("Health Score", health_score)
    st.write("Risks:", risks)

    st.subheader("Nutrition Pathway")
    for p in pathway:
        st.markdown(f"### {p['phase']}")
        st.write(p["goal"])
        st.write(p["foods"])
        st.divider()

    st.subheader("🧬 Digital Twin Simulation")

    foods = []
    for p in pathway:
        foods += p["foods"]

    foods = list(set(foods))

    df = run_digital_twin(user, foods, days=10)

    st.line_chart(df.set_index("Day")[["Energy","Stress","Recovery","Inflammation","Metabolic"]])
    st.line_chart(df.set_index("Day")[["RiskScore"]])

    st.success("System now includes physiological prediction + adaptive nutrition + risk pathways.")
