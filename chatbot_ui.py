import streamlit as st
import requests
import time

# --- Configuration ---
st.set_page_config(layout="centered", page_title="FinLit Chatbot")
BACKEND_URL = "http://localhost:8000"  # URL of your FastAPI backend

# --- Page Title ---
st.title("💸 Financial Literacy Chatbot")
st.caption("Ask me anything about your financial documents!")

# --- Initialize Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I help you with your financial questions today?"}
    ]

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input ---
if prompt := st.chat_input("Ask a question about budgeting, saving, etc."):
    # 1. Add user message to history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # 2. Get bot response from backend
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            # Call the FastAPI backend's /chat endpoint
            api_request_data = {
                "message": prompt,
                "user_id": "streamlit_user_123" 
            }
            
            response = requests.post(
                f"{BACKEND_URL}/api/v1/chatbot/chat",
                json=api_request_data,
                timeout=60 # 60-second timeout
            )
            
            if response.status_code == 200:
                bot_response = response.json()
                response_text = bot_response.get("response", "Sorry, I couldn't get a response.")
                
                # Simulate typing effect
                full_response = ""
                for chunk in response_text.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
                # Add bot response to history
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            else:
                error_detail = response.json().get('detail', 'Unknown server error')
                st.error(f"Failed to get response from bot: {error_detail}")
                st.session_state.messages.append({"role": "assistant", "content": f"Sorry, I ran into an error: {error_detail}"})

        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")
            st.session_state.messages.append({"role": "assistant", "content": f"Sorry, I couldn't connect to the server: {e}"})
