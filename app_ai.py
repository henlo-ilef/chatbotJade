import streamlit as st
import os
from rag_pipeline import search_llm 
from external_search import external_search
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas
import pickle 
from pathlib import Path
import streamlit_authenticator as stauth
from io import BytesIO

st.set_page_config(page_title="💬PPP Benchmark studies Chatbot")


# --- USER AUTHENTIFICATION ---

names = ["Houyem", "test"]
usernames = ["houyem", "test"]


# load hashed passwords
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    "jade_chatbot", "abcdef", cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")








if authentication_status:
    # Define the directory where PDFs will be saved
    PDF_DIR = "D:/HenloIlef/2K24/chatbotJade/chatbotJade/allLocal/"
    # Function to save response to PDF
    

    # Initialize session state
    if "questions_button_clicked" not in st.session_state:
        st.session_state.questions_button_clicked = False

    if "conduct_button_clicked" not in st.session_state:
        st.session_state.conduct_button_clicked = False

    with st.sidebar:
        st.sidebar.title(f"Welcome {name}")
        st.title('💬PPP Benchmark studies Chatbot')
        st.write('This chatbot is created using the open-source Mistral and RAG.')
        authenticator.logout("Logout", "sidebar")


        # Add two buttons to the sidebar
        if st.button("Questions about existing documents"):
            # Mark the button as clicked
            st.session_state.questions_button_clicked = True
            # Add a message to the chat history
            st.session_state.messages.append({"role": "assistant", "content": "What questions do you have about existing documents?"})

        if st.button("Conduct new benchmark studies"):
            # Mark the button as clicked
            st.session_state.conduct_button_clicked = True
            # Add a message to the chat history
            st.session_state.messages.append({"role": "assistant", "content": "Let's conduct new benchmark studies. What do you want to know?"})

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

        # Call the appropriate function based on the context
        if st.session_state.questions_button_clicked:
            response = search_llm(prompt)
        elif st.session_state.conduct_button_clicked:
            response = external_search(prompt)
            


        # Display the response in the chat
        with st.chat_message("assistant"):
            st.markdown(response)
        

        # Add a button to trigger the saving process
     
       

        # Inside the button callback for "Save as PDF"
        if st.button("Save as PDF"):
            # Create a PDF file with the chat history
            buffer = BytesIO()
            canvas = Canvas(buffer, pagesize=letter)
            for message in st.session_state.messages:
                role = message["role"]
                content = message["content"]
                if role == "user":
                    content = "User: " + content
                elif role == "assistant":
                    content = "Assistant: " + content
                canvas.drawString(10, 750, content)
                canvas.showPage()
            canvas.save()
            
            # Offer the download of the PDF file
            buffer.seek(0)
            st.download_button(label="Download PDF", data=buffer, file_name="chat_history.pdf", mime="application/pdf")
        # Add the assistant's response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

