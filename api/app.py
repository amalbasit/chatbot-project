from fastapi import FastAPI, UploadFile, File, Form

from model import UserInput, BotReply
from utils import load_data, save_data
from rag import RAGPipeline

# RAG Object
rag_pipeline = RAGPipeline(vector_name="chroma_db")

app = FastAPI()

chat_history = load_data()

@app.post("/upload_txt")
def upload_txt(
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    content = file.file.read().decode("utf-8")  
    rag_pipeline.add_session_id(content, session_id=session_id)
    return {"status": "success", "message": "Document uploaded successfully!"}

@app.post('/chat', response_model=BotReply) 
def bot_response(user_input: UserInput) -> BotReply: 
    session_id = user_input.uuid
    user_msg = user_input.message

    if session_id not in chat_history:
        chat_history[session_id] = []

    if session_id not in chat_history:
        chat_history[session_id] = []
        chat_history[session_id].append({
            "role": "system", 
            "content": "You are a friendly AI assistant. Respond naturally to greetings and questions."
        })

    chat_history[session_id].append({'role':'user', 'content':user_msg})

    bot_reply = rag_pipeline.retrieve_and_answer(chat_history, user_msg, session_id)    

    chat_history[session_id].append({'role':'assistant', 'content':bot_reply}) 
    save_data(chat_history)

    return BotReply(reply=bot_reply)