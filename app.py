import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/chat"  # your FastAPI URL

# --- Initialize session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_message" not in st.session_state:
    st.session_state.last_message = ""


# bot reply

def get_bot_response(prompt):
    try:
        response = requests.post(
            API_URL, 
            json={"message": prompt}       
        )
        # Extract reply from JSON
        return response.json().get("reply", "No reply received")
    except Exception as e:
        print(f"Error: {e}") # DEBUGGING, ACC WRITE reply_text = "⚠️ Could not reach server. Please try again."

# --- Function to send message ---
def send_message():
    prompt = st.session_state.user_input.strip()
    reply_text = ""

    # Avoid duplicates or empty messages
    if prompt and prompt != st.session_state.last_message:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.last_message = prompt

        reply_text = get_bot_response(prompt)

        st.session_state.user_input = ""  # safely clears input

    # Append AI reply to chat
    st.session_state.messages.append({"role": "ai", "content": reply_text})

message_container = st.container(height=680, border=False) # acts as a div

with message_container:
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.write(message['content'])

# --- Input row layout ---
col_plus, col_input, col_send = st.columns([0.7, 8, 1.2], vertical_alignment='bottom', gap='small')

with col_plus:
    st.button(label="", icon="➕")

# Text input with on_change callback
with col_input:
    st.text_input(
        label="Message",
        label_visibility="hidden",
        placeholder="Type your message...",
        key="user_input",
        on_change=send_message
    )

# Send button triggers the same function
with col_send:
    if st.button("Send", type="primary"):
        send_message()
