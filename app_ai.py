import streamlit as st
import os
from rag_pipeline import search_llm 
from external_search import external_search
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas
import pickle 
from pathlib import Path
import streamlit_authenticator as stauth
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
    def save_to_pdf(response, filename):
        try:
            pdf_path = PDF_DIR + filename
            c = Canvas(pdf_path, pagesize=letter)

            # Define font and font size
            c.setFont("Helvetica", 12)

            # Split the response into lines
            lines = response.split("\n")

            # Set initial y coordinate for drawing text
            y_coordinate = 750

            # Draw each line of the response
            for line in lines:
                # Draw the line at the current y coordinate
                c.drawString(100, y_coordinate, line)

                # Move to the next line
                y_coordinate -= 20  # Adjust this value based on line spacing

            # Save the PDF file
            c.save()

            print(f"PDF saved successfully at: {pdf_path}")
        except Exception as e:
            print(f"Error occurred while saving PDF: {e}")


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
        # Prompt the user for a filename to save the response as a PDF
        filename_input = st.text_input("Enter filename (without extension) to save response as PDF:")

        # Add a button to trigger the saving process
        if st.button("Save as PDF") and filename_input:
            filename = filename_input.strip()  # Remove leading/trailing whitespaces
            filename = filename.replace(" ", "_")  # Replace spaces with underscores
            filename += ".pdf"
            save_to_pdf(response, filename)
        

        # Add the assistant's response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

