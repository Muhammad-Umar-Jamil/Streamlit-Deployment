import streamlit as st
import database as db

def login():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        if not username or not password:
            st.warning("Please provide both username and password.")
            return

        user = db.get_user(username)
        if user and db.check_password(password, user['password_hash']):
            st.session_state['user_id'] = user['id']
            st.session_state['username'] = user['username']
            st.session_state['is_admin'] = user['is_admin']
            st.session_state['has_broken_guardrail'] = user['has_broken_guardrail']
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid username or password")

def signup():
    st.subheader("Sign Up")
    new_user = st.text_input("Username", key="signup_username")
    new_password = st.text_input("Password", type="password", key="signup_password")
    if st.button("Sign Up"):
        if not new_user or not new_password:
            st.warning("Please provide both username and password.")
            return

        if db.get_user(new_user):
            st.error("Username already exists")
        else:
            db.create_user(new_user, new_password, is_admin=False)
            st.success("Account created successfully! Please log in.")
