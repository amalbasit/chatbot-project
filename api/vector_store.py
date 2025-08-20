
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def init_vector_store(name: str) -> Chroma:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    vector_store = Chroma(
        collection_name=name,
        embedding_function=embeddings,
        persist_directory="./api/chroma_langchain_db",
    )
    return vector_store