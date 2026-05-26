import streamlit as st
import pandas as pd
import numpy as np
import datetime
from dataclasses import dataclass

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Precision Nutrition Intelligence",
    layout="wide"
)

# =========================================================
# SESSION INIT
# =========================================================
def init():
    keys = ["users", "history", "habits"]

    for k in keys:
        if k not in st.session_state:
            st.session_state[k] = []

init()

# =========================================================
# FOOD DOMAIN
# =========================================================
FOODS = [
    "Salmon",
    "Oats",
    "Eggs",
    "Spinach",
    "Chicken Breast",
    "Avocado",
    "Blueberries"
]

# =========================================================
# FOOD KNOWLEDGE
# =========================================================
FOOD_LIBRARY = {

    "Salmon": {
        "goal": ["fitness", "glucose_control"],
        "category": [
            "RECOVERY_SUPPORT",
            "ANTI_INFLAMMATORY"
        ],
        "desc": "Omega-3 rich recovery food"
    },

    "Oats": {
        "goal": ["glucose_control"],
        "category": [
            "GLUCOSE_STABILIZING",
            "MICROBIOME_SUPPORT"
        ],
        "desc": "Stable energy carbohydrates"
    },

    "Eggs": {
        "goal": ["fitness"],
        "category": [
            "RECOVERY_SUPPORT"
        ],
        "desc": "Complete protein source"
    },

    "Spinach": {
        "goal": ["glucose_control"],
        "category": [
            "MICROBIOME_SUPPORT",
            "ANTI_INFLAMMATORY"
        ],
        "desc": "Micronutrient dense greens"
    },

    "Chicken Breast": {
        "goal": ["fitness", "fat_loss"],
        "category": [
            "RECOVERY_SUPPORT"
        ],
        "desc": "Lean protein support"
    },

    "Avocado": {
        "goal": ["fat_loss"],
        "category": [
            "ANTI_INFLAMMATORY"
        ],
        "desc": "Healthy fats"
    },

    "Blueberries": {
        "goal": ["glucose_control"],
        "category": [
            "COGNITIVE_SUPPORT",
            "ANTI_INFLAMMATORY"
        ],
        "desc": "Antioxidant support"
    }
}

# =========================================================
# BASE NUTRITION DATABASE
# =========================================================
BASE_NUTRITION = {

    "Salmon": {
        "protein": 25,
        "omega3": 100,
        "vitamin_d": 90,
        "selenium": 75,
        "b12": 85,
        "cal": 208
    },

    "Oats": {
        "fiber": 85,
        "protein": 17,
        "magnesium": 70,
        "beta_glucan": 95,
        "polyphenols": 55,
        "cal": 389
    },

    "Eggs": {
        "protein": 12,
        "b12": 70,
        "choline": 88,
        "selenium": 60,
        "vitamin_d": 50,
        "cal": 155
    },

    "Spinach": {
        "magnesium": 95,
        "iron": 90,
        "folate": 88,
        "fiber": 70,
        "vitamin_k": 100,
        "cal": 23
    },

    "Chicken Breast": {
        "protein": 31,
        "selenium": 55,
        "b6": 60,
        "niacin": 70,
        "cal": 165
    },

    "Avocado": {
        "healthy_fats": 90,
        "fiber": 65,
        "potassium": 80,
        "folate": 50,
        "cal": 160
    },

    "Blueberries": {
        "polyphenols": 100,
        "vitamin_c": 80,
        "fiber": 45,
        "antioxidants": 100,
        "cal": 57
    }
}

# =========================================================
# NUTRIENT SENSITIVITY
# =========================================================
NUTRIENT_SENSITIVITY = {

    "vitamin_c": 1.8,

    "polyphenols": 1.6,

    "omega3": 1.5,

    "vitamin_d": 1.3,

    "antioxidants": 1.6,

    "healthy_fats": 1.2,

    "magnesium": 0.5,

    "protein": 0.3,

    "fiber": 0.4
}

# =========================================================
# NUTRIENT BIOLOGICAL EFFECTS
# =========================================================
NUTRIENT_EFFECTS = {

    "omega3": [
        "Improves recovery",
        "Reduces inflammation",
        "Supports cardiovascular health"
    ],

    "protein": [
        "Supports muscle repair",
        "Improves satiety"
    ],

    "fiber": [
        "Stabilizes glucose",
        "Supports gut microbiome"
    ],

    "polyphenols": [
        "Reduces oxidative stress",
        "Supports metabolic health"
    ],

    "magnesium": [
        "Supports sleep quality",
        "Improves muscle recovery"
    ],

    "vitamin_c": [
        "Supports immunity",
        "Reduces oxidative stress"
    ],

    "healthy_fats": [
        "Supports hormone balance",
        "Improves satiety"
    ],

    "antioxidants": [
        "Protects cells from stress",
        "Supports cognitive health"
    ]
}

# =========================================================
# SUPPLY TELEMETRY MODEL
# =========================================================
@dataclass
class SupplyTelemetry:

    farm_id: str

    harvest_date: datetime.date

    soil_quality: float

    pesticide_score: float

    avg_transport_temp: float

    transport_delay_hours: int

    warehouse_days: int

    humidity_exposure: float

    processing_level: float

    contamination_risk: float

    cold_chain_breaks: int

# =========================================================
# MOCK REAL FARM-TO-PLATE DATA
# =========================================================
def fetch_supply_chain_data(food):

    rng = np.random.default_rng(
        abs(hash(food)) % 10000
    )

    return SupplyTelemetry(

        farm_id=f"FARM-{rng.integers(100,999)}",

        harvest_date=datetime.date.today() -
        datetime.timedelta(
            days=int(rng.integers(1,10))
        ),

        soil_quality=round(
            rng.uniform(0.6,1.0),2
        ),

        pesticide_score=round(
            rng.uniform(0.0,0.4),2
        ),

        avg_transport_temp=round(
            rng.uniform(2,15),1
        ),

        transport_delay_hours=int(
            rng.integers(0,20)
        ),

        warehouse_days=int(
            rng.integers(1,7)
        ),

        humidity_exposure=round(
            rng.uniform(0.2,0.9),2
        ),

        processing_level=round(
            rng.uniform(0.0,0.6),2
        ),

        contamination_risk=round(
            rng.uniform(0.0,0.4),2
        ),

        cold_chain_breaks=int(
            rng.integers(0,3)
        )
    )

# =========================================================
# USER ENGINE
# =========================================================
def create_user(weight, height, goal):

    uid = len(st.session_state.users) + 1

    bmi = round(
        weight / (height ** 2),
        1
    )

    st.session_state.users.append({

        "id": uid,

        "weight": weight,

        "height": height,

        "goal": goal,

        "bmi": bmi
    })

# =========================================================
# WEARABLE ENGINE
# =========================================================
def wearable(uid):

    rng = np.random.default_rng(uid)

    return {

        "sleep": round(
            rng.uniform(5,8),2
        ),

        "recovery": int(
            rng.uniform(30,95)
        ),

        "strain": round(
            rng.uniform(5,18),1
        ),

        "glucose_variability": round(
            rng.uniform(10,40),1
        ),

        "hrv": int(
            rng.uniform(20,90)
        )
    }

# =========================================================
# HEALTH ENGINE
# =========================================================
def health_score(user, wear):

    score = 0

    reasons = []

    if user["bmi"] > 27:
        score += 2
        reasons.append("High BMI")

    if wear["sleep"] < 6:
        score += 2
        reasons.append("Poor Sleep")

    if wear["recovery"] < 50:
        score += 2
        reasons.append("Low Recovery")

    if wear["glucose_variability"] > 30:
        score += 2
        reasons.append("Glucose Instability")

    risk = "LOW"

    if score >= 6:
        risk = "HIGH"

    elif score >= 3:
        risk = "MODERATE"

    return risk, reasons

# =========================================================
# NUTRIENT RETENTION ENGINE
# =========================================================
def adjusted_nutrients(food, telemetry):

    base = BASE_NUTRITION[food]

    adjusted = {}

    heat_factor = (
        telemetry.avg_transport_temp / 10
    )

    delay_factor = (
        telemetry.transport_delay_hours / 24
    )

    processing_factor = (
        telemetry.processing_level
    )

    for nutrient, value in base.items():

        sensitivity = NUTRIENT_SENSITIVITY.get(
            nutrient,
            1.0
        )

        degradation = (

            heat_factor * 0.2 * sensitivity

            +

            delay_factor * 0.15 * sensitivity

            +

            processing_factor * 0.25 * sensitivity

        )

        retention = max(
            0.2,
            1 - degradation
        )

        adjusted[nutrient] = {

            "original": value,

            "remaining": round(
                value * retention,
                1
            ),

            "retention_percent": round(
                retention * 100,
                1
            )
        }

    return adjusted

# =========================================================
# FOOD INTEGRITY ENGINE
# =========================================================
def compute_integrity_score(telemetry):

    score = 100

    if telemetry.avg_transport_temp > 10:
        score -= 15

    score -= (
        telemetry.transport_delay_hours * 0.5
    )

    score -= (
        telemetry.warehouse_days * 1.5
    )

    score -= (
        telemetry.processing_level * 20
    )

    score -= (
        telemetry.contamination_risk * 25
    )

    score -= (
        telemetry.cold_chain_breaks * 10
    )

    score += (
        telemetry.soil_quality * 10
    )

    score -= (
        telemetry.pesticide_score * 15
    )

    return round(
        max(min(score,100),0),
        1
    )

# =========================================================
# USER PREFERENCE ENGINE
# =========================================================
def preferences(uid):

    df = pd.DataFrame(
        st.session_state.history
    )

    if df.empty:
        return {}

    df = df[df.user == uid]

    if df.empty:
        return {}

    result = {}

    for food, g in df.groupby("food"):

        result[food] = len(
            g[g.decision == "yes"]
        ) / len(g)

    return result

# =========================================================
# HABIT ENGINE
# =========================================================
def log_habit(uid, food):

    st.session_state.habits.append({

        "user": uid,

        "food": food,

        "date": datetime.date.today()
    })

def habit_score(uid):

    df = pd.DataFrame(
        st.session_state.habits
    )

    if df.empty:
        return 0

    return len(df[df.user == uid])

# =========================================================
# BIOLOGICAL EXPLANATION ENGINE
# =========================================================
def explain_food(user, wear, nutrients):

    explanations = []

    for nutrient, data in nutrients.items():

        if data["retention_percent"] < 50:
            continue

        effects = NUTRIENT_EFFECTS.get(
            nutrient,
            []
        )

        # Recovery Support
        if wear["recovery"] < 50:

            if nutrient in [
                "omega3",
                "magnesium",
                "protein"
            ]:

                explanations.extend(effects)

        # Glucose Support
        if wear["glucose_variability"] > 30:

            if nutrient in [
                "fiber",
                "polyphenols"
            ]:

                explanations.extend(effects)

        # General Benefits
        explanations.extend(effects)

    return list(set(explanations))

# =========================================================
# RECOMMENDATION ENGINE
# =========================================================
def food_recommendation(food, user, wear):

    telemetry = fetch_supply_chain_data(food)

    integrity = compute_integrity_score(
        telemetry
    )

    nutrients = adjusted_nutrients(
        food,
        telemetry
    )

    explanations = explain_food(
        user,
        wear,
        nutrients
    )

    score = 50

    # Goal Alignment
    if user["goal"] in FOOD_LIBRARY[food]["goal"]:
        score += 20

    # Recovery Support
    if wear["recovery"] < 50:
        score += 10

    # Glucose Support
    if wear["glucose_variability"] > 30:
        score += 10

    # Food Integrity
    score += integrity * 0.3

    return {

        "food": food,

        "description":
        FOOD_LIBRARY[food]["desc"],

        "categories":
        FOOD_LIBRARY[food]["category"],

        "integrity": integrity,

        "score": round(score,1),

        "nutrients": nutrients,

        "telemetry": telemetry,

        "explanations": explanations
    }

# =========================================================
# RECOMMENDER
# =========================================================
def recommend(user, uid):

    wear = wearable(uid)

    recommendations = []

    for food in FOODS:

        recommendations.append(

            food_recommendation(
                food,
                user,
                wear
            )
        )

    df = pd.DataFrame(
        recommendations
    )

    return df.sort_values(
        "score",
        ascending=False
    ), wear

# =========================================================
# UI
# =========================================================
st.title(
    "🧠 Precision Nutrition Intelligence"
)

page = st.sidebar.radio(

    "Pages",

    [
        "Create User",
        "Health Insights",
        "Recommendations",
        "Habit Tracker",
        "Food Intelligence"
    ]
)

# =========================================================
# CREATE USER
# =========================================================
if page == "Create User":

    weight = st.number_input(
        "Weight (kg)",
        40.0,
        200.0,
        75.0
    )

    height = st.number_input(
        "Height (m)",
        1.2,
        2.5,
        1.75
    )

    goal = st.selectbox(

        "Goal",

        [
            "fitness",
            "fat_loss",
            "glucose_control"
        ]
    )

    if st.button("Create User"):

        create_user(
            weight,
            height,
            goal
        )

        st.success("User Created")

# =========================================================
# HEALTH INSIGHTS
# =========================================================
elif page == "Health Insights":

    users = pd.DataFrame(
        st.session_state.users
    )

    if users.empty:
        st.stop()

    uid = st.selectbox(
        "User",
        users.id
    )

    user = users[
        users.id == uid
    ].iloc[0].to_dict()

    wear = wearable(uid)

    risk, reasons = health_score(
        user,
        wear
    )

    st.subheader("Physiology")

    c1,c2,c3,c4,c5 = st.columns(5)

    c1.metric("BMI", user["bmi"])

    c2.metric("Sleep", wear["sleep"])

    c3.metric("Recovery", wear["recovery"])

    c4.metric("HRV", wear["hrv"])

    c5.metric(
        "Glucose Variability",
        wear["glucose_variability"]
    )

    st.subheader("Risk Assessment")

    st.write("Risk:", risk)

    st.write("Drivers:", reasons)

# =========================================================
# RECOMMENDATIONS
# =========================================================
elif page == "Recommendations":

    users = pd.DataFrame(
        st.session_state.users
    )

    if users.empty:
        st.stop()

    uid = st.selectbox(
        "User",
        users.id
    )

    user = users[
        users.id == uid
    ].iloc[0].to_dict()

    recs, wear = recommend(
        user,
        uid
    )

    st.subheader(
        "Wearable Intelligence"
    )

    st.write(wear)

    st.subheader(
        "Precision Nutrition Recommendations"
    )

    for _, r in recs.iterrows():

        with st.container(border=True):

            st.subheader(r.food)

            st.write(r.description)

            st.write(
                "Biological Categories:",
                ", ".join(r.categories)
            )

            st.metric(
                "Food Integrity",
                r.integrity
            )

            st.subheader(
                "Remaining Nutrients"
            )

            for nutrient, values in r.nutrients.items():

                st.write(

                    f"""
                    {nutrient.upper()}
                    →
                    Remaining:
                    {values['remaining']}
                    |
                    Retention:
                    {values['retention_percent']}%
                    """
                )

                st.progress(
                    values["retention_percent"] / 100
                )

            st.subheader(
                "Why This Helps You"
            )

            for e in r.explanations:

                st.write(f"• {e}")

            telemetry = r.telemetry

            st.subheader(
                "Food Chain Intelligence"
            )

            st.write({

                "Farm ID":
                telemetry.farm_id,

                "Harvest Date":
                str(telemetry.harvest_date),

                "Transport Temp":
                telemetry.avg_transport_temp,

                "Delay Hours":
                telemetry.transport_delay_hours,

                "Warehouse Days":
                telemetry.warehouse_days,

                "Cold Chain Breaks":
                telemetry.cold_chain_breaks,

                "Contamination Risk":
                telemetry.contamination_risk
            })

            c1,c2 = st.columns(2)

            if c1.button(
                f"Accept {r.food}",
                key=f"a{uid}{r.food}"
            ):

                st.session_state.history.append({

                    "user": uid,

                    "food": r.food,

                    "decision": "yes"
                })

                log_habit(uid, r.food)

                st.rerun()

            if c2.button(
                f"Reject {r.food}",
                key=f"r{uid}{r.food}"
            ):

                st.session_state.history.append({

                    "user": uid,

                    "food": r.food,

                    "decision": "no"
                })

                st.rerun()

# =========================================================
# HABIT TRACKER
# =========================================================
elif page == "Habit Tracker":

    users = pd.DataFrame(
        st.session_state.users
    )

    if users.empty:
        st.stop()

    uid = st.selectbox(
        "User",
        users.id
    )

    st.metric(
        "Healthy Nutrition Actions",
        habit_score(uid)
    )

# =========================================================
# FOOD INTELLIGENCE
# =========================================================
elif page == "Food Intelligence":

    food = st.selectbox(
        "Food",
        FOODS
    )

    telemetry = fetch_supply_chain_data(
        food
    )

    integrity = compute_integrity_score(
        telemetry
    )

    nutrients = adjusted_nutrients(
        food,
        telemetry
    )

    st.subheader(
        "Farm → Plate Intelligence"
    )

    st.write({

        "Farm ID":
        telemetry.farm_id,

        "Harvest Date":
        str(telemetry.harvest_date),

        "Soil Quality":
        telemetry.soil_quality,

        "Pesticide Score":
        telemetry.pesticide_score,

        "Transport Temperature":
        telemetry.avg_transport_temp,

        "Delay Hours":
        telemetry.transport_delay_hours,

        "Warehouse Days":
        telemetry.warehouse_days,

        "Processing Level":
        telemetry.processing_level,

        "Contamination Risk":
        telemetry.contamination_risk,

        "Cold Chain Breaks":
        telemetry.cold_chain_breaks
    })

    st.metric(
        "Food Integrity",
        integrity
    )

    st.subheader(
        "Nutrient Retention"
    )

    for nutrient, values in nutrients.items():

        st.write(

            f"""
            {nutrient.upper()}
            →
            Remaining:
            {values['remaining']}
            |
            Retention:
            {values['retention_percent']}%
            """
        )

        st.progress(
            values["retention_percent"] / 100
        )
