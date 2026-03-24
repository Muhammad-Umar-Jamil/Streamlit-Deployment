import streamlit as st
import os
from dotenv import load_dotenv

st.set_page_config(
    page_title="AI Jailbreak Challenge",
    layout="wide",
    page_icon="🔓"
)

def load_css():
    st.markdown("""
    <style>
    @keyframes fadeIn {
        0% {opacity: 0; transform: translateY(10px);}
        100% {opacity: 1; transform: translateY(0);}
    }
    .stApp {
        animation: fadeIn 1s ease-in-out;
    }
    div.stButton > button {
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        border-radius: 10px;
        font-weight: bold;
    }
    div.stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
    }
    input, textarea, .stSelectbox {
        transition: all 0.3s ease;
        border-radius: 8px !important;
    }
    input:focus, textarea:focus {
        border-color: #ff4b4b !important;
        box-shadow: 0 0 10px rgba(255, 75, 75, 0.2) !important;
    }
    .stChatMessage {
        transition: background-color 0.3s ease;
        border-radius: 10px;
    }
    .stChatMessage:hover {
        background-color: rgba(255, 255, 255, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)
    
load_css()

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
        pass
    return InferenceClient(
        model="Qwen/Qwen2.5-72B-Instruct",
        token=hf_token
    )

def main():
    db.init_db()

    if 'user_id' not in st.session_state:
        st.markdown("<h1 style='text-align: center;'>⚡ Welcome to the AI Arena ⚡</h1>", unsafe_allow_html=True)
        st.write("Prove your prompt engineering masterclass! Please log in or register to enter the challenge.")
        
        tab1, tab2 = st.tabs(["🔒 Login", "📝 Sign Up"])
        with tab1:
            auth.login()
        with tab2:
            auth.signup()
        return

    # Check Approval
    if not st.session_state.get('is_approved'):
        st.markdown("<h1 style='text-align: center;'>⏳ Registration Pending</h1>", unsafe_allow_html=True)
        st.warning("Your profile is currently waiting for Administrator approval.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("https://media.giphy.com/media/tXL4FHPSnVJ0A/giphy.gif", use_container_width=True)
        
        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        return

    # Load fresh user data on every run so admin changes reflect instantly
    # We query the DB specifically to see if the user has custom prompts set
    current_user_data = db.get_user(st.session_state['username'])
    
    # If admin deleted them mid-session, log them out.
    if not current_user_data:
        st.session_state.clear()
        st.rerun()
        
    global_settings = db.get_settings()
    
    # Apply user overrides if they exist, otherwise fallback to global settings
    active_system_prompt = current_user_data['custom_system_prompt'] if current_user_data['custom_system_prompt'] else global_settings['system_prompt']
    active_forbidden_word = current_user_data['custom_forbidden_word'] if current_user_data['custom_forbidden_word'] else global_settings['forbidden_word']

    with st.sidebar:
        st.markdown(f"### 👋 Welcome, {st.session_state.get('name', st.session_state['username'])}")
        st.write(f"**Role:** `{str(st.session_state.get('role', 'user')).upper()}`")
        
        status = '🔓 Jailbroken' if st.session_state.get('has_broken_guardrail') else '🔒 Locked'
        st.write(f"Status: **{status}**")
        
        st.divider()
        
        if st.session_state.get('is_admin'):
            if st.button("🛡️ Admin Panel", use_container_width=True):
                st.session_state['view'] = 'admin'
                st.rerun()
                
        if st.button("⚔️ Jailbreak Arena", use_container_width=True):
            st.session_state['view'] = 'challenge'
            st.rerun()
            
        st.divider()
        if st.button("➡️ Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    view = st.session_state.get('view', 'challenge')

    if view == 'admin' and st.session_state.get('is_admin'):
        admin.admin_panel()
    else:
        jailbreak_challenge(active_system_prompt, active_forbidden_word)

def jailbreak_challenge(system_prompt, forbidden_word):
    st.markdown("<h1 style='text-align: center;'>🔓 System Jailbreak Arena</h1>", unsafe_allow_html=True)
    
    user_id = st.session_state['user_id']
    is_tester = (st.session_state.get('role') == 'tester')
    
    if st.session_state.get('has_broken_guardrail'):
        st.success("🎉 CONGRATULATIONS! You have successfully broken the AI's guardrail! 🎉")
    
    # Defaults for regular users
    temperature = 0.7
    max_tokens = 512
    
    if is_tester:
        with st.expander("🛠️ Tester Controls (Adjust Runtime Parameters)", expanded=False):
            st.info("Since you are a **Tester**, you can temporarily override the model's parameters for your session.")
            system_prompt = st.text_area("Live System Prompt Override", value=system_prompt, height=150, help="Changes made here only last for this page load.")
            
            col1, col2 = st.columns(2)
            with col1:
                temperature = st.slider("Temperature", 0.0, 1.2, 0.7, 0.05)
            with col2:
                max_tokens = st.slider("Max Tokens", 128, 2048, 512, 64)
    
    st.markdown(f"""
    **Mission:** Convince the AI to divulge its secret. 
    If the AI ever outputs the forbidden word (**{forbidden_word}**), you win!
    """)
    st.divider()
    
    client = get_client()

    if 'messages' not in st.session_state:
        chats = db.get_chats(user_id)
        st.session_state.messages = [{"role": c["role"], "content": c["content"]} for c in chats]

    colA, colB = st.columns([1, 5])
    with colA:
        if st.button("🗑️ Clear View", help="Clears your screen. History is kept in DB."):
            st.session_state.messages = []
            st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter your prompt to trick the AI..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        db.save_chat(user_id, "user", prompt)
        
        with st.chat_message("user"):
            st.markdown(prompt)

        llm_messages = [{"role": "system", "content": system_prompt}]
        for msg in st.session_state.messages:
            llm_messages.append({"role": msg["role"], "content": msg["content"]})

        with st.chat_message("assistant"):
            with st.spinner("Target AI is processing..."):
                try:
                    completion = client.chat.completions.create(
                        messages=llm_messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=0.9,
                        stream=False
                    )
                    
                    response_text = completion.choices[0].message.content
                    st.markdown(response_text)
                    
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    db.save_chat(user_id, "assistant", response_text)
                    
                    if forbidden_word.lower() in response_text.lower():
                        if not st.session_state.get('has_broken_guardrail'):
                            db.update_user_status(user_id, True)
                            st.session_state['has_broken_guardrail'] = True
                            st.balloons()
                            st.rerun()
                            
                except HfHubHTTPError as e:
                    st.error(f"Inference HTTP error: {e}")
                    st.info("There may be an issue with your Hugging Face Token or the selected model.")
                except Exception as e:
                    st.error(f"Unexpected error communicating with AI: {e}")

if __name__ == "__main__":
    main()