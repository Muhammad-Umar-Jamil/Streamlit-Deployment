import streamlit as st
import os
from dotenv import load_dotenv

# Set page config must be first
st.set_page_config(
    page_title="AI Jailbreak Challenge",
    layout="wide",
    page_icon="🔓"
)

import database as db
import auth
import admin
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError

load_dotenv()
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

@st.cache_resource
def get_client():
    if not hf_token:
        # Default open model when token not available might not work, 
        # so return Client and hope token isn't strictly necessary or give clear error
        pass
    
    # Try using a well-known instruction tuned model on HF
    # You can change the model id here depending on your needs.
    return InferenceClient(
        model="Qwen/Qwen2.5-72B-Instruct",
        token=hf_token
    )

def main():
    db.init_db()

    if 'user_id' not in st.session_state:
        st.title("🔓 AI Jailbreak Challenge")
        st.write("Welcome to the AI Jailbreak Challenge. Please log in or sign up to continue.")
        st.info("Login as Admin: **Username:** `admin`, **Password:** `admin`")
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            auth.login()
        with tab2:
            auth.signup()
        return

    # User is logged in
    with st.sidebar:
        st.write(f"Logged in as: **{st.session_state['username']}**")
        status = '🔓 Jailbroken' if st.session_state.get('has_broken_guardrail') else '🔒 Locked'
        st.write(f"Status: **{status}**")
        
        st.divider()
        
        if st.session_state.get('is_admin'):
            if st.button("Admin Panel", use_container_width=True):
                st.session_state['view'] = 'admin'
                st.rerun()
                
        if st.button("Jailbreak Challenge", use_container_width=True):
            st.session_state['view'] = 'challenge'
            st.rerun()
            
        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    view = st.session_state.get('view', 'challenge')

    if view == 'admin':
        admin.admin_panel()
    else:
        jailbreak_challenge()

def jailbreak_challenge():
    st.title("🔓 System Jailbreak Round")
    
    if st.session_state.get('has_broken_guardrail'):
        st.success("🎉 CONGRATULATIONS! You have successfully broken the AI's guardrail! 🎉")
    
    settings = db.get_settings()
    forbidden_word = settings['forbidden_word']
    system_prompt = settings['system_prompt']
    
    st.markdown(f"""
    **Mission:** Convince the AI to divulge its secret. 
    If the AI ever outputs the forbidden word (**{forbidden_word}**), you win!
    """)
    
    client = get_client()

    user_id = st.session_state['user_id']
    
    # Clear session state messages if user changes account or to reload
    if 'messages' not in st.session_state:
        chats = db.get_chats(user_id)
        st.session_state.messages = [{"role": c["role"], "content": c["content"]} for c in chats]

    # Quick reset button
    if st.button("Clear Chat History", type="secondary"):
        st.session_state.messages = []
        # Not deleting from DB to keep logs for admin, just clearing view
        st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter your prompt to trick the AI..."):
        # Add to state and DB
        st.session_state.messages.append({"role": "user", "content": prompt})
        db.save_chat(user_id, "user", prompt)
        
        with st.chat_message("user"):
            st.markdown(prompt)

        # Build message history for LLM
        llm_messages = [{"role": "system", "content": system_prompt}]
        for msg in st.session_state.messages:
            llm_messages.append({"role": msg["role"], "content": msg["content"]})

        with st.chat_message("assistant"):
            with st.spinner("Target AI is processing..."):
                try:
                    completion = client.chat.completions.create(
                        messages=llm_messages,
                        max_tokens=512,
                        temperature=0.7,
                        top_p=0.9,
                        stream=False
                    )
                    
                    response_text = completion.choices[0].message.content
                    st.markdown(response_text)
                    
                    # Add response to db and session
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    db.save_chat(user_id, "assistant", response_text)
                    
                    # Check win condition (case insensitive)
                    if forbidden_word.lower() in response_text.lower():
                        if not st.session_state.get('has_broken_guardrail'):
                            db.update_user_status(user_id, True)
                            st.session_state['has_broken_guardrail'] = True
                            st.rerun()
                            
                except HfHubHTTPError as e:
                    st.error(f"Inference HTTP error: {e}")
                    st.info("There may be an issue with your Hugging Face Token or the selected model.")
                except Exception as e:
                    st.error(f"Unexpected error communicating with AI: {e}")

if __name__ == "__main__":
    main()