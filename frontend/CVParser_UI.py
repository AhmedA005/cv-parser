import streamlit as st
import requests
from typing import Optional
import json

# Page config
st.set_page_config(
    page_title="CV Parser",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern design
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    .upload-box {
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        margin: 1rem 0;
    }
    .success-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        font-weight: 500;
        margin: 1rem 0;
    }
    .error-box {
        background: linear-gradient(135deg, #f12711 0%, #f5af19 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        font-weight: 500;
        margin: 1rem 0;
    }
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .stJson {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Constants
API_URL = "https://unexpendable-intercounty-tuan.ngrok-free.dev/extract"
API_KEY = "secret123"

# Session state initialization
if 'result' not in st.session_state:
    st.session_state.result = None
if 'error' not in st.session_state:
    st.session_state.error = None

# Header
st.markdown("# 📄 CV Parser")
st.markdown("<p class='subtitle'>Upload your resume and extract structured data instantly</p>", unsafe_allow_html=True)

# File upload section
pdf = st.file_uploader(
    "📎 Drop your PDF here or click to browse",
    type=["pdf"],
    help="Upload a PDF resume to extract information"
)

if pdf:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info(f"📎 **{pdf.name}** ({pdf.size / 1024:.1f} KB)")

# Extract button
if pdf:
    if st.button("🚀 Extract Data", type="primary"):
        with st.spinner("🔄 Processing your CV..."):
            try:
                # API request
                response = requests.post(
                    API_URL,
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    files={"file": (pdf.name, pdf.getvalue(), pdf.type)},
                    timeout=120  # Increased timeout for LLM processing
                )
                
                # Handle response
                if response.status_code == 200:
                    st.session_state.result = response.json()
                    st.session_state.error = None
                    st.markdown("<div class='success-box'>✅ Successfully extracted CV data!</div>", unsafe_allow_html=True)
                else:
                    st.session_state.error = f"API Error: {response.status_code}"
                    st.session_state.result = None
                    
            except requests.exceptions.Timeout:
                st.session_state.error = "Request timed out. Please try again."
                st.session_state.result = None
            except requests.exceptions.RequestException as e:
                st.session_state.error = f"Connection error: {str(e)}"
                st.session_state.result = None
            except json.JSONDecodeError:
                st.session_state.error = "Invalid response format from server"
                st.session_state.result = None

# Display results
if st.session_state.error:
    st.markdown(f"<div class='error-box'>❌ {st.session_state.error}</div>", unsafe_allow_html=True)

if st.session_state.result:
    st.markdown("---")
    st.markdown("### 📊 Extracted Data")
    st.json(st.session_state.result, expanded=True)
    
    # Download button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="💾 Download JSON",
            data=json.dumps(st.session_state.result, indent=2),
            file_name=f"{pdf.name.rsplit('.', 1)[0]}_extracted.json",
            mime="application/json"
        )

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #999; font-size: 0.9rem;'>Powered by AI • Secure & Fast</p>", unsafe_allow_html=True)