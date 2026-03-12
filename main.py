import streamlit as st

# 1. Page Configuration
st.set_page_config(page_title="Secure Login", page_icon="🔐", layout="centered")

# 2. Custom CSS for "Amazing UI"
# This creates a centered card, styles the buttons, and adds the Google branding
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Login Card Styling */
    .login-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        text-align: center;
    }

    /* Styled Google Button */
    .google-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: white;
        color: #757575;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        cursor: pointer;
        text-decoration: none;
        font-weight: 500;
        margin-top: 10px;
        transition: background-color 0.3s;
    }
    .google-btn:hover {
        background-color: #f1f1f1;
    }
    .google-logo {
        width: 20px;
        margin-right: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. The UI Layout
# Using columns to center the content
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/295/295128.png", width=80) # Replace with your logo
    st.title("Welcome Back")
    st.caption("Please enter your details to continue")

    # Native Streamlit Inputs (Inside the "Card")
    username = st.text_input("Username", placeholder="e.g. jdoe")
    password = st.text_input("Password", type="password", placeholder="••••••••")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Login Button Logic
    if st.button("Sign In", use_container_width=True, type="primary"):
        # YOUR AUTH CODE GOES HERE
        st.success(f"Logging in {username}...")

    # Divider
    st.markdown('<div style="text-align: center; margin: 15px 0; color: #888;">OR</div>', unsafe_allow_html=True)

    # 4. Google Login Button (Styled HTML)
    # Note: Since you're writing the auth, you'll need to wrap this in a link 
    # or use a streamlit-clickable-component to trigger your Google OAuth flow.
    google_button_html = """
        <a href="#" class="google-btn">
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" class="google-logo">
            Continue with Google
        </a>
    """
    st.markdown(google_button_html, unsafe_allow_html=True)
    
    st.markdown("<br><p style='text-align: center; font-size: 12px;'>Don't have an account? <a href='#'>Sign up</a></p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)