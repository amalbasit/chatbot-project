import os

from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

from api.constants import DATA_PATH

# Load all documents DONT NEED
def load_docs() -> List:
    docs = []
    for file in os.listdir(DATA_PATH):
        if file.endswith(".txt"):
            loader = TextLoader(os.path.join(DATA_PATH, file))
            docs.extend(loader.load())
    return docs


# Split into chunks
def split_docs(chunk_size: int, chunk_overlap: int, docs: List) -> List:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True
    )
    return text_splitter.split_documents(docs)