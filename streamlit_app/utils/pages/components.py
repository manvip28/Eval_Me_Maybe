"""Page display components for the Streamlit app"""
import streamlit as st

def show_home_page():
    """Display the home page with enhanced feature cards and visual elements"""
    st.markdown("""
    <div class="main-header">
        <h1>🎓 AI Question Generator & Answer Evaluator</h1>
        <p>Transform textbooks into questions and evaluate student answers with AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome message with stats
    st.markdown("### 🎯 Welcome to Your AI-Powered Education Assistant")
    st.markdown("Generate high-quality questions from any textbook and evaluate student answers with advanced AI technology.")
    
    # Feature cards with enhanced styling
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📝 Question Generation</h3>
            <p>Upload your textbook and generate comprehensive questions with manual review capabilities. Get both question papers and answer keys in DOCX format.</p>
            <div style="margin-top: 1.5rem;">
                <span style="background: #1e3a5e; color: #93c5fd; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; margin-right: 0.5rem;">PDF & DOCX</span>
                <span style="background: #3a1a4a; color: #d8b4fe; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; margin-right: 0.5rem;">AI-Powered</span>
                <span style="background: #1a3a1a; color: #86efac; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">Manual Review</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Start Question Generation", use_container_width=True):
            st.session_state.current_page = 'question_generation'
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Answer Evaluation</h3>
            <p>Upload answer keys and student answers to get detailed evaluation reports with scores, feedback, and comprehensive analysis.</p>
            <div style="margin-top: 1.5rem;">
                <span style="background: #3a2a1a; color: #fbbf24; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; margin-right: 0.5rem;">Multi-Format</span>
                <span style="background: #1a2a3a; color: #60a5fa; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; margin-right: 0.5rem;">Detailed Reports</span>
                <span style="background: #3a1a2a; color: #f472b6; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">AI Analysis</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📈 Start Answer Evaluation", use_container_width=True):
            st.session_state.current_page = 'answer_evaluation'
            st.rerun()
    
    
    # Features overview with enhanced styling
    st.markdown("---")
    st.markdown("## ✨ Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3a 100%); padding: 2rem; border-radius: 15px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3); height: 100%; border: 1px solid #3a3a4a;">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🤖</div>
                <h3 style="color: #a78bfa; margin: 0;">AI-Powered</h3>
            </div>
            <ul style="color: #d1d5db; line-height: 1.8; margin: 0; padding-left: 1.2rem;">
                <li>Advanced NLP for question generation</li>
                <li>Bloom's taxonomy classification</li>
                <li>Semantic similarity evaluation</li>
                <li>Image comparison capabilities</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3a 100%); padding: 2rem; border-radius: 15px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3); height: 100%; border: 1px solid #3a3a4a;">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📚</div>
                <h3 style="color: #4ade80; margin: 0;">Multiple Formats</h3>
            </div>
            <ul style="color: #d1d5db; line-height: 1.8; margin: 0; padding-left: 1.2rem;">
                <li>PDF and DOCX textbook support</li>
                <li>JSON and DOCX answer keys</li>
                <li>Student answers in multiple formats</li>
                <li>Automatic format detection</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3a 100%); padding: 2rem; border-radius: 15px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3); height: 100%; border: 1px solid #3a3a4a;">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
                <h3 style="color: #fbbf24; margin: 0;">Manual Review</h3>
            </div>
            <ul style="color: #d1d5db; line-height: 1.8; margin: 0; padding-left: 1.2rem;">
                <li>Interactive question review</li>
                <li>Approve/reject/edit questions</li>
                <li>Real-time filtering</li>
                <li>Quality control interface</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    

def show_question_generation_page():
    """Display the question generation page with single column layout"""
    st.markdown("# 📝 Question Generation")
    st.markdown("Generate questions from your textbook with AI assistance and manual review capabilities.")
    
    # Single column layout
    st.markdown("### 📁 Upload & Configuration")
    
    # File upload section
    uploaded_file = st.file_uploader(
        "Upload PDF/DOCX",
        type=['pdf', 'docx'],
        help="Upload a PDF or DOCX file containing your textbook content",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        st.success("✅ File uploaded successfully and ready for processing.")
        
        # Configuration section
        st.markdown("#### ⚙️ Configuration")
        questions_per_topic = st.number_input(
            "Questions per topic",
            min_value=1,
            max_value=10,
            value=2,
            help="Number of questions to generate for each topic found in the textbook"
        )
        
        # Process button
        if st.button("🚀 Generate Questions", type="primary", use_container_width=True):
            if 'processing' not in st.session_state:
                st.session_state.processing = False
            
            if not st.session_state.processing:
                st.session_state.processing = True
                from utils.pipeline.integration import process_question_generation
                process_question_generation(uploaded_file, questions_per_topic)
        
    # Manual review section (if questions are generated) - Full width
    if 'generated_questions' in st.session_state and st.session_state.generated_questions:
        st.divider()
        st.write("## Manual Review")
        
        # Review interface
        from utils.review.components import review_questions_interface
        review_questions_interface()

def show_answer_evaluation_page():
    """Display the answer evaluation page"""
    st.markdown("# 📊 Answer Evaluation")
    st.markdown("Upload answer keys and student answers to get detailed evaluation reports.")
    
    # File upload section
    st.markdown("## 📁 Upload Files")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Answer Key")
        answer_key_file = st.file_uploader(
            "Upload answer key",
            type=['json', 'docx'],
            help="Upload answer key in JSON or DOCX format"
        )
        
        if answer_key_file:
            st.success(f"✅ Answer key uploaded: {answer_key_file.name}")
    
    with col2:
        st.markdown("### 📝 Student Answer(s)")
        student_answer_files = st.file_uploader(
            "Upload student answer(s)",
            type=['pdf', 'docx', 'json', 'png', 'jpg', 'jpeg'],
            help="Upload one or more student answers in any supported format",
            accept_multiple_files=True
        )
        
        if student_answer_files:
            if len(student_answer_files) == 1:
                st.success(f"✅ Student answer uploaded: {student_answer_files[0].name}")
            else:
                st.success(f"✅ {len(student_answer_files)} student answers uploaded:")
                for file in student_answer_files:
                    st.text(f"   • {file.name}")
    
    # Process evaluation
    if answer_key_file and student_answer_files:
        st.markdown("## 🚀 Process Evaluation")
        
        if st.button("📊 Evaluate Answers", type="primary", use_container_width=True):
            if 'evaluating' not in st.session_state:
                st.session_state.evaluating = False
            
            if not st.session_state.evaluating:
                st.session_state.evaluating = True
                from utils.evaluation.utils import process_multiple_student_evaluations
                process_multiple_student_evaluations(answer_key_file, student_answer_files)
    
    # Display results if available
    if 'all_evaluation_results' in st.session_state and st.session_state.all_evaluation_results:
        st.markdown("---")
        st.markdown("## 📈 Evaluation Results")
        from utils.evaluation.display import display_all_students_evaluation_results
        display_all_students_evaluation_results()

def show_manual_review_page():
    """Dedicated manual review page with tick, cross, and edit buttons"""
    from utils.review.components import display_question_review_card
    from utils.document.generator import generate_final_documents, save_questions_to_file
    import os
    
    # Page header
    st.markdown("# 🔍 Manual Review")
    st.markdown("Review and approve the generated questions before creating the final documents.")
    
    # Check if questions are available
    if 'generated_questions' not in st.session_state or not st.session_state.generated_questions:
        st.warning("⚠️ No questions available for review.")
        st.info("Please generate questions first using the Question Generation page.")
        
        if st.button("📝 Go to Question Generation", type="primary"):
            st.session_state.current_page = 'question_generation'
            st.rerun()
        return
    
    questions = st.session_state.generated_questions
    
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
    st.markdown("### 🔍 Filter Questions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_approved = st.checkbox("Show approved", value=True)
    
    with col2:
        show_pending = st.checkbox("Show pending", value=True)
    
    with col3:
        bloom_filter = st.selectbox(
            "Filter by Bloom's level",
            ["All"] + list(set(q.get('bloom', '') for q in questions)),
            index=0
        )
    
    # Bulk actions
    st.markdown("### 🔧 Bulk Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Approve All", use_container_width=True):
            for question in questions:
                question['approved'] = True
            save_questions_to_file()
            st.rerun()
    
    with col2:
        if st.button("❌ Reject All", use_container_width=True):
            for question in questions:
                question['approved'] = False
            save_questions_to_file()
            st.rerun()
    
    with col3:
        if st.button("🔄 Reset All", use_container_width=True):
            for question in questions:
                question['approved'] = False
            save_questions_to_file()
            st.rerun()
    
    # Question display
    st.markdown("### 📝 Questions")
    
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
        # Check if documents are already generated
        if st.session_state.get('documents_generated', False):
            st.markdown("### 📄 Download Final Documents")
            st.success("✅ Documents have been generated successfully!")
            
            # Show download buttons
            col1, col2 = st.columns(2)
            
            with col1:
                question_paper_path = st.session_state.get('question_paper_path')
                if question_paper_path and os.path.exists(question_paper_path):
                    with open(question_paper_path, 'rb') as f:
                        st.download_button(
                            "📄 Download Question Paper",
                            data=f.read(),
                            file_name="question_paper.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error("❌ Question paper not found")
            
            with col2:
                answer_key_path = st.session_state.get('answer_key_path')
                if answer_key_path and os.path.exists(answer_key_path):
                    with open(answer_key_path, 'rb') as f:
                        st.download_button(
                            "📄 Download Answer Key",
                            data=f.read(),
                            file_name="answer_key.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error("❌ Answer key not found")
            
            # Option to regenerate if needed
            if st.button("🔄 Regenerate Documents", use_container_width=True):
                st.session_state.documents_generated = False
                st.rerun()
        else:
            st.markdown("### 📄 Generate Final Documents")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📄 Generate Question Paper", type="primary", use_container_width=True):
                    generate_final_documents()
            
            with col2:
                st.markdown(f"**Ready to generate:** {approved_questions} approved questions")

