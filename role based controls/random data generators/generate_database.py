from langchain_openai import AzureOpenAIEmbeddings
# from langchain.llms import OpenAI
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import Chroma

import openai 
import shutil
import warnings
warnings.filterwarnings("ignore")

from config import *
import os

DATA_PATH_TEXT = "../data/textfiles"
DATA_PATH_PDF = "../data/pdffiles"
CHROMA_PATH = "../chroma"

azure_AI_embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=api_base,
    api_key=api_key,
    api_version=api_version
)


def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)


def load_documents():
    loader_txt = DirectoryLoader(DATA_PATH_TEXT, glob="*.txt")
    loader_pdf = DirectoryLoader(DATA_PATH_PDF, glob="*.pdf", loader_cls=PyPDFLoader)
    documents_txt = loader_txt.load()
    documents_pdf = loader_pdf.load()
    documents = documents_txt + documents_pdf
    return documents


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 500,
        length_function=len,
        add_start_index = True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    document = chunks[10]
    print(document.page_content)
    print(document.metadata)
    return chunks


def save_to_chroma(chunks: list[Document]):
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    db = Chroma.from_documents(
        chunks, azure_AI_embeddings, persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")

    
if __name__ == "__main__":
    generate_data_store()