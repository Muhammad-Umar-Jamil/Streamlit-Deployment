import streamlit as st
import database as db

def admin_panel():
    st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>Admin Command Center</h1>", unsafe_allow_html=True)
    if not st.session_state.get('is_admin'):
        st.error("Access denied. Command Center is strictly for Admins.")
        return

    users = db.get_all_users()

    st.header("⚙️ Global Settings")
    settings = db.get_settings()
    with st.form("settings_form"):
        system_prompt = st.text_area("Global System Prompt", value=settings['system_prompt'], height=150)
        forbidden_word = st.text_input("Global Forbidden Word", value=settings['forbidden_word'], help="The secret word.")
        if st.form_submit_button("Deploy Global Settings", use_container_width=True):
            db.update_settings(system_prompt, forbidden_word)
            st.success("Global Settings successfully deployed!")

    st.divider()

    st.header("🎛️ User-Specific Settings (Overrides Global)")
    override_users = {f"{u['username']} ({u['name']})": u for u in users if not u['is_admin']}
    if override_users:
        sel = st.selectbox("Select User to Override", options=["-- Select User --"] + list(override_users.keys()))
        if sel != "-- Select User --":
            u_data = override_users[sel]
            with st.form(f"override_form_{u_data['id']}"):
                st.write(f"Configure custom challenge for **{u_data['username']}**")
                
                curr_p = u_data['custom_system_prompt'] if u_data['custom_system_prompt'] else ""
                curr_w = u_data['custom_forbidden_word'] if u_data['custom_forbidden_word'] else ""
                
                c_prompt = st.text_area("Custom System Prompt (Leave blank to use Global)", value=curr_p, height=150)
                c_word = st.text_input("Custom Forbidden Word (Leave blank to use Global)", value=curr_w)
                
                if st.form_submit_button("Save User Overrides", type="primary", use_container_width=True):
                    db.update_user_custom_settings(u_data['id'], c_prompt.strip(), c_word.strip())
                    st.success(f"Overrides saved for {u_data['username']}!")
                    st.rerun()
    else:
        st.info("No normal users available to override.")

    st.divider()

    st.header("🛡️ Pending Approvals")
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
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Approve", key=f"approve_{u['id']}", type="primary", use_container_width=True):
                        db.approve_user(u['id'])
                        st.success(f"{u['username']} has been approved!")
                        st.rerun()
                with col2:
                    if st.button(f"❌ Reject & Delete", key=f"reject_{u['id']}", use_container_width=True):
                        db.delete_user(u['id'])
                        st.error(f"{u['username']} rejected and deleted.")
                        st.rerun()
    else:
        st.info("No pending approvals. All caught up!")

    st.divider()

    st.header("📊 User Database")
    if users:
        clean_users = []
        for u in users:
            clean_users.append({
                "ID": u['id'],
                "Username": u['username'],
                "Role": u['role'],
                "Status": "✅ Approved" if u['is_approved'] else "⏳ Pending",
                "Winner": "🏆 Yes" if u['has_broken_guardrail'] else "❌ No",
                "Custom Prompt": "Yes" if u['custom_system_prompt'] else "No"
            })
        st.dataframe(clean_users, use_container_width=True)
    else:
        st.info("No users found.")

    st.divider()

    st.header("🔍 View Chat Transcripts")
    user_options = {f"{u['username']} ({u['role']}) {'🏅' if u['has_broken_guardrail'] else ''}": u['id'] for u in users}
    if user_options:
        selected_user = st.selectbox("Select User Profile", options=["-- Select User --"] + list(user_options.keys()))
        if selected_user != "-- Select User --":
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

    st.divider()

    st.header("❌ Danger Zone")
    if override_users:
        st.warning("Deleting a user is permanent. All chat history will be completely wiped from the database.")
        del_sel = st.selectbox("Select User to Delete", options=["-- Select User --"] + list(override_users.keys()), key="del_sel")
        if del_sel != "-- Select User --":
            u_data = override_users[del_sel]
            if st.button(f"Permanently Delete {u_data['username']}", type="primary"):
                db.delete_user(u_data['id'])
                st.success(f"{u_data['username']} was permanently deleted.")
                st.rerun()
