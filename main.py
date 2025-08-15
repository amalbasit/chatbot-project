import streamlit as st
import requests
import uuid


API_URL = "http://127.0.0.1:8000/chat"

# Session states
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_message" not in st.session_state:
    st.session_state.last_message = ""

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

def get_bot_response(prompt):
    try:
        msg_info = {
            "uuid": st.session_state.session_id,
            "message": prompt,
            "type": "text"
        }
        response = requests.post(API_URL, json=msg_info)
        return response.json().get("reply", "No reply received")
    except Exception as e:
        print(f"Error: {e}")

def send_message():
    prompt = st.session_state.user_input
    reply_text = ""

    if prompt and prompt != st.session_state.last_message:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.last_message = prompt

        reply_text = get_bot_response(prompt)

        st.session_state.user_input = ""

    st.session_state.messages.append({"role": "ai", "content": reply_text})

message_container = st.container(height=680, border=False)

with message_container:
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.write(message['content'])

col_plus, col_input, col_send = st.columns([0.7, 8, 1.2], vertical_alignment='bottom', gap='small')

with col_plus:
    st.button(label="", icon="➕")

with col_input:
    st.text_input(
        label="Message",
        label_visibility="hidden",
        placeholder="Type your message...",
        key="user_input",
        on_change=send_message
    )

with col_send:
    if st.button("Send", type="primary"):
        send_message()
