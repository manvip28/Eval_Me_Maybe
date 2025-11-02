import streamlit as st
import os
import sys
import warnings
import importlib.util
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
# This ensures Azure storage credentials are available before any imports
project_dir = Path(__file__).parent
env_path = project_dir / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try loading from current directory as fallback
    load_dotenv()

# Suppress PyTorch warnings that cause issues with Streamlit
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Change working directory to project root to ensure relative paths work
# (project_dir was already set above when loading .env)
os.chdir(project_dir)

# Import utility functions from streamlit_app directory FIRST
# Note: We need to handle two utils directories:
# 1. Root level: storage (for blob storage)
# 2. Streamlit app level: streamlit_app/utils/ui, utils/pages, etc.
streamlit_app_dir = project_dir / "streamlit_app"
streamlit_app_path = str(streamlit_app_dir)
project_dir_path = str(project_dir)

# CRITICAL: Remove project_dir from path if it exists, then add streamlit_app FIRST
# This ensures utils.ui resolves to streamlit_app/utils/ui, not root utils/
# We also need to remove any cached utils modules
if project_dir_path in sys.path:
    sys.path.remove(project_dir_path)

# Remove cached utils modules that might have been loaded from root
# This includes both 'utils' package and any 'utils.*' submodules
modules_to_remove = [mod for mod in list(sys.modules.keys()) if mod == 'utils' or mod.startswith('utils.')]
for mod in modules_to_remove:
    del sys.modules[mod]

# Ensure streamlit_app is at the very beginning of the path
if streamlit_app_path in sys.path:
    sys.path.remove(streamlit_app_path)
sys.path.insert(0, streamlit_app_path)

# Now add project_dir AFTER streamlit_app for other imports (generation, evaluator, etc.)
sys.path.insert(1, project_dir_path)

try:
    # Verify path order before importing
    # streamlit_app MUST be first, before project_dir
    if sys.path[0] != streamlit_app_path:
        # Force streamlit_app to be first
        if streamlit_app_path in sys.path:
            sys.path.remove(streamlit_app_path)
        sys.path.insert(0, streamlit_app_path)
    
    # Double-check that project_dir is not before streamlit_app
    project_index = sys.path.index(project_dir_path) if project_dir_path in sys.path else -1
    streamlit_index = sys.path.index(streamlit_app_path) if streamlit_app_path in sys.path else -1
    if project_index >= 0 and project_index < streamlit_index:
        # Remove project_dir and re-insert after streamlit_app
        sys.path.remove(project_dir_path)
        sys.path.insert(1, project_dir_path)
    
    # Now import - Python should find streamlit_app/utils/ui since streamlit_app is first
    from utils.ui.styles import load_custom_css
    from utils.pages.components import show_home_page, show_question_generation_page, show_answer_evaluation_page, show_manual_review_page
    
except (ImportError, AttributeError) as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure all dependencies are installed: pip install -r requirements.txt")
    st.error(f"Current working directory: {os.getcwd()}")
    st.error(f"Python path: {sys.path[:5]}")
    st.error(f"Streamlit app dir: {streamlit_app_dir}")
    st.error(f"Streamlit app dir exists: {streamlit_app_dir.exists()}")
    st.error(f"Looking for utils.ui in: {streamlit_app_dir / 'utils' / 'ui'}")
    ui_path = streamlit_app_dir / "utils" / "ui" / "styles.py"
    st.error(f"UI styles file exists: {ui_path.exists()}")
    if ui_path.exists():
        st.error(f"UI styles file path: {ui_path}")
    st.stop()

# Import your existing modules with error handling
try:
    from generation.pipeline import run_pipeline_web
    try:
        from evaluator.answer_evaluator import evaluate_from_json_files
    except ImportError as e:
        st.warning(f"⚠️ Warning: Could not import answer_evaluator: {e}")
        st.warning("Evaluation features may not work properly. Please check your dependencies.")
        evaluate_from_json_files = None
    
    try:
        from evaluator.report_generator import generate_full_report
    except ImportError as e:
        st.warning(f"⚠️ Warning: Could not import report_generator: {e}")
        generate_full_report = None
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.error("Please ensure you're running from the correct directory and all dependencies are installed.")
    import traceback
    st.error(traceback.format_exc())
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

