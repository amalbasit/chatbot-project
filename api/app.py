from fastapi import FastAPI
from model import Request, Response
import json
from llm import llm 
import os

app = FastAPI()
JSON_FILE = './data/chat_data.json'

# folder_path = './data'
# os.makedirs(folder_path, exist_ok=True)
# JSON_FILE = os.path.join(folder_path, 'chat_data.json')

def load_data():
    try:
        with open(JSON_FILE, 'r') as file:
            return json.loads(file)
    except:
        return {}


def save_data(data):
    with open(JSON_FILE, 'w') as file:
        json.dump(data, file, indent=4)

chat_history = load_data() 

@app.post('/chat', response_model=Response) 
def bot_response(request: Request) -> Response: 
    session_id = request.uuid
    user_msg = request.message

    if session_id not in chat_history:
        chat_history[session_id] = []

    chat_history[session_id].append({'role':'user', 'content':user_msg})

    llm_messages = [
        ("system", "You are a helpful assistant that explains technical concepts simply.")
    ]

    # append user msg to llm msgs
    llm_messages.append(("user", user_msg))

    # get AI response
    bot_reply = llm.invoke(llm_messages).content

    # append bot reply to chat history
    chat_history[session_id].append({'role':'ai', 'content':bot_reply})

    save_data(chat_history)

    return Response(reply=bot_reply)

# @app.get("/history/{session_id}")
# def get_history(session_id: str):
#     return {"history": chat_history.get(session_id, [])}