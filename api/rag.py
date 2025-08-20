import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import shutil

from api.data_loader import split_docs
from api.vector_store import init_vector_store
from api.prompt import build_prompt
from api.llm_query import llm_query_with_retriever
from langchain.schema import Document

class RAGPipeline:
    def __init__(self, vector_name, template_string):
        self.vector_store = init_vector_store(vector_name)  
        self.prompt_template = build_prompt(template_string)

    def add_document(self, content: str, session_id: str):
        # wrap content in Document
        doc = Document(page_content=content)
        chunks = split_docs(chunk_size=800, chunk_overlap=150, docs=[doc])
        for chunk in chunks:
            chunk.metadata = {"session_id": session_id}
        print(f"Split into {len(chunks)} chunks for session {session_id}")
        self.vector_store.add_documents(chunks)
        # print(self.vector_store)

    def query(self, question: str, session_id: str):
        docs = self.vector_store.similarity_search(
            query=question,
            k=5,  # number of results to return
            filter={"session_id": session_id}
        )
        return docs

    def query_llm(self, question: str, session_id: str):
        # Create a retriever filtered by session_id
        retriever = self.vector_store.as_retriever(
            search_kwargs={"filter": {"session_id": session_id}}
        )

        # Call LLM with the filtered retriever and the PromptTemplate object directly
        return llm_query_with_retriever(self.vector_store, self.prompt_template, question, retriever)



