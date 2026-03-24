import streamlit as st
import database as db

def admin_panel():
    st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>Admin Command Center</h1>", unsafe_allow_html=True)
    if not st.session_state.get('is_admin'):
        st.error("Access denied. Command Center is strictly for Admins.")
        return

    st.header("⚙️ Global Settings")
    settings = db.get_settings()
    with st.form("settings_form"):
        system_prompt = st.text_area("Global System Prompt", value=settings['system_prompt'], height=200)
        forbidden_word = st.text_input("Forbidden Word", value=settings['forbidden_word'], help="The secret word the user is trying to make the AI say.")
        submitted = st.form_submit_button("Deploy Settings", use_container_width=True)
        if submitted:
            db.update_settings(system_prompt, forbidden_word)
            st.success("Global Settings successfully deployed!")

    st.divider()

    st.header("🛡️ Pending Approvals")
    users = db.get_all_users()
    pending_users = [u for u in users if not u['is_approved']]
    
    if pending_users:
        st.warning(f"You have {len(pending_users)} users waiting for approval.")
        for u in pending_users:
            with st.expander(f"Review Profile: {u['username']} ({u['name']})"):
                st.write(f"**Email:** {u['email']}")
                st.write(f"**Phone:** {u['phone_no']}")
                st.write(f"**Requested Role:** `{u['role']}`")
                
                if u['role'] == "tester":
                    st.write(f"**NU ID:** {u['nu_id']}")
                else:
                    st.write(f"**University:** {u['university']}")
                    st.write(f"**Roll No:** {u['roll_no']}")
                
                if st.button(f"Approve {u['username']}", key=f"approve_{u['id']}", type="primary"):
                    db.approve_user(u['id'])
                    st.success(f"{u['username']} has been approved!")
                    st.rerun()
    else:
        st.info("No pending approvals. All caught up!")

    st.divider()

    st.header("📊 User Progress & Database")
    if users:
        # Prepare dynamic columns for dataframe so it looks clean
        clean_users = []
        for u in users:
            clean_users.append({
                "ID": u['id'],
                "Username": u['username'],
                "Role": u['role'],
                "Broken Guardrail": u['has_broken_guardrail'],
                "Institution Info": u['nu_id'] if u['role'] == 'tester' else f"{u['university']} ({u['roll_no']})",
                "Approved": u['is_approved']
            })
        st.dataframe(clean_users, use_container_width=True)
    else:
        st.info("No users found in the database.")

    st.divider()

    st.header("🔍 View Chat Transcripts")
    user_options = {f"{u['username']} ({u['role']}) {'🏅' if u['has_broken_guardrail'] else ''}": u['id'] for u in users}
    
    if user_options:
        selected_user = st.selectbox("Select User Profile", options=list(user_options.keys()))
        if selected_user:
            user_id = user_options[selected_user]
            chats = db.get_chats(user_id)
            if chats:
                with st.expander(f"Chat History for {selected_user}", expanded=True):
                    for chat in chats:
                        with st.chat_message(chat['role']):
                            st.caption(chat['timestamp'])
                            st.write(chat['content'])
            else:
                st.info("No chat transcripts found for this user.")
