import streamlit as st
import os
import sys
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
import time
import shutil

# Add the parent directory to the path to import your existing modules
parent_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(parent_dir))

# Change working directory to parent to ensure relative paths work
original_cwd = os.getcwd()
os.chdir(parent_dir)

def convert_file_to_json(input_path: str, file_extension: str, file_type: str) -> Optional[str]:
    """
    Convert different file formats to JSON using the same logic as CLI
    
    Args:
        input_path: Path to the input file
        file_extension: File extension (e.g., '.docx', '.png', '.pdf')
        file_type: Type of file ('student' or 'answer_key')
    
    Returns:
        Path to the converted JSON file, or None if conversion failed
    """
    try:
        # Create temporary output directory
        temp_output_dir = tempfile.mkdtemp()
        
        if file_extension == '.json':
            # File is already JSON, just copy it
            output_path = os.path.join(temp_output_dir, f"{file_type}.json")
            shutil.copy2(input_path, output_path)
            return output_path
        
        # Use the same parsing logic as CLI
        if file_extension in ['.docx', '.png', '.jpg', '.jpeg', '.pdf']:
            # Use parse.py logic (same as CLI)
            final_parsed_path = run_parse_cli_style(input_path, temp_output_dir)
            if final_parsed_path and os.path.exists(final_parsed_path):
                # Load the parsed data
                with open(final_parsed_path, 'r', encoding='utf-8') as f:
                    parsed = json.load(f)
                
                # Transform to evaluator schema (same as CLI)
                transformed = transform_parsed_to_schema(parsed, for_answer_key=(file_type == "answer_key"))
                
                # Save the transformed data
                output_path = os.path.join(temp_output_dir, f"{file_type}.json")
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(transformed, f, indent=2, ensure_ascii=False)
                return output_path
            else:
                st.error(f"❌ Failed to parse {file_extension} file")
                return None
        
        else:
            st.error(f"❌ Unsupported file format: {file_extension}")
            return None
            
    except Exception as e:
        st.error(f"❌ Error converting file: {str(e)}")
        return None

def run_parse_cli_style(input_path: str, output_dir: str) -> Optional[str]:
    """
    Run parse.py logic in the same way as CLI - simplified version
    """
    try:
        input_path_obj = Path(input_path)
        output_dir_obj = Path(output_dir)
        output_dir_obj.mkdir(parents=True, exist_ok=True)
        
        # Use subprocess to run parse.py (same as CLI)
        import subprocess
        import sys
        
        # Run parse.py as subprocess (now in extractor folder)
        cmd = [
            sys.executable,
            "-m", "extractor.parse",  # Run as module
            str(input_path_obj)
        ]
        
        # Set environment variables
        env = os.environ.copy()
        env["CUSTOM_OUTPUT_FOLDER"] = str(output_dir_obj)
        
        # Run the parse command from project root
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=parent_dir, env=env, timeout=300)
        
        if result.returncode == 0:
            # Look for the final_answer.json file
            final_output_file = output_dir_obj / "final_answer.json"
            if final_output_file.exists():
                return str(final_output_file)
            else:
                st.error("❌ parse.py completed but no final_answer.json found")
                return None
        else:
            st.error(f"❌ parse.py failed: {result.stderr}")
            return None
        
    except subprocess.TimeoutExpired:
        st.error("❌ File processing timed out (5 minutes)")
        return None
    except Exception as e:
        st.error(f"❌ Error in parse logic: {str(e)}")
        return None

def transform_parsed_to_schema(parsed: dict, for_answer_key: bool) -> dict:
    """
    Transform parsed structure into evaluator schema (same as CLI)
    """
    transformed: dict = {}
    
    def normalize_qid(raw_qid: str) -> str:
        # Convert variants like "Q1.", "Q1:", " q1 " to canonical "Q1"
        if not raw_qid:
            return raw_qid
        s = str(raw_qid).strip()
        # Remove trailing punctuation like . : ) -
        while len(s) > 0 and s[-1] in ".:)-":
            s = s[:-1].strip()
        # Ensure starts with Q and digits
        if s.lower().startswith('q'):
            s_num = ''.join(ch for ch in s[1:] if ch.isdigit())
            if s_num:
                return f"Q{s_num}"
        # Fallback: leave as-is
        return s
    
    for raw_qid, item in parsed.items():
        qid = normalize_qid(raw_qid)
        if not qid:
            continue
            
        # Extract text content
        text = item.get("text", "") or item.get("Text", "")
        
        # Extract diagram/image
        diagram = item.get("diagram") or item.get("Diagram") or item.get("Image")
        
        # Create transformed entry
        transformed[qid] = {
            "Text": text,
            "diagram": diagram
        }
        
        # For answer keys, add additional metadata
        if for_answer_key:
            transformed[qid].update({
                "Question": item.get("question", "") or item.get("Question", ""),
                "BloomLevel": item.get("bloom", "") or item.get("BloomLevel", "Understand"),
                "Keywords": item.get("keywords", []) or item.get("Keywords", [])
            })
    
    return transformed

def process_question_generation(uploaded_file, questions_per_topic: int):
    """
    Process question generation with enhanced progress tracking
    
    Args:
        uploaded_file: Streamlit uploaded file object
        questions_per_topic: Number of questions per topic
    """
    try:
        # Create a continuous loading indicator
        progress_container = st.container()
        with progress_container:
            st.markdown("### 🚀 Processing Question Generation")
            
            # Create a continuous loading spinner
            loading_placeholder = st.empty()
            status_text = st.empty()
            details_text = st.empty()
            
            # Show initial status
            status_text.text("📁 Loading file from Azure blob storage...")
            
            # Get blob path from session state (should be set during upload)
            blob_path = st.session_state.get('textbook_blob_path')
            
            # Load from Azure blob storage ONLY
            if not blob_path or not blob_path.startswith("uploads/"):
                st.error("❌ Textbook not found in Azure blob storage. Please upload the file again.")
                return
            
            try:
                from storage import get_storage_client
                storage = get_storage_client()
                if not storage.is_blob_storage():
                    st.error("❌ Blob storage is not configured. Please configure Azure storage.")
                    return
                
                if not storage.exists(blob_path):
                    st.error(f"❌ File not found in Azure blob storage: {blob_path}")
                    return
                
                # Download from blob storage to temp file (libraries need local files)
                status_text.text("📥 Downloading file from Azure blob storage...")
                file_data = storage.read_file(blob_path)
                
                # Create temporary file (needed for processing - libraries require local files)
                file_extension = Path(blob_path).suffix or Path(uploaded_file.name).suffix if uploaded_file else ".docx"
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                    tmp_file.write(file_data)
                    temp_file_path = tmp_file.name
                
                status_text.text("✅ File loaded from Azure blob storage")
                details_text.text(f"Processing {blob_path} ({len(file_data)} bytes)")
            except Exception as e:
                st.error(f"❌ Failed to load file from Azure blob storage: {str(e)}")
                import traceback
                with st.expander("🔍 Error Details", expanded=False):
                    st.code(traceback.format_exc())
                return
            
            # Update status
            status_text.text("📚 Extracting topics from textbook...")
            details_text.text("Analyzing document structure and identifying topics...")
            
            # Import and use your existing pipeline
            from generation.pipeline import run_pipeline_web
            
            # Show AI processing status with continuous loading
            status_text.text("🧠 AI is analyzing content and generating questions...")
            details_text.text("Please wait while our AI processes your textbook...")
            
            # Create continuous loading spinner
            loading_html = """
            <div style="display: flex; justify-content: center; align-items: center; padding: 2rem;">
                <div style="display: flex; gap: 0.5rem;">
                    <div style="width: 12px; height: 12px; background: #667eea; border-radius: 50%; animation: pulse 1.5s infinite;"></div>
                    <div style="width: 12px; height: 12px; background: #667eea; border-radius: 50%; animation: pulse 1.5s infinite; animation-delay: 0.3s;"></div>
                    <div style="width: 12px; height: 12px; background: #667eea; border-radius: 50%; animation: pulse 1.5s infinite; animation-delay: 0.6s;"></div>
                </div>
            </div>
            <style>
                @keyframes pulse {
                    0%, 100% { opacity: 0.3; transform: scale(0.8); }
                    50% { opacity: 1; transform: scale(1.2); }
                }
            </style>
            """
            loading_placeholder.markdown(loading_html, unsafe_allow_html=True)
            
            # Run the pipeline (this is the blocking operation)
            try:
                run_pipeline_web(temp_file_path, "temp_questions.json", questions_per_topic)
                
                # Update status after pipeline completion
                status_text.text("📝 Loading generated questions...")
                details_text.text("Processing generated questions...")
                
                # Load the intermediate questions from Azure blob storage ONLY
                intermediate_path_str = "answer_key_gen/intermediate_questions.json"
                questions = None
                
                # Load from Azure blob storage ONLY
                try:
                    import sys
                    project_root = Path(__file__).parent.parent.parent.parent
                    if str(project_root) not in sys.path:
                        sys.path.insert(0, str(project_root))
                    from storage import get_storage_client
                    storage = get_storage_client()
                    
                    if not storage.is_blob_storage():
                        st.error("❌ Blob storage is not configured. Please configure Azure storage.")
                        return
                    
                    if storage.exists(intermediate_path_str):
                        questions = storage.read_json(intermediate_path_str)
                        
                        # Ensure all questions default to approved (approved: True)
                        for question in questions:
                            question['approved'] = True
                        
                        # Store in session state for manual review
                        st.session_state.generated_questions = questions
                        
                        # Clear the loading container and show success
                        progress_container.empty()
                        
                    else:
                        progress_container.empty()
                        st.error(f"❌ Could not find generated questions file in Azure blob storage: {intermediate_path_str}")
                except Exception as e:
                    progress_container.empty()
                    st.error(f"❌ Error loading questions from Azure blob storage: {str(e)}")
                    import traceback
                    with st.expander("🔍 Error Details", expanded=False):
                        st.code(traceback.format_exc())
                    
            except Exception as e:
                progress_container.empty()
                st.error(f"❌ Error during question generation: {str(e)}")
                st.error("Please check your file format and try again.")
            
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.error("Please ensure your file is a valid PDF or DOCX format.")

def process_answer_evaluation(answer_key_file, student_answer_file):
    """
    Process answer evaluation with progress tracking
    
    Args:
        answer_key_file: Streamlit uploaded answer key file
        student_answer_file: Streamlit uploaded student answer file
    """
    try:
        # Initialize progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Upload files to Azure blob storage
        status_text.text("📤 Uploading files to Azure blob storage...")
        progress_bar.progress(10)
        
        # Upload files to Azure blob storage
        from utils.file.handlers import handle_file_upload
        from storage import get_storage_client
        
        answer_key_blob_path = handle_file_upload(answer_key_file, "answer_key")
        student_answer_blob_path = handle_file_upload(student_answer_file, "student_answer")
        
        if not answer_key_blob_path or not student_answer_blob_path:
            st.error("❌ Failed to upload files to Azure blob storage")
            return
        
        # Load files from Azure blob storage for processing
        status_text.text("📥 Loading files from Azure blob storage...")
        progress_bar.progress(20)
        
        storage = get_storage_client()
        if not storage.is_blob_storage():
            st.error("❌ Blob storage is not configured. Please configure Azure storage.")
            return
        
        # Download from blob storage to temp files (libraries need local files)
        answer_key_data = storage.read_file(answer_key_blob_path)
        student_answer_data = storage.read_file(student_answer_blob_path)
        
        # Create temporary files for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(answer_key_file.name).suffix) as tmp_answer_key:
            tmp_answer_key.write(answer_key_data)
            temp_answer_key_path = tmp_answer_key.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(student_answer_file.name).suffix) as tmp_student:
            tmp_student.write(student_answer_data)
            temp_student_path = tmp_student.name
        
        # Step 2: Process files based on type
        status_text.text("🔄 Processing files...")
        progress_bar.progress(30)
        
        # Determine file types and process accordingly
        answer_key_extension = Path(answer_key_file.name).suffix.lower()
        student_extension = Path(student_answer_file.name).suffix.lower()
        
        # Step 3: Convert to JSON if needed
        status_text.text("📝 Converting files to JSON format...")
        progress_bar.progress(50)
        
        # Convert files to JSON format using existing parsing logic
        status_text.text("🔄 Converting student file...")
        converted_student_path = convert_file_to_json(temp_student_path, student_extension, "student")
        
        status_text.text("🔄 Converting answer key file...")
        converted_answer_key_path = convert_file_to_json(temp_answer_key_path, answer_key_extension, "answer_key")
        
        if not converted_student_path or not converted_answer_key_path:
            st.error("❌ Failed to convert files to JSON format.")
            return
        
        # Debug: Check the converted JSON files
        try:
            with open(converted_student_path, 'r', encoding='utf-8') as f:
                student_data = json.load(f)
            with open(converted_answer_key_path, 'r', encoding='utf-8') as f:
                answer_key_data = json.load(f)
            
                
        except Exception as e:
            st.warning(f"⚠️ Debug: Could not read converted JSON files: {str(e)}")
        
        # Step 4: Run evaluation
        status_text.text("📊 Running evaluation...")
        progress_bar.progress(70)
        
        try:
            # Import and use your existing evaluator
            from evaluator.answer_evaluator import evaluate_from_json_files
            
            # Run evaluation with converted JSON files
            results = evaluate_from_json_files(converted_student_path, converted_answer_key_path)
            
            
            if results:
                # Step 5: Store results
                status_text.text("💾 Storing results...")
                progress_bar.progress(90)
                
                st.session_state.evaluation_results = results
                
                # Step 6: Complete
                status_text.text("✅ Evaluation completed!")
                progress_bar.progress(100)
                
                
            else:
                st.error("❌ Evaluation failed. Please check your files and try again.")
                
        except Exception as e:
            st.error(f"❌ Error during evaluation: {str(e)}")
            st.error("Please check your file formats and try again.")
        
        finally:
            # Clean up temporary files
            try:
                os.unlink(temp_answer_key_path)
                os.unlink(temp_student_path)
                # Clean up converted JSON files if they exist
                if 'converted_student_path' in locals() and converted_student_path:
                    os.unlink(converted_student_path)
                if 'converted_answer_key_path' in locals() and converted_answer_key_path:
                    os.unlink(converted_answer_key_path)
            except:
                pass
                
    except Exception as e:
        st.error(f"❌ Error processing files: {str(e)}")
        st.error("Please ensure your files are in the correct format.")

def get_processing_status() -> Dict[str, Any]:
    """
    Get current processing status
    
    Returns:
        Dictionary with processing status information
    """
    status = {
        'question_generation': {
            'in_progress': st.session_state.get('processing', False),
            'questions_generated': len(st.session_state.get('generated_questions', [])),
            'questions_approved': sum(1 for q in st.session_state.get('generated_questions', []) if q.get('approved', False))
        },
        'answer_evaluation': {
            'in_progress': st.session_state.get('evaluating', False),
            'results_available': 'evaluation_results' in st.session_state
        }
    }
    
    return status

def reset_session_state():
    """Reset session state for new session"""
    keys_to_reset = [
        'processing', 'evaluating', 'generated_questions', 
        'evaluation_results'
    ]
    
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    

def get_system_info() -> Dict[str, Any]:
    """
    Get system information and status
    
    Returns:
        Dictionary with system information
    """
    info = {
        'python_version': sys.version,
        'working_directory': os.getcwd(),
        'answer_key_gen_exists': os.path.exists('answer_key_gen'),
        'session_state_keys': list(st.session_state.keys())
    }
    
    return info

