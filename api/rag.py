import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List

from .constants import RAG_PROMPT
from .llm import llm


# -- Vector Store --
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

def init_vector_store(name: str) -> Chroma:

    vector_store = Chroma(
        collection_name=name,
        embedding_function=embeddings
    )
    return vector_store

# -- Prompt Builder --
def build_prompt() -> PromptTemplate: 
    prompt_template = PromptTemplate(
        input_variables=["chat_history", "context", "query"],
        template=RAG_PROMPT
    )
    return prompt_template

# -- RAG Pipeline --
class RAGPipeline:
    def __init__(self, vector_name: str) -> None:
        self.vector_store = init_vector_store(vector_name)  
        self.llm_chain = build_prompt() | llm | StrOutputParser()

    def split_docs(self, chunk_size: int, chunk_overlap: int, docs: List) -> List:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            add_start_index=True
        )
        return text_splitter.split_documents(docs)

    # def chunks_split(self, content: str, session_id: str) -> None:
    #     doc = Document(page_content=content)
    #     chunks = self.split_docs(chunk_size=800, chunk_overlap=100, docs=[doc])
    #     for chunk in chunks:
    #         chunk.metadata = {"session_id": session_id}
    #     self.vector_store.add_documents(chunks)

    from langchain.schema import Document

    def chunks_split(self, content: str, session_id: str, batch_size: int = 5) -> None:
        """
        Splits content into chunks and adds them to vector store in batches.
        This avoids memory spikes and long blocking operations.
        """
        doc = Document(page_content=content)
        chunks = self.split_docs(chunk_size=800, chunk_overlap=100, docs=[doc])

        # Add session metadata
        for chunk in chunks:
            chunk.metadata = {"session_id": session_id}

        # Add to vector store in small batches
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            self.vector_store.add_documents(batch)


    def retrieve_and_answer(self, chat_history_text: str, question: str, session_id: str) -> str:
        # Retrieve docs
        retriever = self.vector_store.as_retriever(
            search_kwargs={"filter": {"session_id": session_id}}
        )
        docs = retriever.get_relevant_documents(question)
        context = "\n".join([doc.page_content for doc in docs])

        # Call LLM Chain
        response = self.llm_chain.invoke({
            "chat_history": chat_history_text,
            "query": question,
            "context": context
        })

        if '</think>' in response:
            response = response.split("</think>")[-1].strip()

        return response