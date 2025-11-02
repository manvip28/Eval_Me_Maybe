import streamlit as st
import os
import json
import tempfile
import subprocess
import sys
from pathlib import Path
from typing import Dict

# Add the parent directory to the path for imports
parent_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(parent_dir))

# Import the web pipeline function
try:
    from generation.pipeline import run_pipeline_web
    print("DEBUG: Successfully imported run_pipeline_web at module level")
except ImportError as e:
    print(f"DEBUG: Import error at module level: {e}")
    run_pipeline_web = None

# Simple file validation functions
def validate_file_type(uploaded_file, allowed_types: list) -> bool:
    """Validate if uploaded file is of allowed type"""
    if uploaded_file is None:
        return False
    file_extension = Path(uploaded_file.name).suffix.lower()
    return file_extension in allowed_types

def check_file_size_limit(uploaded_file, max_size_mb: float = 50.0) -> bool:
    """Check if file size is within limit"""
    if uploaded_file is None:
        return True
    file_size_mb = uploaded_file.size / (1024 * 1024)
    return file_size_mb <= max_size_mb

def process_question_generation(uploaded_file, questions_per_topic: int):
    """Process question generation with progress tracking"""
    try:
        # Initialize progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Save uploaded file
        status_text.text("📁 Saving uploaded file...")
        progress_bar.progress(10)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            temp_file_path = tmp_file.name
        
        # Step 2: Run the pipeline WITHOUT manual review
        status_text.text("🤖 Generating questions...")
        progress_bar.progress(50)
        
        try:
            # Get the parent directory
            parent_dir = Path(__file__).parent.parent.parent.parent
            
            # Call web pipeline function (guaranteed to skip manual review)
            if run_pipeline_web is None:
                st.error("❌ run_pipeline_web function not available. Please check imports.")
                return
            
            print(f"DEBUG: Calling run_pipeline_web (web interface mode)")
            print(f"DEBUG: input_path={temp_file_path}")
            print(f"DEBUG: questions_per_topic={questions_per_topic}")
            print(f"DEBUG: About to call run_pipeline_web function")
            
            try:
                result = run_pipeline_web(
                    input_path=temp_file_path,
                    output_file="temp_questions.json",
                    questions_per_topic=questions_per_topic
                )
                print(f"DEBUG: run_pipeline_web completed, result: {result}")
            except Exception as e:
                print(f"DEBUG: Error calling run_pipeline_web: {e}")
                st.error(f"❌ Error calling run_pipeline_web: {e}")
                return
            
            # Step 3: Load generated questions for manual review
            status_text.text("📝 Loading questions for review...")
            progress_bar.progress(80)
            
            # Load intermediate questions for manual review
            answer_key_gen_dir = parent_dir / "answer_key_gen"
            answer_key_gen_dir.mkdir(exist_ok=True)
            
            intermediate_path = answer_key_gen_dir / "intermediate_questions.json"
            if intermediate_path.exists():
                with open(intermediate_path, 'r', encoding='utf-8') as f:
                    questions = json.load(f)
                
                # Ensure all questions default to pending (approved: False)
                for question in questions:
                    question['approved'] = False
                
                # Store in session state for manual review
                st.session_state.generated_questions = questions
                # Reset documents generated flag since new questions are available
                st.session_state.documents_generated = False
                
                # Step 4: Complete
                status_text.text("✅ Questions ready for review!")
                progress_bar.progress(100)
                
                st.success("🎉 Questions generated successfully!")
                st.info("🔄 Redirecting to Manual Review page...")
                
                # Navigate to manual review page
                st.session_state.current_page = 'manual_review'
                st.rerun()
            else:
                st.error("❌ Could not find generated questions file.")
                
        except Exception as e:
            st.error(f"❌ Error during question generation: {str(e)}")
            st.error("Please check your file format and try again.")
            import traceback
            st.error(f"Full error: {traceback.format_exc()}")
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")

