import streamlit as st
import os
from rag_pipeline import search_llm 

# App title
st.set_page_config(page_title="💬PPP Benchmark studies Chatbot")

with st.sidebar:
    st.title('💬PPP Benchmark studies Chatbot')
    st.write('This chatbot is created using the open-source Mistral and RAG.')

if "gemini_model" not in st.session_state:
    st.session_state["gemini_model"] = "gemini-pro"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
prompt = st.chat_input("How can I help you?")
if prompt:
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Call the function to get the response
    response = search_llm(prompt)

    # Process the response
    response_text = response.split("Response:")[1].strip()  # Remove "Response:" prefix
    sources = [source for source in response.split("Sources: ")[1].split(", ") if source != "None"]  # Filter out None sources

    # Display the processed response in the chat
    with st.chat_message("assistant"):
        st.markdown(response_text)
    

    # Add the assistant's response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_text})
