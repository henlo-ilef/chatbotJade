import docx
import streamlit as st
import os
#from rag_pipeline import search_llm 
from external_search import get_response
from external_search import titre 
import pickle 
from pathlib import Path
import streamlit_authenticator as stauth
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from account import login, sign
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import requests

from docx import Document
from docx.shared import RGBColor, Pt , Inches

st.set_page_config(page_title="💬PPP Benchmark studies Chatbot")
service_account_path = 'C:/Users/tasnim/Downloads/chatbotJade-main/chatbotJade-main/jade.json'

def initialize_firebase():
    # Check if any apps are already initialized in this environment
    if not firebase_admin._apps:
        # If no apps, initialize app with credentials
        cred = credentials.Certificate(service_account_path)
        firebase_app = firebase_admin.initialize_app(cred)
    else:
        # If already initialized, use the existing app
        firebase_app = firebase_admin.get_app()
    return firebase_app

# Initialize Firebase
firebase_app = initialize_firebase()
db = firestore.client(app=firebase_app)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Display login form if not logged in
if not st.session_state.logged_in:
    st.subheader("Login")
    if login():
        st.session_state.logged_in = True
        #st.success("You are now logged in!")
        #username = st.session_state.get("username", "")
        st.rerun()
        


# Display sign up form
    st.subheader("Sign Up")
    if sign():
        st.session_state.logged_in = True
        st.success("Sign up successful! You are now logged in.")
        
        #username = st.session_state.get("username", "")
        st.rerun()
else:
   st.empty() 
if 'username' in st.session_state:
    username = st.session_state['username']
    user_id = username

   
    

# Initialize Firebase

if st.session_state.logged_in: 
    
    
    

    # --- USER AUTHENTIFICATION ---


    from google.cloud.firestore import ArrayUnion
    import datetime
    blue_titles = [
    "1. Présentation du projet",
    "2. Structure contractuelle du projet",
    "3. Leçons tirées/Recommandations/Meilleures pratiques/Erreurs à éviter",
    "Leçons tirées:",
    "3. Leçons tirées",
    "Project presentation",
    "Project presentation:",
    "1. Project presentation",
    "1. Project Presentation",
    "Project presentation",
    "Project presentation:",
    "Project Presentation:",
    "1. Project Overview",
    "Project Contractual Structure",
    "Project Contractual Structure:",
    "2. Project Contractual Structure",
    "Project Contractual Structure:",
    
    "3. Lessons Learned/Recommendations/Best Practices/Mistakes to Avoid",
    "Lessons Learned/Recommendations/Best Practices/Mistakes to Avoid",
    "Lessons Learned/Recommendations/Best Practices/Mistakes to Avoid:",
    "Project Overview",
    
    ]
    def create_docx_with_colored_titles(content, blue_titles, images):
        doc = Document()
        presentation_titles = [
            "Project presentation", "Project presentation:", "1. Project presentation",
            "1. Project Presentation", "1. Présentation du projet", "Project Overview"
        ]

        # Process each line of the content
        for line in content.split("\n"):
            clean_line = line.strip("* ")

            # Add the line to the document
            if clean_line in blue_titles:
                para = doc.add_paragraph()
                run = para.add_run(clean_line)
                run.font.color.rgb = RGBColor(0, 0, 255)  # Blue color
                run.font.size = Pt(14)  # Font size

                # If the line is one of the presentation titles, add the image below
                if clean_line in presentation_titles:
                    for image_url in images:
                        response = requests.get(image_url)
                        image_stream = BytesIO(response.content)  # Create a memory stream with the downloaded image
                        doc.add_picture(image_stream, width=Inches(5.5))  # Adjust size as needed
                        para = doc.add_paragraph()
                        para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER  # Center the image
            else:
                doc.add_paragraph(clean_line)

        # Save the document to a memory buffer
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        return buffer
    def save_message(user_id, role, content, new_chat=False, chat_id=None):
        chats_ref = db.collection('users').document(user_id).collection('chats')
        if new_chat:
                # Start a new chat document
            chat_ref = chats_ref.document()
            chat_ref.set({
                'started_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP,
                'status': 'active',
                'messages': [{
                    'timestamp': datetime.datetime.now(),
                    'sender': role,
                    'content': content,
                    'type': 'text'
                }]
            })
        else:
                # Use the existing chat_id if provided
            if chat_id:
                chat_ref = chats_ref.document(chat_id)
            else:
                    # Find the most recent chat document
                chat_doc = chats_ref.order_by('updated_at', direction=firestore.Query.DESCENDING).limit(1).get()
                if chat_doc and list(chat_doc):
                    chat_doc = chat_doc[0]
                    chat_ref = chats_ref.document(chat_doc.id)

            new_message = {
                'timestamp': datetime.datetime.now(),
                'sender': role,
                'content': content,
                'type': 'text',
                'role': role
            }
            chat_ref.update({
                'messages': ArrayUnion([new_message]),
                'updated_at': firestore.SERVER_TIMESTAMP
            })





    def get_history(user_id):
        chats_ref = db.collection('users').document(user_id).collection('chats')
        all_chats = []
        chats = chats_ref.stream()  # Récupère tous les documents de chat pour cet utilisateur

        for chat in chats:
            chat_data = chat.to_dict()
            messages = chat_data.get('messages', [])
            all_chats.append({
                'chat_id': chat.id,  # Inclure l'ID du document de chat
                'messages': messages
            })

        return all_chats



    if "questions_button_clicked" not in st.session_state:
        st.session_state.questions_button_clicked = False

    if "conduct_button_clicked" not in st.session_state:
        st.session_state.conduct_button_clicked = False



        #user_id = username  # Example to link chats to user id
    user_id=username
    with st.sidebar:
        st.title(f"Welcome {username}")
        if st.button("Questions about existing documents"):
                    # Mark the button as clicked
            st.session_state.questions_button_clicked = True
                    # Add a message to the chat history
            st.session_state.messages.append({"role": "assistant", "content": "What questions do you have about existing documents?"})

        if st.button("Conduct new benchmark studies"):
                    # Mark the button as clicked
            st.session_state.conduct_button_clicked = True
            st.session_state.start_new_chat = True
            st.session_state.selected_chat = None 
            st.session_state.messages = []
            # Ajouter un message initial pour le chat
            initial_message = "Let's conduct new benchmark studies. What do you want to know?"
            st.session_state.messages.append({"role": "assistant", "content": initial_message})
            # Sauvegarder le message dans un nouveau chat
            save_message(user_id, "assistant", initial_message, new_chat=True)
        st.title("Historique")
        all_chats = get_history(user_id)
        if all_chats:
            for chat in all_chats:
                   
                if chat['messages']: 
                    if len(chat['messages']) > 1:
                        msg = chat['messages'][1]['content']
                        titre_result=titre(msg)
                    else:
                        titre_result=chat['messages'][0]['content']

                       
                    if st.button(f"{titre_result}", key=chat['chat_id']):
                        st.session_state.selected_chat = chat
                else:
                    st.write(f"Chat {chat['chat_id']} has no messages yet.")
        else:
            st.write("No chat history found.")


        

                    
    if 'start_new_chat' not in st.session_state:
        st.session_state.start_new_chat = False

    if 'selected_chat' in st.session_state and not st.session_state.start_new_chat:
        chat = st.session_state.selected_chat
        st.write(f"Chat started on: {chat['messages'][0]['timestamp']}")
        for message in chat['messages']:
            with st.chat_message(message["sender"]):
                st.markdown(message['content'])

    if "messages" not in st.session_state:
        st.session_state.messages = []
            # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    prompt = st.chat_input("How can I help you?")
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
            if 'selected_chat_id' in st.session_state:
                save_message(user_id, "user", prompt, chat_id=st.session_state.selected_chat_id)
            else :
                save_message(user_id, "user", prompt)

                                  
        st.session_state.messages.append({"role": "user", "content": prompt})
            
        
                
        if st.session_state.conduct_button_clicked:
            response,images = get_response(prompt)
            if 'selected_chat_id' in st.session_state:
                save_message(user_id, "assistant", response, chat_id=st.session_state.selected_chat_id)
            else:
                save_message(user_id, "assistant", response)
                
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
             # Appeler la fonction et créer le document
            buffer = create_docx_with_colored_titles(response, blue_titles,images)

        # Créer un bouton de téléchargement pour le document DOCX dans Streamlit
            st.download_button(
                label="Download",
                data=buffer,
                file_name="bechmark_study.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
  
