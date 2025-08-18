import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="deepseek-r1-distill-llama-70b",
    temperature=0.8,
    max_tokens=1000,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
)