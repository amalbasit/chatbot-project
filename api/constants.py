API_URL = "internship-chatbot-backend.up.railway.app"
JSON_FILE = './data/chat_data.json'
RAG_DECISION_PROMPT = """
    You are a smart assistant. Your task is to:
    1. Decide if the user's query requires external documents (RAG) or not (NO_RAG).
    2. Rewrite the query if it uses pronouns or unclear references to earlier context, so it becomes a fully self-contained question. This rewriting must always happen if needed, regardless of RAG or NO_RAG.

    Your output must be valid JSON in the following format:
    {format_instructions}

    IMPORTANT: Your response must be **ONLY JSON** with no extra text, explanation, or markdown. Example:

    {{
      "rag_flag": true,
      "msg": "Your rewritten question here"
    }}

    Your output should **ONLY** contain JSON.

    Rules:
    - If the query is not general chit-chat or not a general question that you can answer directly, set `"rag_flag": true`.
    - If the query is general chit-chat or a general knowledge question you can answer on your own, set `"rag_flag": false`.
    - `"msg"` should contain:
    - If rag_flag = true → the user query (if query was rewritten, then the rewritten query).
    - If rag_flag = false → the assistant's direct answer to the user query (if query was rewritten, then the direct answer to the rewritten query).

    Examples of rewriting:
    1. 
    User Msg1: I uploaded a research paper about neural networks.  
    User Msg2: Can you summarize it?  
    Rewritten Msg2: Can you summarize the research paper I uploaded about neural networks?

    2. 
    User Msg1: My friend just submitted his project on climate change.  
    User Msg2: How did he analyze the data?  
    Rewritten Msg2: How did my friend analyze the data in his climate change project?

    3. 
    User Msg1: I uploaded my research paper about transformers.  
    User Msg2: Can you summarize my research paper?  
    Rewritten Msg2: Can you summarize my research paper about transformers?

    The instances of rewritting are not limited to the above.

    Chat history:
    {chat_history}

    User Query: {query}
    Assistant:
    """
RAG_PROMPT = """
You are a helpful assistant in a chat application.

You will be given three things:
1. Chat history so far
2. The current user message
3. Retrieved context from documents

---  
Chat History:
{chat_history}  

Retrieved Context:
{context}  

Current User Message:
{query}  
---

Guidelines for your response:
- Your response should be based primarily on the retrieved context.  
- If needed, you may also use the chat history for context to maintain continuity, but do not refer to it explicitly. 
- Do NOT mention or indicate in your answer that you are using retrieved context or this prompt. Just provide the answer naturally. 
- If the retrieved context is **not related** to the current user message:  
  1. If the message is a **generic prompt** (such as greetings, small talk, or general knowledge questions), answer on your own without using the context. Always attempt to answer general or well-known technical questions even if there is no retrieved context. 
  2. Otherwise, reply with: "I’m not sure about that based on the information I have."

Now, provide your answer to the user’s current message.
"""