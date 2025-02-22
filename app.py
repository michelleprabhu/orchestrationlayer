import streamlit as st
import pandas as pd
import random
import time
import plotly.express as px
import openai

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
        "lower_model_calls": 0,
        "total_tokens_openai": 0,
        "total_tokens_mool": 0
    }

metrics_db = st.session_state.metrics_db

# Cost Configurations
COST_PER_OPENAI_TOKEN = 0.00002  # Example cost per token for GPT-4
COST_PER_MOOL_TOKEN = 0.00001  # Example cost per token for Mool AI (GPT-3.5 equivalent)

# Function to determine model based on complexity (Router LLM Logic)
def determine_model(question):
    if len(question.split()) > 7:  # If question is complex, use GPT-4 (higher model)
        return "gpt-4-turbo"
    else:
        return "mool-ai"  # Use Mool AI (GPT-3.5 equivalent) for simpler queries

# Function to generate response using OpenAI API
def generate_response(question):
    if not openai_api_key:
        return "Error: OpenAI API Key is required. Please enter it in the sidebar."
    
    model_name = determine_model(question)
    
    try:
        client = openai.Client(api_key=openai_api_key)
        response = client.chat.completions.create(
            model=model_name if model_name != "mool-ai" else "gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}]
        )
        tokens_used = response.usage.total_tokens
        
        # Update metrics
        if model_name == "gpt-4-turbo":
            metrics_db["openai_calls"] += 1
            metrics_db["higher_model_calls"] += 1
            metrics_db["total_tokens_openai"] += tokens_used
        else:
            metrics_db["mool_calls"] += 1
            metrics_db["lower_model_calls"] += 1
            metrics_db["total_tokens_mool"] += tokens_used
        
        return response.choices[0].message.content
    except openai.OpenAIError as e:
        return f"⚠️ OpenAI API Error: {str(e)}"
    except Exception as e:
        return f"⚠️ Unexpected Error: {str(e)}"

if page == "Chatbot":
    st.subheader("Mool AI Chatbot")
    chat_history = st.session_state.get("chat_history", [])
    
    user_input = st.text_input("Ask a question:")
    if st.button("Send") and user_input:
        model_used = determine_model(user_input)
        response_text = f"Response from: **{model_used.upper()}**"
        
        ai_response = generate_response(user_input)
        response_text += f"\nAI Response:\n{ai_response}"
        
        chat_history.append((user_input, response_text))
        st.session_state["chat_history"] = chat_history
    
    for user_msg, bot_msg in chat_history[-5:]:
        st.write(f"**You:** {user_msg}")
        st.write(f"**Mool AI:**")
        st.text(bot_msg)
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
        
        fig = px.pie(names=["Higher Model (GPT-4 Turbo)", "Lower Model (Mool AI)"],
                     values=[metrics_db['higher_model_calls'], metrics_db['lower_model_calls']],
                     title="Routing Distribution (Higher vs. Lower Model)")
        st.plotly_chart(fig)
    
    with col2:
        st.subheader("Cost Analysis Based on Tokens")
        total_cost_openai = metrics_db["total_tokens_openai"] * COST_PER_OPENAI_TOKEN
        total_cost_mool = metrics_db["total_tokens_mool"] * COST_PER_MOOL_TOKEN
        st.metric(label="Total Cost (OpenAI - GPT-4 Turbo)", value=f"${total_cost_openai:.4f}")
        st.metric(label="Total Cost (Mool AI - GPT-3.5 Turbo)", value=f"${total_cost_mool:.4f}")
        st.metric(label="Savings with Mool AI", value=f"${total_cost_openai - total_cost_mool:.4f}")
        
        cost_df = pd.DataFrame({
            "Method": ["OpenAI (GPT-4 Turbo)", "Mool AI (GPT-3.5 Turbo)"],
            "Cost": [total_cost_openai, total_cost_mool]
        })
        fig_cost = px.bar(cost_df, x="Method", y="Cost", title="Cost Comparison (GPT-4 vs. Mool AI)", text_auto=True)
        st.plotly_chart(fig_cost)

st.sidebar.markdown("---")
st.sidebar.text("Mool AI Chatbot v1.0")
