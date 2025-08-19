from fastapi import FastAPI

from api.model import UserInput, BotReply
from api.llm import llm
from api.utils import load_data, save_data

app = FastAPI()

chat_history = load_data() 

@app.post('/chat', response_model=BotReply) 
def bot_response(user_input: UserInput) -> BotReply: 
    session_id = user_input.uuid
    user_msg = user_input.message

    if session_id not in chat_history:
        chat_history[session_id] = []

    chat_history[session_id].append({'role':'user', 'content':user_msg})

    llm_msgs = [
        {"role": "system", "content": "You are a friendly AI assistant. Respond naturally to greetings and questions."}
    ]

    # Add all previous messages for this session
    for msg in chat_history[session_id]:
        llm_msgs.append({"role": msg['role'], "content": msg['content']})

    # Get AI response
    bot_reply = llm.invoke(llm_msgs).content

    # Append bot reply to chat history
    chat_history[session_id].append({'role':'assistant', 'content':bot_reply}) 

    save_data(chat_history)

    print(llm_msgs)

    return BotReply(reply=bot_reply)