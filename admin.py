import streamlit as st
import database as db

def admin_panel():
    st.title("Admin Panel")
    if not st.session_state.get('is_admin'):
        st.error("Access denied. Admins only.")
        return

    st.header("Settings")
    settings = db.get_settings()
    with st.form("settings_form"):
        system_prompt = st.text_area("System Prompt", value=settings['system_prompt'], height=200)
        forbidden_word = st.text_input("Forbidden Word", value=settings['forbidden_word'], help="The secret word the user is trying to make the AI say.")
        submitted = st.form_submit_button("Update Settings")
        if submitted:
            db.update_settings(system_prompt, forbidden_word)
            st.success("Settings updated!")

    st.header("User Progress")
    users = db.get_all_users()
    if users:
        st.dataframe(users, use_container_width=True)
    else:
        st.info("No users found.")

    st.header("View User Chats")
    user_options = {f"{u['username']}{' (Broken Guardrail)' if u['has_broken_guardrail'] else ''}": u['id'] for u in users}
    
    if user_options:
        selected_user = st.selectbox("Select User Profile", options=list(user_options.keys()))
        if selected_user:
            user_id = user_options[selected_user]
            chats = db.get_chats(user_id)
            if chats:
                st.write(f"Showing chat history for user ID: {user_id}")
                for chat in chats:
                    with st.chat_message(chat['role']):
                        st.caption(chat['timestamp'])
                        st.write(chat['content'])
            else:
                st.info("No chats found for this user.")
