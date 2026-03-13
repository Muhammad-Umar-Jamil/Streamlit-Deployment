import streamlit as st
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError

# ────────────────────────────────────────────────
# 0. Load environment variables
# ────────────────────────────────────────────────
load_dotenv()
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

if not hf_token:
    st.error("HUGGINGFACEHUB_API_TOKEN not found in .env file")
    st.stop()

# ────────────────────────────────────────────────
# 1. Page config & title
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="GPT-OSS 120B Chat",
    layout="wide",
    page_icon="🚀"
)

st.title("🚀 GPT-OSS 120B Explorer")
st.caption("Open-weight 120B model via Hugging Face Inference API")

# ────────────────────────────────────────────────
# 2. Sidebar – settings
# ────────────────────────────────────────────────
with st.sidebar:
    st.header("Model Settings")
    
    system_prompt = st.text_area(
        "System Prompt",
        value="You are a helpful, reasoning-focused assistant. Reasoning: high",
        height=140,
        help="Tip: You can include phrases like 'Reasoning: low/medium/high' — some models react to them."
    )
    
    max_new_tokens = st.slider("Max new tokens", 256, 2048, 1000, step=64)
    temperature = st.slider("Temperature", 0.0, 1.2, 0.7, 0.05)
    
    if st.button("Clear Chat History", type="primary"):
        st.session_state.messages = []
        st.rerun()

# ────────────────────────────────────────────────
# 3. Initialize chat history
# ────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ────────────────────────────────────────────────
# 4. Create Inference Client
# ────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return InferenceClient(
        model="openai/gpt-oss-120b",
        token=hf_token
    )

client = get_client()

# ────────────────────────────────────────────────
# 5. Display previous messages
# ────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ────────────────────────────────────────────────
# 6. User input & generation
# ────────────────────────────────────────────────
if prompt := st.chat_input("Ask GPT-OSS 120B anything..."):
    
    # Add user message to history & display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build messages list in OpenAI format
    messages = [{"role": "system", "content": system_prompt.strip()}]
    
    for msg in st.session_state.messages:
        messages.append({
            "role": "user" if msg["role"] == "user" else "assistant",
            "content": msg["content"]
        })

    # Show assistant "thinking" placeholder
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                completion = client.chat.completions.create(
                    messages=messages,
                    max_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=0.9,
                    stream=False   # set to True later if you want streaming
                )
                
                response_text = completion.choices[0].message.content
                
                # Display the response
                st.markdown(response_text)
                
                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text
                })
                
            except HfHubHTTPError as http_err:
                st.error(f"HTTP Error from HF Inference API: {http_err}")
                if "rate limit" in str(http_err).lower():
                    st.warning("You may have hit the rate limit — wait a minute or upgrade your plan.")
                elif "does not support" in str(http_err):
                    st.error("This model may not support the chat completions endpoint anymore. Try a different repo_id.")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                st.info("Make sure your HF token has access to this model (some require PRO or explicit approval).")

    # Optional: force rerun to refresh layout cleanly
    # st.rerun()