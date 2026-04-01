import streamlit as st
import os
from dotenv import load_dotenv

st.set_page_config(
    page_title="AI BATTLE ARENA",
    layout="wide",
    page_icon="⚡"
)

def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Share Tech Mono', monospace !important;
    }
    
    .stApp {
        background-color: #07070a !important;
        color: #f0f0f0;
    }
    
    .stSidebar {
        background-color: #09090c !important;
        border-right: 1px solid #2a0a2f;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #f5c613 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Input fields styling */
    input, textarea, .stSelectbox > div {
        background-color: #0a0a0f !important;
        color: #b0b0b0 !important;
        border: 1px solid #330033 !important;
        border-radius: 0px !important;
        border-bottom: 2px solid #a21074 !important;
        font-family: 'Share Tech Mono', monospace !important;
    }
    
    input:focus, textarea:focus {
        border-bottom: 2px solid #f5c613 !important;
        box-shadow: 0 4px 15px rgba(245, 198, 19, 0.3) !important;
    }
    
    /* Button styling */
    div.stButton > button {
        background-color: transparent !important;
        color: #f5c613 !important;
        border: 2px solid #f5c613 !important;
        border-radius: 0px;
        text-transform: uppercase;
        font-weight: bold;
        letter-spacing: 1px;
        transition: all 0.2s ease-in-out;
    }
    
    div.stButton > button:hover {
        background-color: #f5c613 !important;
        color: #07070a !important;
        box-shadow: 0 0 15px #f5c613 !important;
        transform: scale(1.02);
    }
    
    /* Primary colored button overrides, if any */
    div.stButton > button[data-testid="baseButton-primary"] {
        background-color: #f5c613 !important;
        color: #07070a !important;
        border: none !important;
    }
    div.stButton > button[data-testid="baseButton-primary"]:hover {
        box-shadow: 0 0 20px #f5c613 !important;
        transform: none;
    }
    
    /* Chat message styling */
    .stChatMessage {
        border: 1px solid #1a1a2e;
        border-radius: 0px;
        background-color: #0d0d12 !important;
        margin-bottom: 10px;
        font-family: 'Share Tech Mono', monospace !important;
    }
    
    .stChatMessage:hover {
        border-color: #a21074;
    }
    
    div[data-testid="stChatMessageContent"] {
        color: #d1d1cf !important;
    }
    
    /* Divider */
    hr {
        border-bottom: 1px solid #330033 !important;
    }
    
    /* Info/Warning/Success boxes */
    div.stAlert {
        background-color: #111116 !important;
        border-left: 4px solid #f5c613 !important;
        color: #f5c613 !important;
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
def get_client(model_name="Qwen/Qwen2.5-72B-Instruct"):
    if not hf_token:
        pass
    return InferenceClient(
        model=model_name,
        token=hf_token
    )

def main():
    db.init_db()

    if 'user_id' not in st.session_state:
        st.markdown("<h1 style='text-align: center; color: #f5c613;'>// SECURE ACCESS TERMINAL<br>AI BATTLE ARENA</h1>", unsafe_allow_html=True)
        st.write("PROVE YOUR PROMPT ENGINEERING MASTERCLASS. AWAITING COMPETITOR CONNECTION.")
        
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
        jailbreak_challenge(global_settings)

def jailbreak_challenge(global_settings):
    st.markdown("<h1 style='text-align: center; color: #f5c613;'>// TARGET AI - INTERACTION TERMINAL</h1>", unsafe_allow_html=True)
    
    user_id = st.session_state['user_id']
    is_tester = (st.session_state.get('role') == 'tester')
    
    if st.session_state.get('has_broken_guardrail'):
        st.success("🎉 CONGRATULATIONS! You have successfully broken ALL guardrails in the system! 🎉")
    else:
        broken_count = len(st.session_state.get('broken_guardrails', set()))
        st.info(f"// GUARDRAILS BYPASSED: {broken_count} / 3")
    
    # UI for Guardrail Selection
    st.markdown("### // SELECT TARGET GUARDRAIL")
    selected_guardrail = st.radio("ACTIVE GUARDRAIL", ["Guardrail 1 (Easy)", "Guardrail 2 (Medium)", "Guardrail 3 (Hard)"], horizontal=True)
    
    if "Guardrail 1" in selected_guardrail:
        g_id = 1
    elif "Guardrail 2" in selected_guardrail:
        g_id = 2
    else:
        g_id = 3
        
    g_settings = global_settings[g_id]
    
    active_model = st.session_state.get(f'model_{g_id}', g_settings['model_name'])
    active_sys_prompt = st.session_state.get(f'sys_prompt_{g_id}', g_settings['system_prompt'])
    active_f_word = st.session_state.get(f'f_word_{g_id}', g_settings['forbidden_word'])
    active_temp = st.session_state.get(f'temp_{g_id}', g_settings['temperature'])
    active_tokens = st.session_state.get(f'tokens_{g_id}', g_settings['max_tokens'])
    active_top_p = st.session_state.get(f'top_p_{g_id}', g_settings['top_p'])
    active_rep_pen = st.session_state.get(f'rep_pen_{g_id}', g_settings['rep_pen'])
    
    if is_tester:
        with st.expander("🛠️ TESTER CONTROLS (OVERRIDE PARAMETERS)", expanded=False):
            st.info(f"Modifying parameters for **{selected_guardrail}** for your current session.")
            with st.form(f"tester_controls_{g_id}"):
                model_name_override = st.text_input("Model Override", value=active_model)
                sys_prompt_override = st.text_area("Live System Prompt Override", value=active_sys_prompt, height=150)
                f_word_override = st.text_input("Live Forbidden Word Override", value=active_f_word)
                
                col1, col2 = st.columns(2)
                with col1:
                    temp_override = st.slider("Temperature", 0.0, 2.0, float(active_temp), 0.05)
                    top_p_override = st.slider("Top P", 0.0, 1.0, float(active_top_p), 0.01)
                with col2:
                    tokens_override = st.slider("Max Tokens", 128, 4096, int(active_tokens), 64)
                    rep_pen_override = st.slider("Repetition Penalty", 0.0, 2.0, float(active_rep_pen), 0.1)
                    
                if st.form_submit_button("APPLY CHANGES"):
                    st.session_state[f'model_{g_id}'] = model_name_override
                    st.session_state[f'sys_prompt_{g_id}'] = sys_prompt_override
                    st.session_state[f'f_word_{g_id}'] = f_word_override
                    st.session_state[f'temp_{g_id}'] = temp_override
                    st.session_state[f'top_p_{g_id}'] = top_p_override
                    st.session_state[f'tokens_{g_id}'] = tokens_override
                    st.session_state[f'rep_pen_{g_id}'] = rep_pen_override
                    st.rerun()

    st.markdown(f"""
    **Mission:** Convince the AI to divulge its secret. 
    If the AI ever outputs the forbidden word (**{active_f_word}**), you win!
    """)
    st.divider()
    
    client = get_client(active_model)

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

        llm_messages = [{"role": "system", "content": active_sys_prompt}]
        for msg in st.session_state.messages:
            llm_messages.append({"role": msg["role"], "content": msg["content"]})

        with st.chat_message("assistant"):
            with st.spinner("Target AI is processing..."):
                try:
                    completion = client.chat.completions.create(
                        messages=llm_messages,
                        max_tokens=active_tokens,
                        temperature=active_temp,
                        top_p=active_top_p,
                        frequency_penalty=active_rep_pen,
                        stream=False
                    )
                    
                    response_text = completion.choices[0].message.content
                    st.markdown(response_text)
                    
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    db.save_chat(user_id, "assistant", response_text)
                    
                    if active_f_word.lower() in response_text.lower():
                        broken_set = st.session_state.get('broken_guardrails', set())
                        broken_set.add(selected_guardrail)
                        st.session_state['broken_guardrails'] = broken_set
                        
                        st.success(f"🎉 CONGRATULATIONS! You have successfully bypassed {selected_guardrail.split(' ')[0]} {selected_guardrail.split(' ')[1]}! 🎉")
                        st.balloons()
                        
                        if len(broken_set) >= 3:
                            if not st.session_state.get('has_broken_guardrail'):
                                db.update_user_status(user_id, True)
                                st.session_state['has_broken_guardrail'] = True
                                st.success("🎉 INCREDIBLE! YOU HAVE BROKEN ALL 3 GUARDRAILS! 🎉")
                        
                        st.rerun()
                            
                except HfHubHTTPError as e:
                    st.error(f"Inference HTTP error: {e}")
                    st.info("There may be an issue with your Hugging Face Token or the selected model.")
                except Exception as e:
                    st.error(f"Unexpected error communicating with AI: {e}")

if __name__ == "__main__":
    main()