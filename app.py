import streamlit as st
import streamlit as st
import subprocess
import sys

# === Add this to the beginning or a dedicated section of your Streamlit app ===
st.sidebar.title("Utilities")

if st.sidebar.button('Start FastAPI with Uvicorn'):
    with st.spinner("Starting FastAPI with Uvicorn..."):
        # Launches the FastAPI app using uvicorn in a subprocess
        # Note: This will block until the server is stopped unless you use Popen or threading
        try:
            process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.api.main:app", "--reload"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            st.sidebar.success("Uvicorn process started!")
            st.sidebar.write(f"PID: {process.pid}")
        except Exception as e:
            st.sidebar.error(f"Failed to start Uvicorn: {e}")

import requests

API_BASE = "http://localhost:8000"

st.title("FastAPI Route Tester")

# -- AUTH ROUTES --
st.header("Authentication")

with st.expander("Register"):
    reg_username = st.text_input("Username", key="reg_username")
    reg_password = st.text_input("Password", key="reg_password", type="password")
    if st.button("Register"):
        resp = requests.post(f"{API_BASE}/auth/register", json={
            "username": reg_username, "password": reg_password
        })
        st.write(resp.status_code, resp.json())

with st.expander("Login"):
    log_username = st.text_input("Username", key="log_username")
    log_password = st.text_input("Password", key="log_password", type="password")
    if st.button("Login"):
        resp = requests.post(f"{API_BASE}/auth/login", json={
            "username": log_username, "password": log_password
        })
        st.write(resp.status_code, resp.json())

with st.expander("Get Current User Info"):
    token = st.text_input("Access Token", key="me_token")
    if st.button("Fetch User Info"):
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{API_BASE}/auth/me", headers=headers)
        st.write(resp.status_code, resp.json())

# -- RESEARCH ROUTES --
st.header("Research")

with st.expander("Create Research"):
    title = st.text_input("max_iterations", key="research_title")
    description = st.text_area("Query", key="research_description")
    research_token = st.text_input("Access Token (required)", key="create_research_token")
    if st.button("Create Research"):
        headers = {"Authorization": f"Bearer {research_token}"}
        resp = requests.post(f"{API_BASE}/research/", headers=headers, json={
            "max_iterations": title, "query": description
        })
        st.write(resp.status_code, resp.json())

with st.expander("Get Research History"):
    token_his = st.text_input("Access Token", key="history_token")
    if st.button("Get History"):
        headers = {"Authorization": f"Bearer {token_his}"}
        resp = requests.get(f"{API_BASE}/research/history", headers=headers)
        st.write(resp.status_code, resp.json())

with st.expander("Get Research By Id"):
    research_id = st.text_input("Research ID", key="by_id")
    token_id = st.text_input("Access Token", key="by_id_token")
    if st.button("Fetch Research"):
        headers = {"Authorization": f"Bearer {token_id}"}
        resp = requests.get(f"{API_BASE}/research/{research_id}", headers=headers)
        st.write(resp.status_code, resp.json())

with st.expander("Delete Research By Id"):
    del_research_id = st.text_input("Research ID", key="del_id")
    del_token = st.text_input("Access Token", key="del_token")
    if st.button("Delete Research"):
        headers = {"Authorization": f"Bearer {del_token}"}
        resp = requests.delete(f"{API_BASE}/research/{del_research_id}", headers=headers)
        st.write(resp.status_code, resp.json())
