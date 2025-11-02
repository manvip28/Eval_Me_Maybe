"""Document generation utilities"""
import streamlit as st
import json
import os
from pathlib import Path

def save_questions_to_file():
    """Save questions back to the intermediate file"""
    try:
        if 'generated_questions' in st.session_state:
            parent_dir = Path(__file__).parent.parent.parent.parent
            answer_key_gen_dir = parent_dir / "answer_key_gen"
            answer_key_gen_dir.mkdir(exist_ok=True)
            
            intermediate_path = answer_key_gen_dir / "intermediate_questions.json"
            with open(intermediate_path, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.generated_questions, f, indent=2, ensure_ascii=False)
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
        
        # Get the parent directory
        parent_dir = Path(__file__).parent.parent.parent.parent
        
        # Save approved questions to final JSON
        final_questions_path = parent_dir / "answer_key_gen" / "final_questions.json"
        os.makedirs(parent_dir / "answer_key_gen", exist_ok=True)
        
        with open(final_questions_path, 'w', encoding='utf-8') as f:
            json.dump(approved_questions, f, indent=2, ensure_ascii=False)
        
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
            
            # Load approved questions
            with open(final_questions_path, 'r', encoding='utf-8') as f:
                questions = json.load(f)
            
            # Generate documents
            question_paper_path = parent_dir / "answer_key_gen" / "question_paper.docx"
            answer_key_path = parent_dir / "answer_key_gen" / "final_answer_key.docx"
            
            save_question_paper_to_docx(questions, str(question_paper_path))
            save_to_docx(questions, str(answer_key_path), None)
            
            # Step 4: Complete
            status_text.text("✅ Documents generated successfully!")
            progress_bar.progress(100)
            
            # Set session state to indicate documents are generated
            st.session_state.documents_generated = True
            st.session_state.question_paper_path = str(question_paper_path)
            st.session_state.answer_key_path = str(answer_key_path)
            
            st.success("🎉 Final documents generated successfully!")
            st.rerun()  # Refresh to show download buttons
                
        except Exception as e:
            st.error(f"❌ Error generating documents: {str(e)}")
            import traceback
            st.error(f"Full error: {traceback.format_exc()}")
        
    except Exception as e:
        st.error(f"❌ Error generating documents: {str(e)}")

