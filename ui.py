import streamlit as st
import requests

API_URL = "https://render.com/docs/web-services#port-binding"

st.set_page_config(page_title="Churn Predictor", page_icon="📊")

st.title("📉 Customer Churn Prediction")

# --------------------------------------------------
# AUTH SECTION
# --------------------------------------------------
tab1, tab2 = st.tabs(["Login", "Register"])

with tab1:
    st.subheader("Login")
    login_user = st.text_input("Username")
    login_pass = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post(
            f"{API_URL}/login",
            json={"username": login_user, "password": login_pass}
        )
        if res.status_code == 200:
            st.session_state.token = res.json()["access_token"]
            st.success("Login successful")
        else:
            st.error("Invalid credentials")

with tab2:
    st.subheader("Register")
    reg_user = st.text_input("New Username")
    reg_pass = st.text_input("New Password", type="password")

    if st.button("Register"):
        res = requests.post(
            f"{API_URL}/register",
            json={"username": reg_user, "password": reg_pass}
        )
        if res.status_code == 200:
            st.success("Registered successfully")
        else:
            st.error("User already exists")

# --------------------------------------------------
# PREDICTION SECTION
# --------------------------------------------------
st.divider()
st.subheader("Churn Prediction")

if "token" not in st.session_state:
    st.warning("Login required to predict")
else:
    tenure = st.number_input("Tenure", 0)
    monthly = st.number_input("Monthly Charges", 0.0)
    total = st.number_input("Total Charges", 0.0)

    if st.button("Predict"):
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        payload = {
            "tenure": tenure,
            "monthly_charges": monthly,
            "total_charges": total
        }

        res = requests.post(
            f"{API_URL}/predict/auth",
            json=payload,
            headers=headers
        )

        if res.status_code == 200:
            data = res.json()
            st.success(f"Churn: {data['churn']}")
            st.info(f"Probability: {data['probability']}")
        else:
            st.error("Unauthorized or token expired")
