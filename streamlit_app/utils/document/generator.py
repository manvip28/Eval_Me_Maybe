"""Document generation utilities"""
import streamlit as st
import json
import os
from pathlib import Path

# Import storage client for persistent file operations
try:
    import sys
    # Add project root to path to find storage (not streamlit_app/utils)
    project_root = Path(__file__).parent.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from storage import get_storage_client, should_use_temp_local
    _storage_available = True
except ImportError:
    _storage_available = False

def save_questions_to_file():
    """Save questions back to the intermediate file"""
    try:
        if 'generated_questions' in st.session_state:
            intermediate_path_str = "answer_key_gen/intermediate_questions.json"
            
            # Save to Azure blob storage ONLY
            if not _storage_available:
                st.error("❌ Storage client not available. Please configure Azure storage.")
                return
            
            try:
                storage = get_storage_client()
                if not storage.is_blob_storage():
                    st.error("❌ Blob storage is not configured. Please configure Azure storage.")
                    return
                
                # Save directly to blob storage
                storage.write_json(intermediate_path_str, st.session_state.generated_questions)
                return
            except Exception as e:
                st.error(f"❌ Failed to save to blob storage: {str(e)}")
                import traceback
                with st.expander("🔍 Error Details", expanded=False):
                    st.code(traceback.format_exc())
    except Exception as e:
        st.error(f"Error saving questions: {str(e)}")

def generate_final_documents():
    """Generate final question paper and answer key documents"""
    try:
        if 'generated_questions' not in st.session_state:
            st.error("❌ No questions available to generate documents.")
            return
        
        questions = st.session_state.generated_questions
        approved_questions = [q for q in questions if q.get('approved', False)]
        
        if not approved_questions:
            st.error("❌ No approved questions available. Please approve some questions first.")
            return
        
        # Initialize progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Save approved questions
        status_text.text("💾 Saving approved questions...")
        progress_bar.progress(20)
        
        # Save approved questions to final JSON - Azure blob storage ONLY
        final_questions_path_str = "answer_key_gen/final_questions.json"
        
        # Save to blob storage ONLY
        if not _storage_available:
            st.error("❌ Storage client not available. Please configure Azure storage.")
            return
        
        try:
            storage = get_storage_client()
            if not storage.is_blob_storage():
                st.error("❌ Blob storage is not configured. Please configure Azure storage.")
                return
            
            # Save directly to blob storage
            storage.write_json(final_questions_path_str, approved_questions)
        except Exception as e:
            st.error(f"❌ Failed to save to blob storage: {str(e)}")
            import traceback
            with st.expander("🔍 Error Details", expanded=False):
                st.code(traceback.format_exc())
            return
        
        # Step 2: Generate question paper
        status_text.text("📄 Generating question paper...")
        progress_bar.progress(40)
        
        # Step 3: Generate answer key
        status_text.text("📋 Generating answer key...")
        progress_bar.progress(60)
        
        # Generate documents directly (no subprocess)
        try:
            # Import and use your existing document generation
            from generation.pipeline import save_question_paper_to_docx, save_to_docx
            
            # Load approved questions from Azure blob storage ONLY
            questions = None
            
            if not _storage_available:
                st.error("❌ Storage client not available. Please configure Azure storage.")
                return
            
            try:
                storage = get_storage_client()
                if not storage.is_blob_storage():
                    st.error("❌ Blob storage is not configured. Please configure Azure storage.")
                    return
                
                if storage.exists(final_questions_path_str):
                    # Load from blob storage
                    questions = storage.read_json(final_questions_path_str)
                else:
                    st.error(f"❌ Could not find questions file in Azure blob storage: {final_questions_path_str}")
                    return
            except Exception as e:
                st.error(f"❌ Failed to load from blob storage: {str(e)}")
                import traceback
                with st.expander("🔍 Error Details", expanded=False):
                    st.code(traceback.format_exc())
                return
            
            # Generate documents - save to blob storage if available
            question_paper_path_str = "answer_key_gen/question_paper.docx"
            answer_key_path_str = "answer_key_gen/final_answer_key.docx"
            
            # For document generation, we need local temp files first
            # Then upload to blob storage
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_qp:
                temp_qp_path = tmp_qp.name
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_ak:
                temp_ak_path = tmp_ak.name
            
            try:
                # Generate to temp files
                save_question_paper_to_docx(questions, temp_qp_path)
                save_to_docx(questions, temp_ak_path, None)
                
                # Upload to Azure blob storage ONLY
                if not _storage_available:
                    st.error("❌ Storage client not available. Please configure Azure storage.")
                    return
                
                try:
                    storage = get_storage_client()
                    if not storage.is_blob_storage():
                        st.error("❌ Blob storage is not configured. Please configure Azure storage.")
                        return
                    
                    # Read temp files and upload to blob
                    with open(temp_qp_path, 'rb') as f:
                        storage.write_file(question_paper_path_str, f.read())
                    with open(temp_ak_path, 'rb') as f:
                        storage.write_file(answer_key_path_str, f.read())
                    # Store blob paths in session state
                    question_paper_path = question_paper_path_str
                    answer_key_path = answer_key_path_str
                except Exception as e:
                    st.error(f"❌ Failed to save documents to blob storage: {str(e)}")
                    import traceback
                    with st.expander("🔍 Error Details", expanded=False):
                        st.code(traceback.format_exc())
                    return
            finally:
                # Clean up temp files
                try:
                    if os.path.exists(temp_qp_path):
                        os.unlink(temp_qp_path)
                    if os.path.exists(temp_ak_path):
                        os.unlink(temp_ak_path)
                except:
                    pass
            
            # Step 4: Complete
            status_text.text("✅ Documents generated successfully!")
            progress_bar.progress(100)
            
            # Set session state to indicate documents are generated
            st.session_state.documents_generated = True
            st.session_state.question_paper_path = str(question_paper_path)
            st.session_state.answer_key_path = str(answer_key_path)
            
            st.rerun()  # Refresh to show download buttons
                
        except Exception as e:
            st.error(f"❌ Error generating documents: {str(e)}")
            import traceback
            st.error(f"Full error: {traceback.format_exc()}")
        
    except Exception as e:
        st.error(f"❌ Error generating documents: {str(e)}")

