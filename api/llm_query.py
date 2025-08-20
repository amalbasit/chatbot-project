from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma

from api.llm import llm


def llm_query_with_retriever(vector_store: Chroma, prompt: PromptTemplate, query: str, retriever) -> str:
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,        # use the filtered retriever
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt}
    )
    # response = qa_chain.invoke(query)
    response = qa_chain.invoke({"query": query})
    return response['result']

