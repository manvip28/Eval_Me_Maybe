"""UI Styles and CSS for Streamlit app"""
import streamlit as st

def load_custom_css():
    """Load and apply custom CSS styles with dark theme"""
    st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global dark theme styles */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
            background-color: #0e1117;
            color: #fafafa;
        }
        
        /* Main header */
        .main-header {
            text-align: center;
            padding: 3rem 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        
        .main-header h1 {
            margin: 0;
            font-size: 3rem;
            font-weight: 700;
            font-family: 'Inter', sans-serif;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .main-header p {
            margin: 1rem 0 0 0;
            font-size: 1.3rem;
            opacity: 0.95;
            font-weight: 400;
        }
        
        /* Feature cards - dark theme */
        .feature-card {
            background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3a 100%);
            padding: 2.5rem;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
            text-align: center;
            transition: all 0.3s ease;
            border: 2px solid #3a3a4a;
            position: relative;
            overflow: hidden;
        }
        
        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-8px);
            border-color: #667eea;
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        }
        
        .feature-card:hover::before {
            transform: scaleX(1);
        }
        
        .feature-card h3 {
            color: #a78bfa;
            margin-bottom: 1.5rem;
            font-size: 1.5rem;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
        }
        
        .feature-card p {
            color: #d1d5db;
            line-height: 1.7;
            font-size: 1rem;
        }
        
        /* Enhanced buttons */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 1rem 2.5rem;
            border-radius: 30px;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            width: 100%;
            font-family: 'Inter', sans-serif;
            text-transform: none;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        }
        
        .stButton > button:active {
            transform: translateY(-1px);
        }
        
        /* Status messages - dark theme */
        .status-success {
            background: linear-gradient(135deg, #1a3a1a 0%, #2d4a2d 100%);
            border: 1px solid #4ade80;
            color: #86efac;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(74, 222, 128, 0.2);
        }
        
        .status-error {
            background: linear-gradient(135deg, #3a1a1a 0%, #4a2d2d 100%);
            border: 1px solid #f87171;
            color: #fca5a5;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(248, 113, 113, 0.2);
        }
        
        .status-info {
            background: linear-gradient(135deg, #1a2a3a 0%, #2d3a4a 100%);
            border: 1px solid #60a5fa;
            color: #93c5fd;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(96, 165, 250, 0.2);
        }
        
        /* Progress indicators - dark theme */
        .progress-container {
            background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3a 100%);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
            margin: 1rem 0;
            border: 1px solid #3a3a4a;
        }
        
        /* Question cards - dark theme */
        .question-card {
            background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3a 100%);
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            border-left: 4px solid #667eea;
            transition: all 0.3s ease;
            border: 2px solid #3a3a4a;
            color: #fafafa;
        }
        
        .question-card:hover {
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            transform: translateY(-2px);
            border-color: #667eea;
        }
        
        .question-card.approved {
            border-left-color: #4ade80;
            background: linear-gradient(135deg, #1a3a1a 0%, #2d4a2d 100%);
            border-color: #3a5a3a;
        }
        
        .question-card.pending {
            border-left-color: #fbbf24;
            background: linear-gradient(135deg, #3a3a1a 0%, #4a4a2d 100%);
            border-color: #5a5a3a;
        }
        
        /* Sidebar styling - dark theme */
        .css-1d391kg {
            background: linear-gradient(180deg, #1e1e2e 0%, #2a2a3a 100%);
        }
        
        /* Streamlit default elements - dark theme */
        .stMarkdown, .stText {
            color: #fafafa !important;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #fafafa !important;
        }
        
        p, li, span, div {
            color: #e5e7eb !important;
        }
        
        /* Streamlit text inputs and text areas */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background-color: #1e1e2e !important;
            color: #fafafa !important;
            border-color: #3a3a4a !important;
        }
        
        /* Streamlit selectboxes */
        .stSelectbox > div > div > select {
            background-color: #1e1e2e !important;
            color: #fafafa !important;
        }
        
        /* Streamlit number inputs */
        .stNumberInput > div > div > input {
            background-color: #1e1e2e !important;
            color: #fafafa !important;
            border-color: #3a3a4a !important;
        }
        
        /* Streamlit checkboxes */
        .stCheckbox > label {
            color: #fafafa !important;
        }
        
        /* Streamlit expander headers */
        .streamlit-expanderHeader {
            color: #fafafa !important;
        }
        
        /* Streamlit metrics */
        .metric-container {
            color: #fafafa !important;
        }
        
        /* Streamlit dataframes */
        .dataframe {
            background-color: #1e1e2e !important;
        }
        
        /* Streamlit success/error/info boxes */
        .stSuccess {
            background-color: #1a3a1a !important;
            border-color: #4ade80 !important;
            color: #86efac !important;
        }
        
        .stError {
            background-color: #3a1a1a !important;
            border-color: #f87171 !important;
            color: #fca5a5 !important;
        }
        
        .stInfo {
            background-color: #1a2a3a !important;
            border-color: #60a5fa !important;
            color: #93c5fd !important;
        }
        
        .stWarning {
            background-color: #3a3a1a !important;
            border-color: #fbbf24 !important;
            color: #fde047 !important;
        }
        
        /* Hide Streamlit's automatic page navigation */
        section[data-testid="stSidebar"] > div:first-child > div:first-child > div > div {
            display: none !important;
        }
        
        div[data-testid="stSidebarNav"] {
            display: none !important;
        }
        
        div[data-testid="stSidebar"] > div:first-child > div:first-child > div:first-child {
            display: none !important;
        }
        
        section[data-testid="stSidebar"] > div:first-child > div:first-child .stRadio {
            display: none !important;
        }
        
        /* File uploader styling - dark theme */
        .stFileUploader > div {
            border: 2px dashed #667eea;
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            transition: all 0.3s ease;
            background-color: #1e1e2e;
        }
        
        .stFileUploader > div:hover {
            border-color: #a78bfa;
            background-color: #2a2a3a;
        }
        
        /* Metrics styling - dark theme */
        .metric-container {
            background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3a 100%);
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            text-align: center;
            margin: 0.5rem;
            border: 1px solid #3a3a4a;
        }
        
        /* Loading animations */
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .loading {
            animation: pulse 2s infinite;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main-header h1 {
                font-size: 2rem;
            }
            
            .main-header p {
                font-size: 1rem;
            }
            
            .feature-card {
                padding: 1.5rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

