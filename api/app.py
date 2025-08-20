import os

from fastapi import FastAPI, UploadFile, File, Form

from api.model import UserInput, BotReply
from api.llm import llm
from api.utils import load_data, save_data
from api.rag import RAGPipeline

# PUT WHERE?
template = """
You are a helpful assistant answering questions.
Use ONLY the following context to answer the question:

Context:
{context}

---

Question: {question}

Answer:
"""

# RAG Object
rag_pipeline = RAGPipeline(vector_name="file_vector", template_string=template)

app = FastAPI()

chat_history = load_data() 


UPLOAD_FOLDER = "./api/uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/upload_txt")
def upload_txt(
    file: UploadFile = File(...),
    session_id: str = Form(...)
    ):
        file_path = os.path.join(UPLOAD_FOLDER, f"{session_id}_{file.filename}")
        
        with open(file_path, "wb") as f:
            f.write(file.file.read()) # uploads file to server

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        rag_pipeline.add_document(content, session_id=session_id)
        return {"status": "success", "file_saved": file_path}





@app.post('/chat', response_model=BotReply) 
def bot_response(user_input: UserInput) -> BotReply: 
    session_id = user_input.uuid
    user_msg = user_input.message

    if session_id not in chat_history:
        chat_history[session_id] = []

    chat_history[session_id].append({'role':'user', 'content':user_msg})

    # retrieved_docs = rag.query(user_msg, session_id=session_id)

    llm_msgs = [
        {"role": "system", "content": "You are a friendly AI assistant. Respond naturally to greetings and questions."}
    ]

    # Add all previous messages for this session
    for msg in chat_history[session_id]:
        llm_msgs.append({"role": msg['role'], "content": msg['content']})

    # 🔹 Retrieve docs
    retrieved_docs = rag_pipeline.query(user_msg, session_id=session_id)

    if retrieved_docs:
        bot_reply = rag_pipeline.query_llm(user_msg, session_id=session_id)
    else:

        bot_reply = llm.invoke(llm_msgs).content
    # Append bot reply to chat history
    chat_history[session_id].append({'role':'assistant', 'content':bot_reply}) 

    save_data(chat_history)

    # print(llm_msgs)

    return BotReply(reply=bot_reply)