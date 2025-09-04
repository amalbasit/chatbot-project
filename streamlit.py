import os
os.environ["STREAMLIT_WATCHDOG_OBSERVERS"] = "0"
import time
import uuid

import streamlit as st
from streamlit_push_notifications import send_alert
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

if "file_uploaded_alert" not in st.session_state:
    st.session_state.file_uploaded_alert = True
    

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

def upload_file_api(file_name: str, file_content: bytes, session_id: str, endpoint: str) -> requests.Response:
    files = {"file": (file_name, file_content)}
    data = {"session_id": session_id}
    return requests.post(f"{API_URL}/{endpoint}", files=files, data=data)

def upload_alert(response: requests.Response, msg: str) -> None:
    if response.status_code == 200:
        send_alert(msg)
        st.session_state.show_upload_options = False        
        time.sleep(0.1)
        st.rerun()
    else:
        try:
            error_msg = response.json().get("detail", f"Failed to upload. Status code: {response.status_code}")
        except Exception:
            error_msg = f"Failed to upload. Status code: {response.status_code}"
        st.error(error_msg)

message_container = st.container(height=680, border=False)

with message_container:
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.write(message['content'])

col_plus, col_input = st.columns([0.7, 8], vertical_alignment='bottom', gap='small')

with col_plus:
    if st.button(label="", icon="➕"):
        st.session_state.show_upload_options = not st.session_state.show_upload_options

if st.session_state.show_upload_options:
    option = st.selectbox("Choose upload option:", ["Select...", "Upload URL", "Upload a File"])
    if option == "Upload URL":
        url_input = st.text_input("Enter a URL to upload:")
        if url_input:
            try:
                data = {
                    "url": url_input,
                    "session_id": st.session_state.session_id
                }
                response = requests.post(f"{API_URL}/upload_url", data=data)

                upload_alert(response, "URL Uploaded Successfully!")

            except Exception as e:
                st.error(f"Error uploading URL: {e}")

    elif option == "Upload a File":
        uploaded_file = st.file_uploader("Upload a File", type=["txt", "pdf"])
        if uploaded_file is not None:
            file_content = uploaded_file.getvalue()         
            if not file_content:
                st.error("The uploaded file is empty!")
            else:
                file_type = uploaded_file.name.split('.')[-1].lower() 
                try: 
                    if file_type == 'txt':
                        response = upload_file_api(
                            uploaded_file.name,
                            file_content,
                            st.session_state.session_id,
                            "upload_txt"
                        )
                    elif file_type == 'pdf':
                        response = upload_file_api(
                            uploaded_file.name,
                            file_content,
                            st.session_state.session_id,
                            "upload_pdf"
                        )
                    else:
                        st.error('Unsupported file type!')
                    
                    upload_alert(response, "File Uploaded Successfully!")

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