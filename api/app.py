from bs4 import BeautifulSoup
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from PyPDF2 import PdfReader
import requests
from typing import Dict
import validators

from model import UserInput, BotReply
from utils import load_data, save_data
from rag import RAGPipeline

rag_pipeline = RAGPipeline(vector_name="chroma_db")

app = FastAPI()

chat_history = load_data()

@app.post("/upload_txt")
def upload_txt(
    file: UploadFile = File(...),
    session_id: str = Form(...)
) -> Dict:
    content = file.file.read().decode("utf-8")  
    rag_pipeline.chunks_split(content, session_id=session_id)
    return {"status": "success"}

@app.post("/upload_pdf")
def upload_pdf(
    file: UploadFile = File(...),
    session_id: str = Form(...)) -> Dict:

    reader = PdfReader(file.file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    rag_pipeline.chunks_split(text, session_id)

    return {"status": "success"}

@app.post("/upload_url")
def upload_url(url: str = Form(...), session_id: str = Form(...)) -> Dict:
    try:
        if not validators.url(url):
            raise HTTPException(
                status_code=400, 
                detail="Invalid URL format."
            )

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser") 
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text(separator="\n")
        text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        rag_pipeline.chunks_split(text, session_id=session_id)
            
        return {"status": "success"}
    
    except:
        raise HTTPException(status_code=response.status_code, detail="URL fetch failed.")


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