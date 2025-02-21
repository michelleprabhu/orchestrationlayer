import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Mool AI Orchestration Chatbot", layout="wide")

st.title("Mool AI Orchestration Chatbot")
st.markdown("## Chat with Mool AI and Analyze API Call Metrics")

# Sidebar Navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Chatbot", "Dashboard"])

# Simulated Database for Metrics
metrics_db = {
    "openai_calls": 0,
    "mool_calls": 0,
    "successful_calls": 0,
    "failed_calls": 0,
    "higher_model_calls": 0,
    "lower_model_calls": 0
}

# Cost Configurations
COST_PER_OPENAI_CALL = 0.02  # Example cost per call
COST_PER_MOOL_CALL = 0.01  # Example cheaper cost per call

def route_call():
    """ Simulates call distribution between high and low models """
    if random.random() < 0.8:
        metrics_db["higher_model_calls"] += 1
        return "higher"
    else:
        metrics_db["lower_model_calls"] += 1
        return "lower"

if page == "Chatbot":
    st.subheader("Mool AI Chatbot")
    user_input = st.text_input("Ask a question:")
    if st.button("Send") and user_input:
        response_type = "mool" if random.random() > 0.5 else "openai"
        status = "success" if random.random() > 0.1 else "fail"
        
        metrics_db["mool_calls"] += 1 if response_type == "mool" else 0
        metrics_db["openai_calls"] += 1 if response_type == "openai" else 0
        metrics_db["successful_calls"] += 1 if status == "success" else 0
        metrics_db["failed_calls"] += 1 if status == "fail" else 0
        
        routed_model = route_call()
        st.write(f"Response from: **{response_type.upper()} Model**")
        st.write(f"Routing Decision: Sent to **{routed_model} model**")
        if status == "success":
            st.success("Response generated successfully!")
        else:
            st.error("Failed to generate response. Try again.")

elif page == "Dashboard":
    st.subheader("API Call Metrics & Cost Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("API Call Metrics")
        df = pd.DataFrame([
            [metrics_db['openai_calls'], metrics_db['mool_calls'], metrics_db['successful_calls'], metrics_db['failed_calls']]
        ], columns=["OpenAI Calls", "Mool AI Calls", "Successful Calls", "Failed Calls"])
        st.table(df)
    
    with col2:
        st.subheader("Cost Analysis")
        total_cost_openai = metrics_db["openai_calls"] * COST_PER_OPENAI_CALL
        total_cost_mool = metrics_db["mool_calls"] * COST_PER_MOOL_CALL
        st.metric(label="Total Cost (OpenAI)", value=f"${total_cost_openai:.4f}")
        st.metric(label="Total Cost (Mool AI)", value=f"${total_cost_mool:.4f}")
        st.metric(label="Savings", value=f"${total_cost_openai - total_cost_mool:.4f}")

st.sidebar.markdown("---")
st.sidebar.text("Mool AI Chatbot v1.0")
