"""Review interface components for question review"""
import streamlit as st
import json
import html
from pathlib import Path
import os

def review_questions_interface():
    """Interactive manual review interface"""
    questions = st.session_state.generated_questions
    
    if not questions:
        st.warning("⚠️ No questions available for review.")
        return
    
    # Summary statistics
    total_questions = len(questions)
    approved_questions = sum(1 for q in questions if q.get('approved', False))
    pending_questions = total_questions - approved_questions
    
    # Display summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Questions", total_questions)
    
    with col2:
        st.metric("Approved", approved_questions)
    
    with col3:
        st.metric("Pending", pending_questions)
    
    with col4:
        approval_rate = (approved_questions / total_questions * 100) if total_questions > 0 else 0
        st.metric("Approval Rate", f"{approval_rate:.1f}%")
    
    # Filter controls
    st.write("**Filters**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_approved = st.checkbox("Show approved", value=True)
    
    with col2:
        show_pending = st.checkbox("Show pending", value=True)
    
    with col3:
        bloom_filter = st.selectbox(
            "Bloom's level",
            ["All"] + list(set(q.get('bloom', '') for q in questions)),
            index=0
        )
    
    # Question display
    st.write("**Questions**")
    
    # Apply filters
    filtered_questions = []
    for i, question in enumerate(questions):
        # Apply status filter
        if not show_approved and question.get('approved', False):
            continue
        if not show_pending and not question.get('approved', False):
            continue
        
        # Apply Bloom's level filter
        if bloom_filter != "All" and question.get('bloom', '') != bloom_filter:
            continue
        
        filtered_questions.append((i, question))
    
    # Display filtered questions
    for i, question in filtered_questions:
        display_question_review_card(i, question)
    
    # Final actions
    if approved_questions > 0:
        st.write("**Generate Documents**")
        
        # Check if documents are already generated
        if st.session_state.get('documents_generated', False):
            st.success("Documents have been generated successfully!")
            
            # Show download buttons
            col1, col2 = st.columns(2)
            
            with col1:
                question_paper_path = st.session_state.get('question_paper_path')
                if question_paper_path and os.path.exists(question_paper_path):
                    with open(question_paper_path, 'rb') as f:
                        st.download_button(
                            "Download Question Paper",
                            data=f.read(),
                            file_name="question_paper.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error("Question paper not found")
            
            with col2:
                answer_key_path = st.session_state.get('answer_key_path')
                if answer_key_path and os.path.exists(answer_key_path):
                    with open(answer_key_path, 'rb') as f:
                        st.download_button(
                            "Download Answer Key",
                            data=f.read(),
                            file_name="answer_key.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error("Answer key not found")
            
            # Option to regenerate if needed
            if st.button("Regenerate Documents", use_container_width=True):
                st.session_state.documents_generated = False
                st.rerun()
        else:
            if st.button("Generate Final Documents", type="primary", use_container_width=True):
                from utils.document.generator import generate_final_documents
                generate_final_documents()

def display_question_review_card(index: int, question: dict):
    """Display a single question card as a horizontal bar"""
    
    # Determine status
    is_approved = question.get('approved', False)
    status_text = "Approved" if is_approved else "Pending"
    question_text = question.get('question', '')
    keywords = question.get('keywords_used', [])
    bloom_level = question.get('bloom', 'N/A')
    marks = question.get('marks', 'N/A')
    keywords_text = ", ".join(keywords) if keywords else "N/A"
    
    # Wrap everything in a styled box
    card_class = "question-card approved" if is_approved else "question-card pending"
    
    # Escape HTML characters in the text
    safe_question_text = html.escape(question_text)
    safe_keywords_text = html.escape(keywords_text)
    safe_bloom_level = html.escape(str(bloom_level))
    safe_marks = html.escape(str(marks))
    safe_status_text = html.escape(status_text)
    
    # Create wrapper div that spans full width with relative positioning
    st.markdown(f"""
    <div id="question-container-{index}" style="position: relative; margin-bottom: 0.5rem; width: 100%;">
    """, unsafe_allow_html=True)
    
    # Create columns for layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Create the card HTML container with position relative to contain buttons
        st.markdown(f"""
        <div class="{card_class}" id="question-card-{index}" style="padding: 1.5rem; padding-right: 8rem; border: 2px solid #3a3a4a; border-radius: 10px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3); position: relative; margin-bottom: 0.5rem; overflow: visible; background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3a 100%);">
            <div style="margin-bottom: 1rem;">
                <h3 style="color: #a78bfa; margin-bottom: 0.5rem; font-size: 1.2rem;">Question {index+1}:</h3>
                <p style="font-size: 1rem; line-height: 1.6; color: #d1d5db; margin-bottom: 1rem; white-space: pre-wrap;">{safe_question_text}</p>
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 1.5rem; margin-bottom: 1rem; padding-bottom: 1rem; color: #e5e7eb;">
                <div><strong>Bloom's Level:</strong> {safe_bloom_level}</div>
                <div><strong>Marks:</strong> {safe_marks}</div>
                <div><strong>Status:</strong> {safe_status_text}</div>
                <div><strong>Keywords:</strong> {safe_keywords_text}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Position buttons using negative margins to move them inside the card
        # Calculate margins to overlay buttons on card
        st.markdown(f"""
        <div style="margin-top: -240px; margin-left: -110px; position: relative; z-index: 10; display: flex; flex-direction: column; gap: 0.5rem; width: 120px;">
        """, unsafe_allow_html=True)
        
        # Action buttons - positioned inside the card on the right
        if st.button("✏️ Edit", key=f"edit_{index}", use_container_width=True):
            st.session_state[f"edit_modal_open_{index}"] = True
            st.rerun()
        
        if st.button("✅ Approve", key=f"accept_{index}", 
                    use_container_width=True, type="primary"):
            question['approved'] = True
            from utils.document.generator import save_questions_to_file
            save_questions_to_file()
            st.rerun()
        
        if st.button("❌ Reject", key=f"reject_{index}", 
                    use_container_width=True):
            question['approved'] = False
            from utils.document.generator import save_questions_to_file
            save_questions_to_file()
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Close wrapper
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Edit modal/popup
    if st.session_state.get(f"edit_modal_open_{index}", False):
        st.divider()
        st.write("**Edit Question**")
        
        edited_question = st.text_area(
            "Question:",
            value=question_text,
            key=f"edit_text_{index}",
            height=100,
            label_visibility="collapsed"
        )
        
        col_edit1, col_edit2 = st.columns(2)
        
        with col_edit1:
            bloom_options = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
            current_bloom = question.get('bloom', 'Understand')
            try:
                bloom_index = bloom_options.index(current_bloom)
            except ValueError:
                bloom_index = 1
            
            edited_bloom = st.selectbox(
                "Bloom's Level:",
                bloom_options,
                index=bloom_index,
                key=f"edit_bloom_{index}"
            )
        
        with col_edit2:
            edited_marks = st.number_input(
                "Marks:",
                min_value=1,
                max_value=20,
                value=int(question.get('marks', 5)),
                key=f"edit_marks_{index}"
            )
        
        col_save, col_cancel = st.columns(2)
        
        with col_save:
            if st.button("Save", key=f"save_{index}", 
                       use_container_width=True, type="primary"):
                question['question'] = edited_question
                question['bloom'] = edited_bloom
                question['marks'] = edited_marks
                from utils.document.generator import save_questions_to_file
                save_questions_to_file()
                st.session_state[f"edit_modal_open_{index}"] = False
                st.rerun()
        
        with col_cancel:
            if st.button("Cancel", key=f"cancel_{index}", 
                       use_container_width=True):
                st.session_state[f"edit_modal_open_{index}"] = False
                st.rerun()

