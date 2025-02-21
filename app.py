import streamlit as st
import pandas as pd
import random
import time
import plotly.express as px


st.set_page_config(page_title="Mool AI Orchestration Chatbot", layout="wide")

st.title("Mool AI Orchestration Chatbot")
st.markdown("## Chat with Mool AI and Analyze API Call Metrics")

# Sidebar Navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Chatbot", "Dashboard"])

# Input OpenAI API key in the sidebar
openai_api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

# Initialize session state for metrics if not already set
if "metrics_db" not in st.session_state:
    st.session_state.metrics_db = {
        "openai_calls": 0,
        "mool_calls": 0,
        "successful_calls": 0,
        "failed_calls": 0,
        "higher_model_calls": 0,
        "lower_model_calls": 0
    }

metrics_db = st.session_state.metrics_db

# Cost Configurations
COST_PER_OPENAI_CALL = 0.02  # Example cost per call
COST_PER_MOOL_CALL = 0.01  # Example cheaper cost per call

# Feature flag toggle for Mool AI
toggle_mool = st.sidebar.checkbox("Enable Mool AI Orchestration", value=True)

# Function to generate response using OpenAI GPT-4
def generate_response(question):
    if not openai_api_key:
        return "Error: OpenAI API Key is required. Please enter it in the sidebar."
    
    try:
        openai.api_key = openai_api_key
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": question}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"

# Function to simulate routing decisions
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
    chat_history = st.session_state.get("chat_history", [])
    
    user_input = st.text_input("Ask a question:")
    if st.button("Send") and user_input:
        response_type = "mool" if toggle_mool else "openai"
        status = "success" if random.random() > 0.1 else "fail"
        
        metrics_db["mool_calls"] += 1 if response_type == "mool" else 0
        metrics_db["openai_calls"] += 1 if response_type == "openai" else 0
        metrics_db["successful_calls"] += 1 if status == "success" else 0
        metrics_db["failed_calls"] += 1 if status == "fail" else 0
        
        routed_model = route_call()
        response_text = f"Response from: **{response_type.upper()} Model**\nRouting Decision: Sent to **{routed_model} model**"
        
        if status == "success":
            ai_response = generate_response(user_input)
            response_text += f"\nAI Response: {ai_response}"
        else:
            response_text += "\nFailed to generate response. Try again."
        
        chat_history.append((user_input, response_text))
        st.session_state["chat_history"] = chat_history
    
    for user_msg, bot_msg in chat_history[-5:]:
        st.write(f"**You:** {user_msg}")
        st.write(f"**Mool AI:** {bot_msg}")
        st.markdown("---")

elif page == "Dashboard":
    st.subheader("API Call Metrics & Cost Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("API Call Metrics")
        df = pd.DataFrame([
            [metrics_db['openai_calls'], metrics_db['mool_calls'], metrics_db['successful_calls'], metrics_db['failed_calls']]
        ], columns=["OpenAI Calls", "Mool AI Calls", "Successful Calls", "Failed Calls"])
        st.table(df)
        
        # Visualization
        fig = px.pie(names=["Higher Model", "Lower Model"],
                     values=[metrics_db['higher_model_calls'], metrics_db['lower_model_calls']],
                     title="Routing Distribution (Higher vs. Lower Model)")
        st.plotly_chart(fig)
    
    with col2:
        st.subheader("Cost Analysis")
        total_cost_openai = metrics_db["openai_calls"] * COST_PER_OPENAI_CALL
        total_cost_mool = metrics_db["mool_calls"] * COST_PER_MOOL_CALL
        st.metric(label="Total Cost (OpenAI)", value=f"${total_cost_openai:.4f}")
        st.metric(label="Total Cost (Mool AI)", value=f"${total_cost_mool:.4f}")
        st.metric(label="Savings", value=f"${total_cost_openai - total_cost_mool:.4f}")
        
        # Bar chart comparison
        cost_df = pd.DataFrame({
            "Method": ["OpenAI", "Mool AI"],
            "Cost": [total_cost_openai, total_cost_mool]
        })
        fig_cost = px.bar(cost_df, x="Method", y="Cost", title="Cost Comparison (OpenAI vs. Mool AI)", text_auto=True)
        st.plotly_chart(fig_cost)

st.sidebar.markdown("---")
st.sidebar.text("Mool AI Chatbot v1.0")
