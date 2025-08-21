import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


from llm import llm
from constants import TEMPLATE


# -- Vector Store --
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

def init_vector_store(name: str) -> Chroma:

    vector_store = Chroma(
        collection_name=name,
        embedding_function=embeddings,
        persist_directory="./chroma_db",
    )
    return vector_store

# -- Prompt Builder --
def build_prompt() -> PromptTemplate: 
    prompt_template = PromptTemplate(
        input_variables=["chat_history", "context", "query"],
        template=TEMPLATE
    )
    return prompt_template

# -- RAG Pipeline --
class RAGPipeline:
    def __init__(self, vector_name):
        self.vector_store = init_vector_store(vector_name)  
        self.llm_chain = LLMChain(llm=llm, prompt=build_prompt())

    def split_docs(self, chunk_size: int, chunk_overlap: int, docs: List) -> List:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            add_start_index=True
        )
        return text_splitter.split_documents(docs)

    def add_session_id(self, content: str, session_id: str):
        doc = Document(page_content=content)
        chunks = self.split_docs(chunk_size=800, chunk_overlap=150, docs=[doc])
        for chunk in chunks:
            chunk.metadata = {"session_id": session_id}
        self.vector_store.add_documents(chunks)

    def retrieve_and_answer(self, chat_history, question: str, session_id: str):

        # Retrieve docs
        retriever = self.vector_store.as_retriever(
            search_kwargs={"filter": {"session_id": session_id}}
        )

        docs = retriever.get_relevant_documents(question)
        context = "\n".join([doc.page_content for doc in docs])

        # Convert chat_history to string
        session_msgs = chat_history.get(session_id, [])
        chat_history_text = "\n".join([f"{m['role']}: {m['content']}" for m in session_msgs])

        # call LLM Chain
        response = self.llm_chain.run({
            "chat_history": chat_history_text,
            "query": question,
            "context": context
        })

        return response