import streamlit as st
import pandas as pd
import numpy as np
import datetime
import hashlib
import requests
import os

st.set_page_config(page_title="Food Intelligence System", layout="wide")

# =========================================================
# CONFIG / CONSTANTS
# =========================================================
FOODS = [
    "Salmon", "Sardines", "Mackerel", "Oats", "Blueberries", "Lentils", "Spinach",
    "Chicken Breast", "Avocado", "Eggs", "Brown Rice", "Yogurt", "Sweet Potato",
    "Broccoli", "Tomatoes", "Walnuts", "Almonds", "Greek Yogurt", "Chickpeas",
    "Black Beans", "Quinoa", "Tofu", "Tempeh", "Oranges", "Bananas", "Dates",
    "Pomegranate", "Kale", "Garlic", "Ginger"
]

PRICE_MAP = {
    "Salmon": 15, "Sardines": 7, "Mackerel": 8, "Oats": 3, "Blueberries": 6,
    "Lentils": 2, "Spinach": 4, "Chicken Breast": 10, "Avocado": 5, "Eggs": 4,
    "Brown Rice": 3, "Yogurt": 5, "Sweet Potato": 3, "Broccoli": 4, "Tomatoes": 3,
    "Walnuts": 8, "Almonds": 7, "Greek Yogurt": 6, "Chickpeas": 2, "Black Beans": 2,
    "Quinoa": 5, "Tofu": 5, "Tempeh": 6, "Oranges": 4, "Bananas": 3, "Dates": 4,
    "Pomegranate": 5, "Kale": 5, "Garlic": 2, "Ginger": 2
}

UAE_STORES = [
    "Carrefour Dubai Marina",
    "Spinneys Abu Dhabi",
    "Lulu Hypermarket Dubai",
    "Waitrose Dubai Mall",
    "Union Coop Dubai",
]

UAE_ENVIRONMENT = {
    "availability": {"healthy": 0.72, "processed": 0.91},
    "price_sensitivity": 0.60,
    "convenience_bias": 0.80
}

FOOD_LIBRARY = {
    "Salmon": {
        "category": "fatty_fish",
        "key_nutrients": ["Omega-3 EPA/DHA", "Protein", "Vitamin D", "Selenium"],
        "benefits": [
            "supports muscle recovery and protein synthesis",
            "helps lower inflammation load over time",
            "supports cardiovascular and brain health",
        ],
        "good_for": ["pain", "fitness", "glucose_control", "inflammation"],
        "watch_for": [],
        "body_effect": "Its omega-3 fats can help reduce inflammatory signaling and support recovery, which matters for muscle soreness, joint discomfort, and long-term heart health."
    },
    "Sardines": {
        "category": "fatty_fish",
        "key_nutrients": ["Omega-3 EPA/DHA", "Protein", "Calcium", "Vitamin B12"],
        "benefits": [
            "supports bone and muscle function",
            "helps with recovery and anti-inflammatory balance",
            "supports nerve health and energy metabolism",
        ],
        "good_for": ["pain", "fitness", "glucose_control"],
        "watch_for": [],
        "body_effect": "Sardines are dense in protein and omega-3s, making them useful for recovery, tissue repair, and reducing inflammatory stress."
    },
    "Mackerel": {
        "category": "fatty_fish",
        "key_nutrients": ["Omega-3 EPA/DHA", "Protein", "Vitamin D"],
        "benefits": [
            "supports recovery from high strain",
            "can help reduce chronic inflammation burden",
            "supports long-term cardiometabolic health",
        ],
        "good_for": ["pain", "fitness", "glucose_control"],
        "watch_for": [],
        "body_effect": "Mackerel combines high-quality protein with fats that may help lower inflammation and support recovery after physical stress."
    },
    "Oats": {
        "category": "whole_grain",
        "key_nutrients": ["Beta-glucan fiber", "Magnesium", "Complex carbohydrates"],
        "benefits": [
            "supports steady glucose release",
            "helps lower LDL cholesterol",
            "supports satiety and appetite control",
        ],
        "good_for": ["glucose_control", "fat_loss", "diabetes_risk"],
        "watch_for": [],
        "body_effect": "The beta-glucan fiber in oats slows digestion and can reduce glucose spikes, which is especially valuable when someone is trending toward insulin resistance."
    },
    "Blueberries": {
        "category": "berry",
        "key_nutrients": ["Polyphenols", "Vitamin C", "Fiber"],
        "benefits": [
            "helps protect cells from oxidative stress",
            "supports vascular health",
            "can support long-term brain health",
        ],
        "good_for": ["pain", "glucose_control", "inflammation"],
        "watch_for": [],
        "body_effect": "Blueberries contain polyphenols that may help reduce oxidative stress and support blood vessel health over time."
    },
    "Lentils": {
        "category": "legume",
        "key_nutrients": ["Fiber", "Plant protein", "Folate", "Iron"],
        "benefits": [
            "supports steady blood sugar response",
            "improves fullness and appetite control",
            "supports gut microbiome health",
        ],
        "good_for": ["glucose_control", "fat_loss", "diabetes_risk"],
        "watch_for": [],
        "body_effect": "Lentils digest slowly, helping flatten glucose rises and improving fullness, which makes them useful for long-term glucose control and weight management."
    },
    "Spinach": {
        "category": "leafy_green",
        "key_nutrients": ["Magnesium", "Folate", "Nitrates", "Vitamin K"],
        "benefits": [
            "supports muscle and nerve function",
            "supports blood flow and oxygen use",
            "adds nutrient density with minimal glucose load",
        ],
        "good_for": ["fitness", "glucose_control", "pain"],
        "watch_for": [],
        "body_effect": "Spinach provides magnesium and nitrates, which can support muscle function, circulation, and overall metabolic health."
    },
    "Chicken Breast": {
        "category": "lean_protein",
        "key_nutrients": ["Protein", "Niacin", "Vitamin B6"],
        "benefits": [
            "supports lean muscle maintenance",
            "helps recovery after activity",
            "supports satiety without much glucose load",
        ],
        "good_for": ["fitness", "fat_loss"],
        "watch_for": [],
        "body_effect": "Chicken breast provides a concentrated protein source that helps preserve lean mass and improves recovery without adding much glycemic load."
    },
    "Avocado": {
        "category": "healthy_fat",
        "key_nutrients": ["Monounsaturated fats", "Fiber", "Potassium"],
        "benefits": [
            "supports satiety and appetite control",
            "supports heart health",
            "may improve meal glycemic response when paired with carbs",
        ],
        "good_for": ["fat_loss", "glucose_control", "pain"],
        "watch_for": [],
        "body_effect": "Avocado slows digestion and can reduce post-meal glucose volatility, while also supporting cardiovascular health."
    },
    "Eggs": {
        "category": "protein",
        "key_nutrients": ["Protein", "Choline", "Vitamin B12", "Selenium"],
        "benefits": [
            "supports muscle repair",
            "supports brain and nerve function",
            "helps satiety and appetite control",
        ],
        "good_for": ["fitness", "fat_loss"],
        "watch_for": [],
        "body_effect": "Eggs deliver a compact mix of high-quality protein and micronutrients that support recovery and satiety."
    },
    "Brown Rice": {
        "category": "whole_grain",
        "key_nutrients": ["Complex carbohydrates", "Manganese", "Fiber"],
        "benefits": [
            "provides sustained energy",
            "supports training fuel",
            "offers a steadier glucose response than more refined grains",
        ],
        "good_for": ["fitness", "energy"],
        "watch_for": ["diabetes_risk"],
        "body_effect": "Brown rice can support energy needs well, but portion size matters when glucose control is a concern."
    },
    "Yogurt": {
        "category": "fermented_dairy",
        "key_nutrients": ["Protein", "Calcium", "Probiotics"],
        "benefits": [
            "supports gut health",
            "supports bone health",
            "helps satiety and recovery",
        ],
        "good_for": ["fitness", "glucose_control"],
        "watch_for": [],
        "body_effect": "Unsweetened yogurt can support gut and metabolic health while providing protein and calcium."
    },
    "Greek Yogurt": {
        "category": "fermented_dairy",
        "key_nutrients": ["Protein", "Calcium", "Probiotics"],
        "benefits": [
            "supports muscle repair",
            "supports gut balance",
            "helps appetite control",
        ],
        "good_for": ["fitness", "fat_loss", "glucose_control"],
        "watch_for": [],
        "body_effect": "Greek yogurt is particularly useful when higher protein intake is needed without much sugar."
    },
    "Sweet Potato": {
        "category": "root_veg",
        "key_nutrients": ["Beta-carotene", "Potassium", "Fiber"],
        "benefits": [
            "supports training fuel",
            "supports immune function",
            "offers more fiber and micronutrients than refined starches",
        ],
        "good_for": ["fitness", "energy"],
        "watch_for": ["diabetes_risk"],
        "body_effect": "Sweet potato can be a useful carb source for energy, but portioning matters for people with impaired glucose tolerance."
    },
    "Broccoli": {
        "category": "cruciferous",
        "key_nutrients": ["Vitamin C", "Sulforaphane precursors", "Fiber"],
        "benefits": [
            "supports antioxidant defense",
            "supports gut and metabolic health",
            "adds nutrients with very low glycemic load",
        ],
        "good_for": ["glucose_control", "fat_loss", "pain"],
        "watch_for": [],
        "body_effect": "Broccoli contributes fiber and plant compounds that support metabolic health and reduce dietary glycemic burden."
    },
    "Tomatoes": {
        "category": "fruit_veg",
        "key_nutrients": ["Lycopene", "Vitamin C", "Potassium"],
        "benefits": [
            "supports antioxidant defense",
            "supports cardiovascular health",
            "adds low-calorie nutrient density",
        ],
        "good_for": ["glucose_control", "pain"],
        "watch_for": [],
        "body_effect": "Tomatoes provide antioxidants like lycopene that support vascular and long-term cellular health."
    },
    "Walnuts": {
        "category": "nut",
        "key_nutrients": ["Omega-3 ALA", "Magnesium", "Polyphenols"],
        "benefits": [
            "supports heart health",
            "supports satiety",
            "can reduce overall diet inflammatory load",
        ],
        "good_for": ["pain", "fat_loss", "glucose_control"],
        "watch_for": [],
        "body_effect": "Walnuts add healthy fats and micronutrients that can support satiety, cardiometabolic health, and inflammatory balance."
    },
    "Almonds": {
        "category": "nut",
        "key_nutrients": ["Magnesium", "Vitamin E", "Healthy fats"],
        "benefits": [
            "supports glycemic stability",
            "supports satiety",
            "supports nerve and muscle function",
        ],
        "good_for": ["glucose_control", "fat_loss", "fitness"],
        "watch_for": [],
        "body_effect": "Almonds are helpful for improving meal satiety and can reduce the glycemic impact of mixed meals."
    },
    "Chickpeas": {
        "category": "legume",
        "key_nutrients": ["Fiber", "Plant protein", "Magnesium"],
        "benefits": [
            "supports blood sugar stability",
            "supports fullness",
            "supports gut health",
        ],
        "good_for": ["glucose_control", "fat_loss", "diabetes_risk"],
        "watch_for": [],
        "body_effect": "Chickpeas digest slowly and can support insulin sensitivity and appetite control when used in place of refined carbohydrates."
    },
    "Black Beans": {
        "category": "legume",
        "key_nutrients": ["Fiber", "Plant protein", "Polyphenols"],
        "benefits": [
            "supports a lower glycemic meal pattern",
            "supports gut health",
            "supports fullness and long-term metabolic balance",
        ],
        "good_for": ["glucose_control", "diabetes_risk"],
        "watch_for": [],
        "body_effect": "Black beans help slow carbohydrate absorption and can support better long-term glucose regulation."
    },
    "Quinoa": {
        "category": "whole_grain",
        "key_nutrients": ["Protein", "Magnesium", "Fiber"],
        "benefits": [
            "supports energy and recovery",
            "offers more protein than many grains",
            "supports satiety",
        ],
        "good_for": ["fitness", "fat_loss"],
        "watch_for": [],
        "body_effect": "Quinoa can support energy and satiety while giving a more balanced nutrient profile than many refined grain options."
    },
    "Tofu": {
        "category": "plant_protein",
        "key_nutrients": ["Protein", "Calcium", "Isoflavones"],
        "benefits": [
            "supports muscle maintenance",
            "supports lower saturated fat eating patterns",
            "works well in glucose-aware meal structures",
        ],
        "good_for": ["fitness", "glucose_control", "fat_loss"],
        "watch_for": [],
        "body_effect": "Tofu offers a lower-saturated-fat protein source that can support recovery and cardiometabolic health."
    },
    "Tempeh": {
        "category": "plant_protein",
        "key_nutrients": ["Protein", "Fiber", "Fermentation-derived compounds"],
        "benefits": [
            "supports gut health",
            "supports satiety and muscle maintenance",
            "fits glucose-conscious eating patterns",
        ],
        "good_for": ["glucose_control", "fat_loss", "fitness"],
        "watch_for": [],
        "body_effect": "Tempeh combines protein and fiber, which makes it useful for satiety and more stable glucose response."
    },
    "Oranges": {
        "category": "fruit",
        "key_nutrients": ["Vitamin C", "Flavonoids", "Fiber"],
        "benefits": [
            "supports immune function",
            "supports collagen formation and tissue repair",
            "better option than juice because of fiber",
        ],
        "good_for": ["pain", "recovery"],
        "watch_for": ["diabetes_risk"],
        "body_effect": "Whole oranges provide vitamin C and fiber, which is much gentler metabolically than drinking orange juice."
    },
    "Bananas": {
        "category": "fruit",
        "key_nutrients": ["Potassium", "Vitamin B6", "Carbohydrates"],
        "benefits": [
            "supports muscle and nerve function",
            "supports training fuel and recovery",
            "can help replenish after activity",
        ],
        "good_for": ["fitness", "muscle_support"],
        "watch_for": ["diabetes_risk"],
        "body_effect": "Bananas can help support muscle function and recovery, especially after exercise, but timing and portion matter if glucose control is a concern."
    },
    "Dates": {
        "category": "fruit",
        "key_nutrients": ["Carbohydrates", "Potassium", "Polyphenols"],
        "benefits": [
            "rapid energy source",
            "supports quick fuel around training",
            "contains some beneficial plant compounds",
        ],
        "good_for": ["energy", "fitness"],
        "watch_for": ["diabetes_risk"],
        "body_effect": "Dates provide quick fuel and can be useful around exercise, but they are not ideal as a frequent free-snacking fruit for someone trending toward diabetes."
    },
    "Pomegranate": {
        "category": "fruit",
        "key_nutrients": ["Polyphenols", "Vitamin C", "Potassium"],
        "benefits": [
            "supports antioxidant defense",
            "supports vascular function",
            "may support recovery from oxidative stress",
        ],
        "good_for": ["pain", "recovery", "glucose_control"],
        "watch_for": [],
        "body_effect": "Pomegranate provides antioxidants that may support vascular health and help counter oxidative stress."
    },
    "Kale": {
        "category": "leafy_green",
        "key_nutrients": ["Vitamin K", "Vitamin C", "Folate"],
        "benefits": [
            "supports overall nutrient density",
            "supports low-glycemic eating",
            "supports antioxidant defense",
        ],
        "good_for": ["glucose_control", "fat_loss", "pain"],
        "watch_for": [],
        "body_effect": "Kale adds high nutrient density with minimal glycemic burden, which helps long-term metabolic quality."
    },
    "Garlic": {
        "category": "aromatic",
        "key_nutrients": ["Sulfur compounds", "Manganese", "Vitamin B6"],
        "benefits": [
            "supports vascular health",
            "supports dietary anti-inflammatory patterns",
            "adds health value without glycemic cost",
        ],
        "good_for": ["pain", "glucose_control"],
        "watch_for": [],
        "body_effect": "Garlic contributes compounds that may support vascular and inflammatory balance over time."
    },
    "Ginger": {
        "category": "aromatic",
        "key_nutrients": ["Gingerols", "Antioxidant compounds"],
        "benefits": [
            "supports anti-inflammatory eating patterns",
            "may help with digestive comfort",
            "supports recovery-oriented meal patterns",
        ],
        "good_for": ["pain", "recovery"],
        "watch_for": [],
        "body_effect": "Ginger contains compounds associated with lower inflammatory burden and can be useful in recovery-supportive eating patterns."
    },
}

# =========================================================
# SESSION STATE
# =========================================================
if "users" not in st.session_state:
    st.session_state["users"] = []
if "history" not in st.session_state:
    st.session_state["history"] = []

# =========================================================
# WEARABLE CONNECTORS
# =========================================================
class WearableProvider:
    def fetch_data(self, user_id=None, days=7):
        raise NotImplementedError

class SimulatedWearableProvider(WearableProvider):
    def fetch_data(self, user_id=None, days=7):
        seed = user_id if user_id is not None else 42
        np.random.seed(seed)
        rows = []
        for i in range(days):
            rows.append({
                "date": datetime.date.today() - datetime.timedelta(days=i),
                "hrv": np.random.randint(40, 100),
                "resting_hr": np.random.randint(50, 75),
                "sleep_hours": round(np.random.uniform(4.5, 8.5), 2),
                "recovery": np.random.randint(30, 95),
                "strain": round(np.random.uniform(5, 18), 1),
                "steps": np.random.randint(3000, 14000)
            })
        return pd.DataFrame(rows)

class WhoopProvider(WearableProvider):
    def __init__(self, access_token):
        self.access_token = access_token

    def fetch_data(self, user_id=None, days=7):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        rows = []

        try:
            # Placeholder structure. Replace mapping with actual WHOOP fields after app registration.
            # Keeping robust fallback so app remains usable.
            for i in range(days):
                rows.append({
                    "date": datetime.date.today() - datetime.timedelta(days=i),
                    "hrv": 60,
                    "resting_hr": 58,
                    "sleep_hours": 7.1,
                    "recovery": 72,
                    "strain": 11.4,
                    "steps": 8500
                })
            return pd.DataFrame(rows)
        except Exception:
            return SimulatedWearableProvider().fetch_data(user_id=user_id, days=days)

class FitbitProvider(WearableProvider):
    def __init__(self, access_token):
        self.access_token = access_token

    def fetch_data(self, user_id=None, days=7):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        rows = []

        try:
            for i in range(days):
                rows.append({
                    "date": datetime.date.today() - datetime.timedelta(days=i),
                    "hrv": 55,
                    "resting_hr": 60,
                    "sleep_hours": 6.8,
                    "recovery": 68,
                    "strain": 10.2,
                    "steps": 9200
                })
            return pd.DataFrame(rows)
        except Exception:
            return SimulatedWearableProvider().fetch_data(user_id=user_id, days=days)

def aggregate_wearable(df):
    return {
        "avg_hrv": int(df["hrv"].mean()) if "hrv" in df else None,
        "avg_sleep": round(df["sleep_hours"].mean(), 2) if "sleep_hours" in df else None,
        "avg_strain": round(df["strain"].mean(), 1) if "strain" in df else None,
        "avg_recovery": int(df["recovery"].mean()) if "recovery" in df else None,
        "avg_resting_hr": int(df["resting_hr"].mean()) if "resting_hr" in df else None,
        "avg_steps": int(df["steps"].mean()) if "steps" in df else None
    }

# =========================================================
# HEALTH / METABOLIC LOGIC
# =========================================================
def calculate_bmi(w, h):
    return round(w / (h ** 2), 1)

def estimate_metabolic_status(user):
    score = 0
    reasons = []

    if user.get("bmi", 0) >= 28:
        score += 2
        reasons.append("higher BMI raises long-term metabolic risk")
    elif user.get("bmi", 0) >= 25:
        score += 1
        reasons.append("BMI is above the lean range")

    if user.get("sleep_hours", 10) < 6:
        score += 2
        reasons.append("short sleep worsens glucose regulation and appetite control")
    elif user.get("sleep_hours", 10) < 7:
        score += 1
        reasons.append("sleep is slightly below an ideal recovery range")

    if user.get("steps", 10000) < 6000:
        score += 2
        reasons.append("low movement reduces insulin sensitivity")
    elif user.get("steps", 10000) < 8000:
        score += 1
        reasons.append("daily movement could be higher for metabolic protection")

    if user.get("recovery", 100) < 50:
        score += 1
        reasons.append("poor recovery may reflect elevated physiological stress")

    if user.get("strain", 0) > 15 and user.get("sleep_hours", 8) < 6:
        score += 1
        reasons.append("high strain with low sleep increases recovery debt")

    if score >= 5:
        level = "high"
    elif score >= 3:
        level = "moderate"
    else:
        level = "low"

    return {
        "risk_level": level,
        "risk_score": score,
        "reasons": reasons
    }

def interpret_health(user):
    messages = []

    if user.get("sleep_hours") is not None and user["sleep_hours"] < 6:
        messages.append("Low sleep duration can increase cravings, reduce recovery quality, and worsen glucose control over time.")

    if user.get("recovery") is not None and user["recovery"] < 50:
        messages.append("Low recovery suggests elevated physiological stress and lower resilience to training and daily demands.")

    if user.get("hrv") is not None and user["hrv"] < 50:
        messages.append("Lower HRV may reflect higher stress load or weaker recovery, which can affect long-term cardiovascular and metabolic balance.")

    if user.get("bmi") is not None and user["bmi"] > 27:
        messages.append("Your BMI suggests elevated metabolic risk, especially if combined with low movement and short sleep.")

    if user.get("steps") is not None and user["steps"] < 6000:
        messages.append("Low daily movement can reduce insulin sensitivity and long-term cardiovascular fitness.")

    return messages

def disease_risk(user):
    risks = []
    metabolic = estimate_metabolic_status(user)

    if user.get("sleep_hours", 10) < 6:
        risks.append("Fatigue, poorer appetite control, and metabolic imbalance risk")
    if user.get("bmi", 0) > 28:
        risks.append("Type 2 diabetes and cardiometabolic disease risk")
    if user.get("strain", 0) > 15:
        risks.append("Accumulated physiological stress and inflammation risk")
    if metabolic["risk_level"] == "high":
        risks.append("Your overall pattern suggests a stronger need for glucose-aware, anti-inflammatory eating")

    return risks

# =========================================================
# SUPPLY CHAIN / NUTRIENT INTEGRITY
# =========================================================
def supply_profile_for_food(food):
    lib = FOOD_LIBRARY.get(food, {})
    category = lib.get("category", "")

    # rough synthetic base nutrient integrity model by food type
    if category in ["berry", "leafy_green", "fruit", "cruciferous"]:
        return {
            "Vitamin C": np.random.uniform(55, 100),
            "Polyphenols": np.random.uniform(60, 120),
            "Protein": np.random.uniform(1, 6),
            "Fiber": np.random.uniform(2, 10),
            "Omega-3": np.random.uniform(0, 2),
            "Magnesium": np.random.uniform(20, 90),
        }
    if category in ["fatty_fish"]:
        return {
            "Vitamin C": np.random.uniform(0, 8),
            "Polyphenols": np.random.uniform(0, 10),
            "Protein": np.random.uniform(18, 30),
            "Fiber": np.random.uniform(0, 1),
            "Omega-3": np.random.uniform(1.2, 3.5),
            "Magnesium": np.random.uniform(20, 60),
        }
    if category in ["legume", "plant_protein"]:
        return {
            "Vitamin C": np.random.uniform(0, 10),
            "Polyphenols": np.random.uniform(10, 40),
            "Protein": np.random.uniform(10, 22),
            "Fiber": np.random.uniform(6, 16),
            "Omega-3": np.random.uniform(0, 1),
            "Magnesium": np.random.uniform(40, 120),
        }
    if category in ["whole_grain", "root_veg"]:
        return {
            "Vitamin C": np.random.uniform(0, 30),
            "Polyphenols": np.random.uniform(5, 25),
            "Protein": np.random.uniform(3, 10),
            "Fiber": np.random.uniform(2, 9),
            "Omega-3": np.random.uniform(0, 0.4),
            "Magnesium": np.random.uniform(30, 100),
        }
    if category in ["nut", "healthy_fat"]:
        return {
            "Vitamin C": np.random.uniform(0, 15),
            "Polyphenols": np.random.uniform(20, 60),
            "Protein": np.random.uniform(4, 12),
            "Fiber": np.random.uniform(4, 12),
            "Omega-3": np.random.uniform(0, 2.5),
            "Magnesium": np.random.uniform(50, 150),
        }
    return {
        "Vitamin C": np.random.uniform(5, 40),
        "Polyphenols": np.random.uniform(10, 50),
        "Protein": np.random.uniform(4, 20),
        "Fiber": np.random.uniform(1, 8),
        "Omega-3": np.random.uniform(0, 1),
        "Magnesium": np.random.uniform(20, 80),
    }

def simulate_supply(food):
    seed = int(hashlib.md5(food.encode()).hexdigest(), 16) % 10**6
    np.random.seed(seed)

    nutrients = supply_profile_for_food(food)

    stage_templates = [
        {"Stage": "Farm", "TempC": np.random.uniform(18, 38), "Humidity": np.random.uniform(35, 85), "Days": np.random.uniform(10, 40), "Event": "growth and field exposure"},
        {"Stage": "Harvest", "TempC": np.random.uniform(16, 34), "Humidity": np.random.uniform(30, 70), "Days": np.random.uniform(0.3, 1.0), "Event": "harvest handling and field-to-pack transition"},
        {"Stage": "Storage", "TempC": np.random.uniform(1, 12), "Humidity": np.random.uniform(45, 90), "Days": np.random.uniform(1, 6), "Event": "cold or dry storage conditions"},
        {"Stage": "Transport", "TempC": np.random.uniform(2, 18), "Humidity": np.random.uniform(40, 85), "Days": np.random.uniform(0.5, 4), "Event": "movement through cold chain or freight route"},
        {"Stage": "Retail", "TempC": np.random.uniform(3, 14), "Humidity": np.random.uniform(35, 75), "Days": np.random.uniform(1, 5), "Event": "shelf and display exposure before purchase"},
        {"Stage": "Home", "TempC": np.random.uniform(3, 25), "Humidity": np.random.uniform(30, 70), "Days": np.random.uniform(0.5, 4), "Event": "consumer storage and preparation window"},
    ]

    rows = []
    for stage in stage_templates:
        temp = stage["TempC"]
        days = stage["Days"]

        # decay model varies slightly by nutrient sensitivity
        decay_factors = {
            "Vitamin C": np.exp(-0.060 * days * (temp / 20)),
            "Polyphenols": np.exp(-0.030 * days * (temp / 22)),
            "Protein": np.exp(-0.008 * days * (temp / 25)),
            "Fiber": np.exp(-0.002 * days * (temp / 25)),
            "Omega-3": np.exp(-0.020 * days * (temp / 20)),
            "Magnesium": np.exp(-0.001 * days * (temp / 25)),
        }

        for nutrient in nutrients:
            nutrients[nutrient] *= decay_factors.get(nutrient, 0.98)

        row = {
            "Stage": stage["Stage"],
            "Event": stage["Event"],
            "TempC": round(stage["TempC"], 1),
            "Humidity": round(stage["Humidity"], 1),
            "Days": round(stage["Days"], 1),
        }
        row.update({k: round(v, 2) for k, v in nutrients.items()})
        rows.append(row)

    return pd.DataFrame(rows)

def explain_supply_chain(df, food):
    explanations = []
    for _, row in df.iterrows():
        stage = row["Stage"]
        event = row["Event"]
        stage_notes = []

        if row["TempC"] > 20:
            stage_notes.append("higher temperature likely increased nutrient degradation pressure")
        elif row["TempC"] < 8:
            stage_notes.append("cooler conditions helped preserve sensitive nutrients")

        if row["Days"] > 3:
            stage_notes.append("longer holding time increased cumulative nutrient loss")
        else:
            stage_notes.append("shorter duration helped maintain food quality")

        if row["Vitamin C"] < 15:
            vc_state = "very limited vitamin C remains at this stage"
        elif row["Vitamin C"] < 40:
            vc_state = "vitamin C is meaningfully reduced"
        else:
            vc_state = "vitamin C remains relatively well preserved"

        if row["Protein"] > 15:
            protein_state = "protein integrity remains strong"
        elif row["Protein"] > 7:
            protein_state = "moderate protein value remains"
        else:
            protein_state = "this food is not a major protein source at this point"

        explanations.append(
            f"**{stage}**: During {event}, the food moved through about **{row['Days']} days** at roughly **{row['TempC']}°C** and **{row['Humidity']}% humidity**. "
            f"At this point, {vc_state}, and {protein_state}. "
            f"The overall condition suggests that {'; '.join(stage_notes)}."
        )
    return explanations

def final_nutrient_gain(df, food):
    final_row = df.iloc[-1].to_dict()
    lib = FOOD_LIBRARY.get(food, {})
    return {
        "food": food,
        "key_nutrients": lib.get("key_nutrients", []),
        "body_effect": lib.get("body_effect", ""),
        "final_values": {
            "Vitamin C": final_row.get("Vitamin C", 0),
            "Protein": final_row.get("Protein", 0),
            "Polyphenols": final_row.get("Polyphenols", 0),
            "Fiber": final_row.get("Fiber", 0),
            "Omega-3": final_row.get("Omega-3", 0),
            "Magnesium": final_row.get("Magnesium", 0),
        }
    }

# =========================================================
# BEHAVIOR ENGINE
# =========================================================
def extract_behavior_patterns(history):
    if history.empty:
        return {"accept_rate": 0, "top_foods": []}

    accept_rate = len(history[history["decision"] == "accepted"]) / len(history)
    food_counts = history["food_name"].value_counts().to_dict()

    return {
        "accept_rate": round(accept_rate, 2),
        "top_foods": list(food_counts.keys())[:3]
    }

def behavior_stage(patterns):
    if patterns["accept_rate"] < 0.3:
        return "resistant"
    elif patterns["accept_rate"] < 0.6:
        return "transitional"
    return "optimized"

ADJACENT_FOODS = {
    "Chicken Breast": ["Salmon", "Greek Yogurt"],
    "Brown Rice": ["Oats", "Quinoa"],
    "Yogurt": ["Blueberries", "Walnuts"],
    "Oats": ["Lentils", "Chickpeas"],
    "Eggs": ["Spinach", "Avocado"],
}

def gradual_recommendation(patterns):
    stage = behavior_stage(patterns)

    if not patterns["top_foods"]:
        return ["Eggs", "Greek Yogurt", "Oats"]

    base = patterns["top_foods"][0]

    if stage == "resistant":
        return ADJACENT_FOODS.get(base, [base])

    if stage == "transitional":
        return list(set(ADJACENT_FOODS.get(base, []) + ["Spinach", "Avocado", "Blueberries"]))

    return ["Salmon", "Spinach", "Blueberries", "Lentils", "Greek Yogurt"]

def explain_behavior(stage):
    if stage == "resistant":
        return "We are making small, realistic upgrades based on what you already accept, so your next choices feel achievable rather than disruptive."
    if stage == "transitional":
        return "You are improving your food pattern, so the system is widening your options toward foods with better long-term metabolic and recovery value."
    return "Your habits are strong enough to focus on higher-quality optimization for long-term health, recovery, and metabolic resilience."

# =========================================================
# RECOMMENDATION ENGINE
# =========================================================
def food_fit_score(food, user):
    lib = FOOD_LIBRARY.get(food, {})
    score = 50

    if user.get("goal") == "fitness" and "fitness" in lib.get("good_for", []):
        score += 18
    if user.get("goal") == "fat_loss" and "fat_loss" in lib.get("good_for", []):
        score += 18
    if user.get("goal") == "glucose_control" and "glucose_control" in lib.get("good_for", []):
        score += 20

    metabolic = estimate_metabolic_status(user)
    if metabolic["risk_level"] in ["moderate", "high"] and "diabetes_risk" in lib.get("good_for", []):
        score += 18
    if user.get("strain", 0) > 13 and "recovery" in lib.get("good_for", []):
        score += 10
    if user.get("strain", 0) > 13 and "fitness" in lib.get("good_for", []):
        score += 7
    if user.get("sleep_hours", 8) < 6 and "glucose_control" in lib.get("good_for", []):
        score += 8
    if user.get("bmi", 0) > 27 and "fat_loss" in lib.get("good_for", []):
        score += 8
    if user.get("bmi", 0) > 27 and "glucose_control" in lib.get("good_for", []):
        score += 10

    if metabolic["risk_level"] in ["moderate", "high"] and "diabetes_risk" in lib.get("watch_for", []):
        score -= 15

    return score

def generate_precise_food_recommendations(user, history_df=None, top_n=8):
    rows = []
    metabolic = estimate_metabolic_status(user)

    for food in FOODS:
        lib = FOOD_LIBRARY.get(food, {})
        supply_df = simulate_supply(food)
        nutrient_state = final_nutrient_gain(supply_df, food)
        fit = food_fit_score(food, user)

        final_vals = nutrient_state["final_values"]
        quality_bonus = min(15, (final_vals.get("Protein", 0) / 2) + (final_vals.get("Fiber", 0) / 2))
        if final_vals.get("Omega-3", 0) > 1:
            quality_bonus += 6
        if final_vals.get("Vitamin C", 0) > 25:
            quality_bonus += 4
        if final_vals.get("Polyphenols", 0) > 40:
            quality_bonus += 4

        total_score = round(fit + quality_bonus, 1)

        long_term_gain = []
        if "glucose_control" in lib.get("good_for", []):
            long_term_gain.append("improve blood sugar stability and reduce repeated glucose spikes")
        if "fat_loss" in lib.get("good_for", []):
            long_term_gain.append("support fullness and make long-term weight management easier")
        if "fitness" in lib.get("good_for", []):
            long_term_gain.append("support muscle repair, training recovery, and lean mass maintenance")
        if "pain" in lib.get("good_for", []):
            long_term_gain.append("support a lower-inflammatory eating pattern that may help with persistent aches")
        if "recovery" in lib.get("good_for", []):
            long_term_gain.append("improve resilience and recovery after periods of stress or exertion")

        why = []
        if user.get("goal") == "glucose_control" and "glucose_control" in lib.get("good_for", []):
            why.append("it fits your glucose-control goal")
        if user.get("goal") == "fat_loss" and "fat_loss" in lib.get("good_for", []):
            why.append("it supports satiety and lower-energy-density eating")
        if user.get("goal") == "fitness" and "fitness" in lib.get("good_for", []):
            why.append("it supports recovery and muscle maintenance")
        if metabolic["risk_level"] in ["moderate", "high"] and "diabetes_risk" in lib.get("good_for", []):
            why.append("your data suggests you would benefit from slower-digesting, higher-fiber foods")
        if user.get("strain", 0) > 13 and ("recovery" in lib.get("good_for", []) or "pain" in lib.get("good_for", [])):
            why.append("your recent strain and recovery pattern suggests extra anti-inflammatory support would help")

        avoid_reason = None
        if metabolic["risk_level"] in ["moderate", "high"] and "diabetes_risk" in lib.get("watch_for", []):
            avoid_reason = "This food is not automatically bad, but portion size, timing, and frequency matter more because your data suggests rising metabolic risk."

        rows.append({
            "food": food,
            "score": total_score,
            "key_nutrients": ", ".join(lib.get("key_nutrients", [])),
            "body_effect": lib.get("body_effect", ""),
            "why_suggested": " ".join(why) if why else "it is a broadly supportive whole-food option",
            "long_term_gain": "; ".join(long_term_gain) if long_term_gain else "supports overall diet quality",
            "watch_out": avoid_reason,
            "protein": round(final_vals.get("Protein", 0), 1),
            "fiber": round(final_vals.get("Fiber", 0), 1),
            "omega3": round(final_vals.get("Omega-3", 0), 2),
            "vitamin_c": round(final_vals.get("Vitamin C", 0), 1),
            "polyphenols": round(final_vals.get("Polyphenols", 0), 1),
        })

    rec_df = pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)

    avoid_df = rec_df[rec_df["watch_out"].notna()].sort_values("score", ascending=True).head(6)
    recommend_df = rec_df.head(top_n)

    return recommend_df, avoid_df

def generate_store_options(food_list):
    np.random.seed(123)
    rows = []
    for food in food_list:
        for store in UAE_STORES:
            quality = np.random.choice(["High integrity", "Standard", "Variable"], p=[0.45, 0.40, 0.15])
            price = PRICE_MAP.get(food, 5) + np.random.randint(-1, 4)
            stock = np.random.choice(["In stock", "Low stock"], p=[0.8, 0.2])

            rows.append({
                "Food": food,
                "Store": store,
                "Quality": quality,
                "Stock": stock,
                "Price_AED": max(1, price)
            })
    return pd.DataFrame(rows)

# =========================================================
# DATA FUNCTIONS
# =========================================================
def get_wearable_provider(source, whoop_token=None, fitbit_token=None):
    if source == "WHOOP" and whoop_token:
        return WhoopProvider(whoop_token)
    if source == "Fitbit" and fitbit_token:
        return FitbitProvider(fitbit_token)
    return SimulatedWearableProvider()

def create_user(w, h, goal, wearable_source, whoop_token=None, fitbit_token=None):
    user_id = len(st.session_state["users"]) + 1
    provider = get_wearable_provider(wearable_source, whoop_token, fitbit_token)
    df = provider.fetch_data(user_id=user_id, days=7)
    m = aggregate_wearable(df)

    user = {
        "id": user_id,
        "weight_kg": w,
        "height_m": h,
        "bmi": calculate_bmi(w, h),
        "sleep_hours": m["avg_sleep"],
        "hrv": m["avg_hrv"],
        "recovery": m["avg_recovery"],
        "strain": m["avg_strain"],
        "resting_hr": m["avg_resting_hr"],
        "steps": m["avg_steps"],
        "goal": goal,
        "wearable_source": wearable_source
    }

    st.session_state["users"].append(user)
    st.session_state[f"wearable_data_{user_id}"] = df

def load_users():
    return pd.DataFrame(st.session_state["users"])

def save_decision(user_id, food, decision):
    st.session_state["history"].append({
        "user_id": user_id,
        "food_name": food,
        "decision": decision,
        "created_at": datetime.datetime.now()
    })

def load_history(user_id):
    df = pd.DataFrame(st.session_state["history"])
    if df.empty:
        return df
    return df[df["user_id"] == user_id]

# =========================================================
# SIDEBAR SETTINGS
# =========================================================
st.sidebar.title("System Settings")
wearable_source = st.sidebar.selectbox("Wearable source", ["Simulated", "WHOOP", "Fitbit"])

default_whoop = os.getenv("WHOOP_ACCESS_TOKEN", "")
default_fitbit = os.getenv("FITBIT_ACCESS_TOKEN", "")

whoop_token = ""
fitbit_token = ""

if wearable_source == "WHOOP":
    whoop_token = st.sidebar.text_input("WHOOP access token", value=default_whoop, type="password")
elif wearable_source == "Fitbit":
    fitbit_token = st.sidebar.text_input("Fitbit access token", value=default_fitbit, type="password")

page = st.sidebar.radio("Navigation", [
    "Create User",
    "Wearable Data",
    "Food Deep Dive",
    "Health Insights",
    "Behavior Engine",
    "Decision Engine",
    "Habit Tracker",
    "Precision Recommendations"
])

# =========================================================
# UI
# =========================================================
st.title("🥗 Food Intelligence System")

if page == "Create User":
    col1, col2, col3 = st.columns(3)
    with col1:
        w = st.number_input("Weight (kg)", 40.0, 150.0, 75.0)
    with col2:
        h = st.number_input("Height (m)", 1.4, 2.2, 1.75)
    with col3:
        goal = st.selectbox("Goal", ["fitness", "fat_loss", "glucose_control"])

    st.caption(f"Wearable source: {wearable_source}")

    if st.button("Save user"):
        create_user(w, h, goal, wearable_source, whoop_token, fitbit_token)
        st.success("User created and wearable snapshot stored.")

elif page == "Wearable Data":
    users = load_users()
    if users.empty:
        st.info("Create a user first.")
        st.stop()

    user_id = st.selectbox("User", users["id"])
    df = st.session_state.get(f"wearable_data_{user_id}")

    if df is None:
        provider = get_wearable_provider(wearable_source, whoop_token, fitbit_token)
        df = provider.fetch_data(user_id=user_id, days=7)
        st.session_state[f"wearable_data_{user_id}"] = df

    st.subheader("Recent wearable trend")
    st.dataframe(df, use_container_width=True)

    chart_cols = [c for c in ["hrv", "sleep_hours", "strain", "steps", "resting_hr", "recovery"] if c in df.columns]
    if chart_cols:
        st.line_chart(df.set_index("date")[chart_cols])

    agg = aggregate_wearable(df)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Avg sleep", agg["avg_sleep"])
    m2.metric("Avg HRV", agg["avg_hrv"])
    m3.metric("Avg recovery", agg["avg_recovery"])
    m4.metric("Avg steps", agg["avg_steps"])

elif page == "Food Deep Dive":
    food = st.selectbox("Food", FOODS)
    df = simulate_supply(food)

    st.subheader(f"{food}: farm-to-plate journey")
    st.dataframe(df, use_container_width=True)

    chart_df = df.set_index("Stage")[["Vitamin C", "Protein", "Fiber", "Omega-3", "Polyphenols", "Magnesium"]]
    st.line_chart(chart_df)

    st.subheader("Stage-by-stage interpretation")
    for line in explain_supply_chain(df, food):
        st.markdown(f"- {line}")

    nutrient_gain = final_nutrient_gain(df, food)

    st.subheader("What the consumer still stands to gain")
    st.write(f"**Key nutrients:** {', '.join(nutrient_gain['key_nutrients'])}")
    st.write(f"**Body effect:** {nutrient_gain['body_effect']}")

    final_vals = nutrient_gain["final_values"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Protein", final_vals["Protein"])
    c2.metric("Fiber", final_vals["Fiber"])
    c3.metric("Omega-3", final_vals["Omega-3"])

    c4, c5, c6 = st.columns(3)
    c4.metric("Vitamin C", final_vals["Vitamin C"])
    c5.metric("Polyphenols", final_vals["Polyphenols"])
    c6.metric("Magnesium", final_vals["Magnesium"])

elif page == "Health Insights":
    users = load_users()
    if users.empty:
        st.info("Create a user first.")
        st.stop()

    user_id = st.selectbox("User", users["id"])
    user = users[users["id"] == user_id].iloc[0].to_dict()

    st.subheader("Health interpretation")
    for msg in interpret_health(user):
        st.write(f"• {msg}")

    st.subheader("Risk flags")
    for r in disease_risk(user):
        st.write(f"⚠️ {r}")

    metabolic = estimate_metabolic_status(user)
    st.subheader("Metabolic direction")
    st.write(f"**Risk level:** {metabolic['risk_level'].upper()} | **Score:** {metabolic['risk_score']}")
    for reason in metabolic["reasons"]:
        st.write(f"- {reason}")

elif page == "Behavior Engine":
    users = load_users()
    if users.empty:
        st.info("Create a user first.")
        st.stop()

    user_id = st.selectbox("User", users["id"])
    history = load_history(user_id)

    patterns = extract_behavior_patterns(history)
    stage = behavior_stage(patterns)

    st.subheader("Behavior stage")
    st.write(stage.upper())
    st.write(explain_behavior(stage))

    recs = gradual_recommendation(patterns)
    st.subheader("Next best foods")
    for r in recs:
        st.write(f"→ {r}")

elif page == "Decision Engine":
    users = load_users()
    if users.empty:
        st.info("Create a user first.")
        st.stop()

    user_id = st.selectbox("User", users["id"])
    food = st.selectbox("Food", FOODS)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Accept"):
            save_decision(user_id, food, "accepted")
            st.success(f"Saved acceptance for {food}")
    with c2:
        if st.button("Reject"):
            save_decision(user_id, food, "rejected")
            st.warning(f"Saved rejection for {food}")

elif page == "Habit Tracker":
    users = load_users()
    if users.empty:
        st.info("Create a user first.")
        st.stop()

    user_id = st.selectbox("User", users["id"])
    history = load_history(user_id)

    if history.empty:
        st.info("No habit history yet.")
    else:
        st.dataframe(history, use_container_width=True)

        accepted = history[history["decision"] == "accepted"]["food_name"].value_counts()
        rejected = history[history["decision"] == "rejected"]["food_name"].value_counts()

        if not accepted.empty:
            st.subheader("Accepted foods")
            st.bar_chart(accepted)

        if not rejected.empty:
            st.subheader("Rejected foods")
            st.bar_chart(rejected)

elif page == "Precision Recommendations":
    users = load_users()
    if users.empty:
        st.info("Create a user first.")
        st.stop()

    user_id = st.selectbox("User", users["id"])
    user = users[users["id"] == user_id].iloc[0].to_dict()
    history = load_history(user_id)

    st.subheader("User context")
    u1, u2, u3, u4 = st.columns(4)
    u1.metric("BMI", user.get("bmi"))
    u2.metric("Sleep", user.get("sleep_hours"))
    u3.metric("Recovery", user.get("recovery"))
    u4.metric("Steps", user.get("steps"))

    recommend_df, avoid_df = generate_precise_food_recommendations(user, history_df=history, top_n=8)

    st.subheader("Best foods for this person now")
    for _, row in recommend_df.iterrows():
        with st.container(border=True):
            st.markdown(f"### {row['food']}")
            st.write(f"**Why suggested:** {row['why_suggested']}.")
            st.write(f"**How it affects the body:** {row['body_effect']}")
            st.write(f"**What they stand to gain long-term:** {row['long_term_gain']}.")
            st.write(f"**Key nutrients likely retained at consumption:** {row['key_nutrients']}")
            st.write(
                f"**Estimated final nutrient state:** "
                f"Protein {row['protein']} | Fiber {row['fiber']} | Omega-3 {row['omega3']} | "
                f"Vitamin C {row['vitamin_c']} | Polyphenols {row['polyphenols']}"
            )

    st.subheader("Foods to be more careful with")
    if avoid_df.empty:
        st.write("No special caution foods identified from current user pattern.")
    else:
        for _, row in avoid_df.iterrows():
            with st.container(border=True):
                st.markdown(f"### {row['food']}")
                st.write(f"**Why caution is needed:** {row['watch_out']}")
                st.write(f"**Context:** {row['body_effect']}")

    st.subheader("Suggested UAE store options for top foods")
    store_df = generate_store_options(recommend_df["food"].tolist())
    st.dataframe(store_df, use_container_width=True)
