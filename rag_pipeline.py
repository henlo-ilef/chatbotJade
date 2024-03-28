from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
import streamlit as st

import os
from PyPDF2 import PdfReader

folder_path = "D:/HenloIlef/2K24/chatbotJade/chatbotJade/allLocal"
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

#print(texts)


from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

class Document:
    def __init__(self, page_content):
        self.page_content = page_content
        self.metadata = {}  # You can add metadata if needed


def split_text(documents: list[list[str]]):
    text_splitter = RecursiveCharacterTextSplitter(
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

from langchain_google_genai import GoogleGenerativeAIEmbeddings

GOOGLE_API_KEY="AIzaSyD0R1MAEAyl-2kg7i-LcPS3JE9esaQnEzc"
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001",google_api_key=GOOGLE_API_KEY)
query_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", task_type="retrieval_query", google_api_key=GOOGLE_API_KEY
)
doc_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", task_type="retrieval_document", google_api_key=GOOGLE_API_KEY
)


import shutil
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# Replace with your API key and CHROMA_PATH
CHROMA_PATH = "D:/HenloIlef/2K24/chatbotJade/chatbotJade/chroma"
GOOGLE_API_KEY="AIzaSyD0R1MAEAyl-2kg7i-LcPS3JE9esaQnEzc"
api_key="AIzaSyD0R1MAEAyl-2kg7i-LcPS3JE9esaQnEzc"

def save_to_chroma(chunks: list[list[str]]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new DB from the documents.
    documents = [Document(page) for chunk in chunks for page in chunk]
    db = Chroma.from_documents(
        documents,
        doc_embeddings,
        persist_directory=CHROMA_PATH
    )
    db.persist()
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
def search_llm(query):
    # Prepare the DB.
    model = ChatGoogleGenerativeAI(model="gemini-pro",google_api_key=GOOGLE_API_KEY,
            temperature=0.3)
    embedding_function = GoogleGenerativeAIEmbeddings(model="models/embedding-001",google_api_key=GOOGLE_API_KEY)
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    query_text= query
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        print(f"Unable to find matching results.")


    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)


    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("source") for doc, _score in results]
    formatted_response = f"Response: {response_text.content}\nSources: {sources}"
    print(formatted_response)
    return formatted_response
# Example usage:
#query_text = input("Enter a question: ")
#print(search_llm(query_text))
