import streamlit as st
import requests

# FastAPI backend URL
BASE_URL = "http://127.0.0.1:8000"

# Streamlit UI Setup
st.set_page_config(page_title="Order Management Chatbot", layout="centered")

st.markdown("<h2 style='text-align: center;'>🛍️ Order Management Chatbot</h2>", unsafe_allow_html=True)

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
user_input = st.chat_input("Ask about an order, create, or cancel an order...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Send Query to FastAPI Chatbot Endpoint
    try:
        response = requests.get(f"{BASE_URL}/chatbot/", params={"query": user_input}, timeout=10)
        if response.status_code == 200:
            bot_reply = response.json().get("response", "Sorry, I couldn't process that request.")
        else:
            bot_reply = f"Error: {response.status_code} - Unable to fetch response."
    except requests.exceptions.RequestException as e:
        bot_reply = f"Connection Error: {e}"

    # Display Bot Response
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
