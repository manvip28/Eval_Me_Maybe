#!/usr/bin/env python3
"""
Streamlit App Runner
Main entry point for the AI Question Generator & Answer Evaluator web application
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add the parent directory to the path to import your existing modules
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Import the main app
from app import main

if __name__ == "__main__":
    # Set page config
    st.set_page_config(
        page_title="AI Question Generator & Answer Evaluator",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Run the main application
    main()
