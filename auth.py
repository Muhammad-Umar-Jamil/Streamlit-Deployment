import streamlit as st
import database as db
import re

def login():
    st.subheader("Login to Arena")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Enter Arena", use_container_width=True):
        if not username or not password:
            st.warning("Please provide both username and password.")
            return

        user = db.get_user(username)
        if user and db.check_password(password, user['password_hash']):
            st.session_state['user_id'] = user['id']
            st.session_state['username'] = user['username']
            st.session_state['name'] = user['name']
            st.session_state['role'] = user['role']
            st.session_state['is_admin'] = user['is_admin']
            st.session_state['is_approved'] = user['is_approved']
            st.session_state['has_broken_guardrail'] = user['has_broken_guardrail']
            st.success("Access Granted! Welcome back.")
            st.rerun()
        else:
            st.error("Invalid credentials. Try again.")

def signup():
    st.subheader("Register for the Challenge")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", key="signup_name")
        new_user = st.text_input("Username", key="signup_username")
        email = st.text_input("Email", key="signup_email")
        
    with col2:
        new_password = st.text_input("Password", type="password", key="signup_password")
        phone_no = st.text_input("Phone Number", key="signup_phone")
        nu_id = st.text_input("NU ID (Format: 2xI-xxxx)", key="signup_nu_id", help="Example: 21I-0453")
        
    role = st.selectbox("Role", ["user", "tester"], help="Testers can adjust model parameters.")
    
    if st.button("Submit Registration", use_container_width=True):
        if not all([name, new_user, new_password, email, phone_no, nu_id]):
            st.warning("Please fill in all the required fields.")
            return
            
        # Regex validation for NU ID (2xI-xxxx)
        if not re.match(r"^2\dI-\d{4}$", nu_id):
            st.error("Invalid NU ID Format. It must match the format 2xI-xxxx (e.g. 21I-1234).")
            return

        if db.get_user(new_user):
            st.error("This username is already taken. Choose another.")
        else:
            db.create_user(
                username=new_user, 
                password=new_password, 
                name=name, 
                email=email, 
                role=role, 
                phone_no=phone_no, 
                nu_id=nu_id
            )
            st.success("Registration Sent! An Admin must approve your profile before you can talk to the AI.")
            st.balloons()
