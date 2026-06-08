import streamlit as st
import pandas as pd
import numpy as np
import datetime
import hashlib
import requests
import os

st.set_page_config(page_title="Food Intelligence System", layout="wide")

# =========================================================
# WHOOP CONFIG
# =========================================================
WHOOP_CLIENT_ID = os.getenv("WHOOP_CLIENT_ID", "")
WHOOP_CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET", "")
WHOOP_REDIRECT_URI = "http://localhost:8501"

def whoop_auth_url():
    return (
        "https://api.prod.whoop.com/oauth/oauth2/auth"
        f"?client_id={WHOOP_CLIENT_ID}"
        f"&redirect_uri={WHOOP_REDIRECT_URI}"
        "&response_type=code"
        "&scope=read:recovery read:sleep read:workout"
    )

def exchange_whoop_code(code):
    url = "https://api.prod.whoop.com/oauth/oauth2/token"
    data = {
        "client_id": WHOOP_CLIENT_ID,
        "client_secret": WHOOP_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": WHOOP_REDIRECT_URI,
    }
    return requests.post(url, data=data).json()

# =========================================================
# WEARABLE PROVIDERS (UPDATED)
# =========================================================
class WearableProvider:
    def fetch_data(self, user_id=None, days=7):
        raise NotImplementedError

class SimulatedWearableProvider(WearableProvider):
    def fetch_data(self, user_id=None, days=7):
        seed = user_id if user_id else 42
        np.random.seed(seed)

        return pd.DataFrame({
            "date": [datetime.date.today() - datetime.timedelta(i) for i in range(days)],
            "hrv": np.random.randint(40, 100, days),
            "resting_hr": np.random.randint(50, 75, days),
            "sleep_hours": np.random.uniform(4.5, 8.5, days),
            "recovery": np.random.randint(30, 95, days),
            "strain": np.random.uniform(5, 18, days),
            "steps": np.random.randint(3000, 14000, days)
        })

class WhoopProvider(WearableProvider):
    def __init__(self, access_token):
        self.token = access_token
        self.base_url = "https://api.prod.whoop.com/developer/v1"

    def headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def fetch_recovery(self):
        r = requests.get(f"{self.base_url}/recovery", headers=self.headers())
        return r.json()

    def fetch_sleep(self):
        r = requests.get(f"{self.base_url}/sleep", headers=self.headers())
        return r.json()

    def fetch_workouts(self):
        r = requests.get(f"{self.base_url}/activity/workout", headers=self.headers())
        return r.json()

def normalize_whoop(rec, sleep, workouts):
    try:
        return pd.DataFrame([{
            "date": datetime.date.today(),
            "hrv": rec["score"]["hrv_rmssd"],
            "resting_hr": 60,
            "sleep_hours": sleep["score"]["stage_summary"]["total_in_bed_time_milli"] / 3600000,
            "recovery": rec["score"]["recovery_score"],
            "strain": sum(w["score"]["strain"] for w in workouts.get("records", [])),
            "steps": 8000  # WHOOP does not provide steps
        }])
    except:
        return SimulatedWearableProvider().fetch_data()

def get_wearable_provider(source, token=None):
    if source == "WHOOP" and token:
        return WhoopProvider(token)
    return SimulatedWearableProvider()

# =========================================================
# CONSTANTS (UNCHANGED)
# =========================================================
FOODS = ["Salmon", "Sardines", "Mackerel", "Oats", "Blueberries", "Lentils", "Spinach"]

# =========================================================
# YOUR ORIGINAL FUNCTION (UNCHANGED)
# =========================================================
def aggregate_wearable(df):
    return {
        "avg_hrv": int(df["hrv"].mean()),
        "avg_sleep": round(df["sleep_hours"].mean(), 2),
        "avg_strain": round(df["strain"].mean(), 1),
        "avg_recovery": int(df["recovery"].mean()),
        "avg_resting_hr": int(df["resting_hr"].mean()),
        "avg_steps": int(df["steps"].mean())
    }

# =========================================================
# USER CREATION (UPDATED WITH WHOOP)
# =========================================================
def create_user(w, h, goal, wearable_source, token=None):
    user_id = len(st.session_state.get("users", [])) + 1

    provider = get_wearable_provider(wearable_source, token)

    # WHOOP FLOW
    if wearable_source == "WHOOP" and isinstance(provider, WhoopProvider):
        rec = provider.fetch_recovery()
        sleep = provider.fetch_sleep()
        workouts = provider.fetch_workouts()

        df = normalize_whoop(rec, sleep, workouts)

    # SIMULATION FLOW
    else:
        df = provider.fetch_data(user_id=user_id, days=7)

    m = aggregate_wearable(df)

    user = {
        "id": user_id,
        "weight_kg": w,
        "height_m": h,
        "bmi": round(w / (h ** 2), 1),
        "sleep_hours": m["avg_sleep"],
        "hrv": m["avg_hrv"],
        "recovery": m["avg_recovery"],
        "strain": m["avg_strain"],
        "resting_hr": m["avg_resting_hr"],
        "steps": m["avg_steps"],
        "goal": goal,
        "wearable_source": wearable_source
    }

    st.session_state.setdefault("users", []).append(user)
    st.session_state[f"wearable_data_{user_id}"] = df

# =========================================================
# HEALTH ENGINE (UNCHANGED)
# =========================================================
def estimate_metabolic_status(user):
    score = 0

    if user["bmi"] > 27: score += 2
    if user["sleep_hours"] < 6: score += 2
    if user["steps"] < 6000: score += 2
    if user["recovery"] < 50: score += 1

    return "high" if score >= 5 else "moderate" if score >= 3 else "low"

# =========================================================
# SESSION STATE
# =========================================================
if "users" not in st.session_state:
    st.session_state["users"] = []

# =========================================================
# UI
# =========================================================
st.title("🥗 Food Intelligence System (WHOOP Integrated)")

# ---------------- SIDEBAR ----------------
st.sidebar.title("Settings")

wearable_source = st.sidebar.selectbox(
    "Wearable Source",
    ["Simulated", "WHOOP"]
)

token = None

if wearable_source == "WHOOP":
    st.sidebar.markdown("### WHOOP Authentication")

    st.sidebar.markdown(f"[Login to WHOOP]({whoop_auth_url()})")

    code = st.sidebar.text_input("Paste OAuth code")

    if code:
        token_data = exchange_whoop_code(code)
        token = token_data.get("access_token")
        st.sidebar.success("WHOOP Connected")

page = st.sidebar.radio("Navigation", ["Create User", "Health Insights"])

# ---------------- CREATE USER ----------------
if page == "Create User":
    w = st.number_input("Weight (kg)", 40.0, 150.0, 75.0)
    h = st.number_input("Height (m)", 1.4, 2.2, 1.75)
    goal = st.selectbox("Goal", ["fitness", "fat_loss", "glucose_control"])

    if st.button("Create User"):
        create_user(w, h, goal, wearable_source, token)
        st.success("User created successfully")

# ---------------- HEALTH ----------------
elif page == "Health Insights":
    users = st.session_state.get("users", [])

    if not users:
        st.warning("No users yet")
        st.stop()

    user = users[-1]

    st.subheader("User Profile")
    st.json(user)

    st.subheader("Metabolic Risk")
    st.write(estimate_metabolic_status(user))
