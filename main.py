import streamlit as st
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError


load_dotenv()
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

if not hf_token:
    st.error("HUGGINGFACEHUB_API_TOKEN not found in .env file")
    st.stop()


st.set_page_config(
    page_title="NaSCon AI Battle | Jail Break",
    layout="wide",
    page_icon="🔓"
)

st.title("🔓 NaSCon AI Battle: Jail Break Round")
st.caption("Test your prompt engineering skills and try to bypass the target AI's defenses!")


with st.sidebar:
    st.header("Battle Settings")
    
    system_prompt = st.text_area(
        "Target System Defenses (System Prompt)",
        value="",
        height=400,
        help="Tip: Set the baseline defenses for the model you are trying to jailbreak."
    )
    
    max_new_tokens = st.slider("Max new tokens", 256, 2048, 1000, step=64)
    temperature = st.slider("Temperature", 0.0, 1.2, 0.7, 0.05)
    
    if st.button("Reset Battle History", type="primary"):
        st.session_state.messages = []
        st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []


@st.cache_resource
def get_client():
    return InferenceClient(
        model="openai/gpt-oss-120b",
        token=hf_token
    )

client = get_client()


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Enter your jailbreak prompt..."):
    
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    
    messages = [{"role": "system", "content": system_prompt.strip()}]
    
    for msg in st.session_state.messages:
        messages.append({
            "role": "user" if msg["role"] == "user" else "assistant",
            "content": msg["content"]
        })

    
    with st.chat_message("assistant"):
        with st.spinner("Target AI is processing..."):
            try:
                completion = client.chat.completions.create(
                    messages=messages,
                    max_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=0.9,
                    stream=False   
                )
                
                response_text = completion.choices[0].message.content
                
                
                st.markdown(response_text)
                
                
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

    st.rerun()