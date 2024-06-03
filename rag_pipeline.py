from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
import streamlit as st
from langchain_core.output_parsers import StrOutputParser
import os
from PyPDF2 import PdfReader

folder_path = "allLocal"
texts = []  # List to store texts of individual documents

# Iterate over files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".pdf"):  # Check if the file is a PDF
        pdf_path = os.path.join(folder_path, filename)
        pdf_reader = PdfReader(pdf_path)
        document_text = []  # List to store text of current document
        for page in pdf_reader.pages:
            document_text.append(page.extract_text())
        texts.append(document_text)




from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
class Document:
    def __init__(self, page_content):
        self.page_content = page_content
        self.metadata = {}  # You can add metadata if needed

from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import TextLoader


def split_text(documents: list[list[str]]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap=0,  # No overlap between chunks
        length_function=len,
        add_start_index=True
    )

    chunks = []
    for document_text in documents:
        for page_content in document_text:
            page_chunks = text_splitter.split_text(page_content)
            chunks.extend(page_chunks)

    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks


chuncks=split_text(texts)



#Embeddings 
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings

GOOGLE_API_KEY="AIzaSyAo-DLb7NFWacpdJEkW9_ilASVpm-6Wu5A"
embeddings = HuggingFaceEmbeddings()



import shutil
from langchain_community.vectorstores import Chroma

# Replace with your API key and CHROMA_PATH
CHROMA_PATH = "chroma"
GOOGLE_API_KEY="AIzaSyAo-DLb7NFWacpdJEkW9_ilASVpm-6Wu5A"
api_key="AIzaSyD0R1MAEAyl-2kg7i-LcPS3JE9esaQnEzc"

def save_to_chroma(chunks: list[list[str]]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new DB from the documents.
    documents = [Document(page) for chunk in chunks for page in chunk]
    db = Chroma.from_documents(
        documents,
        embeddings,
        persist_directory=CHROMA_PATH
    )
    db.persist()
    retriever = db.as_retriever()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}")

save_to_chroma(texts)

import argparse
from dataclasses import dataclass
from langchain.vectorstores.chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate


PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}

"""
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
def search_llm():
    # Prepare the DB.
    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest",google_api_key=GOOGLE_API_KEY,
            temperature=0.3, convert_system_message_to_human=True)
    embedding_function = embeddings
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    retriever = db.as_retriever()

    contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is."""
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
    model, retriever, contextualize_q_prompt
    )
    qa_system_prompt = """You are an assistant for question-answering tasks. \
    Use the following pieces of retrieved context to answer the question. \
    If you don't know the answer, just say that you don't know. \
    Use three sentences maximum and keep the answer concise.\

    {context}"""
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )


    question_answer_chain = create_stuff_documents_chain(model, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    return rag_chain
# Example usage:
#query_text = input("Enter a question: ")
#print(search_llm(query_text))
