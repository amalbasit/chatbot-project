import uuid

import streamlit as st
import requests
 
from api.constants import API_URL

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_message" not in st.session_state:
    st.session_state.last_message = ""

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "show_upload_options" not in st.session_state:
    st.session_state.show_upload_options = False


def get_bot_response(prompt: str) -> str:
    try:
        msg_info = {
            "uuid": st.session_state.session_id,
            "message": prompt
        }
        response = requests.post(f'{API_URL}/chat', json=msg_info)
        bot_reply = response.json().get("reply", "No reply received")
        return bot_reply
    except Exception as e:
        print(f"Error: {e}")


def send_message() -> None:
    prompt = st.session_state.user_input.strip()
    if prompt and prompt != st.session_state.last_message:
        st.session_state.last_message = prompt
        # append user prompt
        st.session_state.messages.append({'role': 'user', 'content': prompt}) 
        bot_reply = get_bot_response(prompt)
        # append bot reply
        st.session_state.messages.append({'role': 'ai', 'content': bot_reply})
        st.session_state.user_input = ""


message_container = st.container(height=680, border=False)

with message_container:
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.write(message['content'])

col_plus, col_input, col_send = st.columns([0.7, 8, 1.2], vertical_alignment='bottom', gap='small')

with col_plus:
    if st.button(label="", icon="➕"):
        st.session_state.show_upload_options = not st.session_state.show_upload_options

if st.session_state.show_upload_options:
    option = st.selectbox("Choose upload option:", ["Select...", "Upload URL", "Upload TXT File"])
    if option == "Upload URL":
        pass
    elif option == "Upload TXT File":
        uploaded_file = st.file_uploader("Upload TXT file", type=["txt"])
        if uploaded_file is not None:
            file_content = uploaded_file.getvalue()            
            if not file_content:
                st.error("Uploaded file is empty!")
            else:
                files = {"file": (uploaded_file.name, file_content)}
                data = {"session_id": st.session_state.session_id}
                try:
                    response = requests.post(f"{API_URL}/upload_txt", files=files, data=data)
                    if response.status_code == 200:
                        st.success("File uploaded successfully!")
                    else:
                        st.error(f"Failed to upload file. Status code: {response.status_code}")
                except Exception as e:
                    st.error(f"Error uploading file: {e}")

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