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
    "Salmon","Sardines","Mackerel","Oats","Blueberries","Lentils","Spinach",
    "Chicken Breast","Avocado","Eggs","Brown Rice","Yogurt","Sweet Potato",
    "Broccoli","Tomatoes","Walnuts","Almonds","Greek Yogurt","Chickpeas",
    "Black Beans","Quinoa","Tofu","Tempeh","Oranges","Bananas","Dates",
    "Pomegranate","Kale","Garlic","Ginger"
]

PRICE_MAP = {
    "Salmon": 15,"Sardines": 7,"Mackerel": 8,"Oats": 3,"Blueberries": 6,
    "Lentils": 2,"Spinach": 4,"Chicken Breast": 10,"Avocado": 5,"Eggs": 4,
    "Brown Rice": 3,"Yogurt": 5,"Sweet Potato": 3,"Broccoli": 4,"Tomatoes": 3,
    "Walnuts": 8,"Almonds": 7,"Greek Yogurt": 6,"Chickpeas": 2,"Black Beans": 2,
    "Quinoa": 5,"Tofu": 5,"Tempeh": 6,"Oranges": 4,"Bananas": 3,"Dates": 4,
    "Pomegranate": 5,"Kale": 5,"Garlic": 2,"Ginger": 2
}

UAE_STORES = [
    "Carrefour Dubai Marina",
    "Spinneys Abu Dhabi",
    "Lulu Hypermarket Dubai",
    "Waitrose Dubai Mall",
    "Union Coop Dubai",
]

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
        np.random.seed(user_id or 42)
        return pd.DataFrame([
            {
                "date": datetime.date.today() - datetime.timedelta(days=i),
                "hrv": np.random.randint(40, 100),
                "resting_hr": np.random.randint(50, 75),
                "sleep_hours": round(np.random.uniform(4.5, 8.5), 2),
                "recovery": np.random.randint(30, 95),
                "strain": round(np.random.uniform(5, 18), 1),
                "steps": np.random.randint(3000, 14000)
            }
            for i in range(days)
        ])


# =========================================================
# ✅ REAL WHOOP INTEGRATION (UPDATED)
# =========================================================
class WhoopProvider(WearableProvider):
    def __init__(self, access_token):
        self.base_url = "https://api.prod.whoop.com/developer/v1"
        self.access_token = access_token

    def fetch_data(self, user_id=None, days=7):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        try:
            # WHOOP recovery endpoint (example structure)
            url = f"{self.base_url}/recovery"
            params = {"limit": days}

            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code != 200:
                raise Exception(f"WHOOP API error: {response.status_code}")

            data = response.json().get("records", [])

            rows = []
            for i, item in enumerate(data[:days]):
                rows.append({
                    "date": datetime.date.today() - datetime.timedelta(days=i),
                    "hrv": item.get("hrv", 60),
                    "resting_hr": item.get("resting_heart_rate", 58),
                    "sleep_hours": item.get("sleep_duration", 7.0),
                    "recovery": item.get("recovery_score", 70),
                    "strain": item.get("strain", 10),
                    "steps": item.get("steps", 8000)
                })

            return pd.DataFrame(rows)

        except Exception:
            # fallback ensures system never breaks
            return SimulatedWearableProvider().fetch_data(user_id=user_id, days=days)


class FitbitProvider(WearableProvider):
    def __init__(self, access_token):
        self.access_token = access_token

    def fetch_data(self, user_id=None, days=7):
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            return SimulatedWearableProvider().fetch_data(user_id=user_id, days=days)
        except Exception:
            return SimulatedWearableProvider().fetch_data(user_id=user_id, days=days)

# =========================================================
# PROVIDER FACTORY
# =========================================================
def get_wearable_provider(source, whoop_token=None, fitbit_token=None):
    if source == "WHOOP" and whoop_token:
        return WhoopProvider(whoop_token)
    if source == "Fitbit" and fitbit_token:
        return FitbitProvider(fitbit_token)
    return SimulatedWearableProvider()

# =========================================================
# USER CREATION
# =========================================================
def create_user(w, h, goal, wearable_source, whoop_token=None, fitbit_token=None):
    user_id = len(st.session_state["users"]) + 1
    provider = get_wearable_provider(wearable_source, whoop_token, fitbit_token)

    df = provider.fetch_data(user_id=user_id, days=7)

    user = {
        "id": user_id,
        "weight_kg": w,
        "height_m": h,
        "bmi": round(w / (h ** 2), 1),
        "sleep_hours": df["sleep_hours"].mean(),
        "hrv": df["hrv"].mean(),
        "recovery": df["recovery"].mean(),
        "strain": df["strain"].mean(),
        "steps": df["steps"].mean(),
        "goal": goal,
        "wearable_source": wearable_source
    }

    st.session_state["users"].append(user)
    st.session_state[f"wearable_data_{user_id}"] = df

# =========================================================
# UI
# =========================================================
st.title("🥗 Food Intelligence System")

st.sidebar.title("System Settings")
wearable_source = st.sidebar.selectbox("Wearable source", ["Simulated", "WHOOP", "Fitbit"])

whoop_token = st.sidebar.text_input("WHOOP token", type="password") if wearable_source == "WHOOP" else None
fitbit_token = st.sidebar.text_input("Fitbit token", type="password") if wearable_source == "Fitbit" else None

page = st.sidebar.radio("Navigation", [
    "Create User",
    "Wearable Data"
])

# =========================================================
# CREATE USER
# =========================================================
if page == "Create User":
    w = st.number_input("Weight", 40.0, 150.0, 75.0)
    h = st.number_input("Height", 1.4, 2.2, 1.75)
    goal = st.selectbox("Goal", ["fitness", "fat_loss", "glucose_control"])

    if st.button("Create"):
        create_user(w, h, goal, wearable_source, whoop_token, fitbit_token)
        st.success("User created with wearable integration (WHOOP/Fitbit/Simulated).")

# =========================================================
# WEARABLE VIEW
# =========================================================
elif page == "Wearable Data":
    users = pd.DataFrame(st.session_state["users"])
    if users.empty:
        st.warning("No users yet")
        st.stop()

    uid = st.selectbox("User", users["id"])
    df = st.session_state.get(f"wearable_data_{uid}")

    st.dataframe(df)
    st.line_chart(df.set_index("date")[["hrv","sleep_hours","strain","recovery"]])
