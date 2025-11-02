import streamlit as st
import os
import sys
import warnings
from pathlib import Path

# Suppress PyTorch warnings that cause issues with Streamlit
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Add the current directory to the path to import your existing modules
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Change working directory to project root to ensure relative paths work
os.chdir(project_dir)

# Import your existing modules with error handling
try:
    from generation.pipeline import run_pipeline_web
    from evaluator.answer_evaluator import evaluate_from_json_files
    from evaluator.report_generator import generate_full_report
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.error("Please ensure you're running from the correct directory and all dependencies are installed.")
    st.stop()

# Import utility functions from streamlit_app directory
try:
    # Add streamlit_app directory to path for utils
    streamlit_app_dir = project_dir / "streamlit_app"
    sys.path.insert(0, str(streamlit_app_dir))
    
    from utils.ui.styles import load_custom_css
    from utils.pages.components import show_home_page, show_question_generation_page, show_answer_evaluation_page, show_manual_review_page
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure all dependencies are installed: pip install -r requirements.txt")
    st.error(f"Current working directory: {os.getcwd()}")
    st.error(f"Python path: {sys.path[:3]}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="AI Question Generator & Answer Evaluator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set dark theme
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stApp {
        background-color: #0e1117;
    }
    .main {
        background-color: #0e1117;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("## 🎓 Navigation")
        
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = 'home'
        
        if st.button("📝 Question Generation", use_container_width=True):
            st.session_state.current_page = 'question_generation'
        
        if st.button("📊 Answer Evaluation", use_container_width=True):
            st.session_state.current_page = 'answer_evaluation'
        
        if st.button("🔍 Manual Review", use_container_width=True):
            st.session_state.current_page = 'manual_review'
    
    # Main content area
    if st.session_state.current_page == 'home':
        show_home_page()
    elif st.session_state.current_page == 'question_generation':
        show_question_generation_page()
    elif st.session_state.current_page == 'answer_evaluation':
        show_answer_evaluation_page()
    elif st.session_state.current_page == 'manual_review':
        show_manual_review_page()

if __name__ == "__main__":
    main()

