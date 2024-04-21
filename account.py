import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import bcrypt
import datetime

# Initialiser Firebase une seule fois
if not firebase_admin._apps:
    cred = credentials.Certificate('./jade.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

def create_user(email, first_name, last_name, username, password):
    if db.collection('users').document(username).get().exists:
        st.error("Nom d'utilisateur déjà pris.Veuillez en choisir un autre.")
        return False
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    doc_ref = db.collection('users').document(username)
    doc_ref.set({
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'username': username,
        'password': hashed_password,
        'last_active': datetime.datetime.now()
    })

def check_user(username, password):
    doc_ref = db.collection('users').document(username)
    doc = doc_ref.get()
    if doc.exists:
        user_info = doc.to_dict()
        if bcrypt.checkpw(password.encode('utf-8'), user_info['password']):
            return True
    return False

def login():
    with st.form("login"):
        st.write("Connexion")
        login_username = st.text_input("Username")
        login_password = st.text_input("Mot de passe de connexion", type="password")
        login_button = st.form_submit_button("Se connecter")

        if login_button:
            if check_user(login_username, login_password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = login_username
                return True
            else:
                st.error("Échec de la connexion.")
                return False
def sign():
    with st.form("signup"):
        st.write("Inscription")
        email = st.text_input("Email")
        first_name = st.text_input("Prénom")
        last_name = st.text_input("Nom")
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submit_button = st.form_submit_button("S'inscrire")

        if submit_button:
            if create_user(email, first_name, last_name, username, password):
                st.session_state['logged_in'] = True
                st.success("Inscription réussie ! Vous êtes maintenant connecté.")
                return True
            else:
                return False
        