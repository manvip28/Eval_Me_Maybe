"""Evaluation results display components"""
import streamlit as st
import json
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(parent_dir))

def display_all_students_evaluation_results():
    """Display evaluation results for all students"""
    all_results = st.session_state.all_evaluation_results
    
    # Summary of all students
    st.markdown("### 📊 Summary of All Students")
    
    # Create summary table
    summary_data = []
    for idx, results in enumerate(all_results, start=1):
        summary = results.get('summary', {})
        student_name = results.get('student_name', f'Student {idx}')
        summary_data.append({
            'Student': student_name,
            'Total Questions': summary.get('total_questions', 0),
            'Answered': summary.get('answered_questions', 0),
            'Average Score': f"{summary.get('overall_average', 0):.1f}%",
            'Total Score': f"{summary.get('total_achieved_score', 0)}/{summary.get('total_possible_score', 0)}"
        })
    
    # Display summary table
    import pandas as pd
    df = pd.DataFrame(summary_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Display each student's results
    for idx, results in enumerate(all_results, start=1):
        student_name = results.get('student_name', f'Student {idx}')
        student_filename = results.get('student_filename', 'Unknown')
        
        with st.expander(f"📝 Student {idx}: {student_name} ({student_filename})", expanded=False):
            display_single_student_results(results, idx)
    
    # Download report section
    st.markdown("### 📄 Download Combined Report")
    
    # Generate report on button click
    if st.button("📄 Generate & Download Combined Evaluation Report", type="primary"):
        generate_multi_student_evaluation_report()
    
    # Show download button if report is already generated
    if 'multi_student_report_content' in st.session_state and st.session_state.multi_student_report_content:
        st.success("✅ Combined evaluation report is ready for download!")
        
        filename = st.session_state.get('multi_student_report_filename', 'evaluation_report_all_students.docx')
        report_bytes = st.session_state.multi_student_report_content
        mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        
        st.download_button(
            "📥 Download Combined Evaluation Report",
            data=report_bytes,
            file_name=filename,
            mime=mime_type
        )

def display_single_student_results(results, student_idx):
    """Display results for a single student"""
    # Summary statistics
    summary = results.get('summary', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Questions", summary.get('total_questions', 0))
    
    with col2:
        st.metric("Answered Questions", summary.get('answered_questions', 0))
    
    with col3:
        st.metric("Overall Average", f"{summary.get('overall_average', 0)}%")
    
    with col4:
        st.metric("Total Score", f"{summary.get('total_achieved_score', 0)}/{summary.get('total_possible_score', 0)}")
    
    # Detailed results
    st.markdown("#### 📋 Detailed Results")
    
    individual_results = results.get('individual_results', {})
    
    for question_id, result in individual_results.items():
        # Use a container instead of expander to avoid nesting
        percentage_score = result.get('percentage_score', 0)
        
        # Create a toggle key for showing/hiding details
        toggle_key = f"toggle_{student_idx}_{question_id}"
        if toggle_key not in st.session_state:
            st.session_state[toggle_key] = False
        
        # Display question header with score
        col_header, col_toggle = st.columns([5, 1])
        
        with col_header:
            score_color = "#4ade80" if percentage_score >= 70 else "#fbbf24" if percentage_score >= 50 else "#f87171"
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3a 100%); padding: 1rem; border-radius: 8px; border-left: 4px solid {score_color}; margin-bottom: 0.5rem;">
                <h4 style="color: #fafafa; margin: 0;">{question_id}: <span style="color: {score_color};">{percentage_score}%</span></h4>
            </div>
            """, unsafe_allow_html=True)
        
        with col_toggle:
            if st.button("👁️", key=f"btn_{student_idx}_{question_id}", help="Toggle details"):
                st.session_state[toggle_key] = not st.session_state[toggle_key]
                st.rerun()
        
        # Display details if toggle is on
        if st.session_state[toggle_key]:
            with st.container():
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Question:** {result.get('question', '')}")
                    st.markdown(f"**Student Answer:** {result.get('student_answer', '')}")
                
                with col2:
                    st.markdown(f"**Expected Answer:** {result.get('expected_answer', '')}")
                    
                    if result.get('evaluation_details'):
                        details = result['evaluation_details']
                        st.markdown(f"**Semantic Score:** {details.get('semantic_score', 0)}")
                        st.markdown(f"**BLEU Score:** {details.get('bleu', 0)}")
                        st.markdown(f"**ROUGE-L Score:** {details.get('rouge_l', 0)}")
                
                st.markdown("---")

def display_evaluation_results():
    """Display evaluation results in a user-friendly format"""
    results = st.session_state.evaluation_results
    
    # Summary statistics
    summary = results.get('summary', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Questions", summary.get('total_questions', 0))
    
    with col2:
        st.metric("Answered Questions", summary.get('answered_questions', 0))
    
    with col3:
        st.metric("Overall Average", f"{summary.get('overall_average', 0)}%")
    
    with col4:
        st.metric("Total Score", f"{summary.get('total_achieved_score', 0)}/{summary.get('total_possible_score', 0)}")
    
    # Detailed results
    st.markdown("### 📋 Detailed Results")
    
    individual_results = results.get('individual_results', {})
    
    for question_id, result in individual_results.items():
        with st.expander(f"{question_id}: {result.get('percentage_score', 0)}%", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Question:** {result.get('question', '')}")
                st.markdown(f"**Student Answer:** {result.get('student_answer', '')}")
            
            with col2:
                st.markdown(f"**Expected Answer:** {result.get('expected_answer', '')}")
                
                if result.get('evaluation_details'):
                    details = result['evaluation_details']
                    st.markdown(f"**Semantic Score:** {details.get('semantic_score', 0)}")
                    st.markdown(f"**BLEU Score:** {details.get('bleu', 0)}")
                    st.markdown(f"**ROUGE-L Score:** {details.get('rouge_l', 0)}")
    
    # Download report section
    st.markdown("### 📄 Download Report")
    
    # Generate report on button click
    if st.button("📄 Generate & Download Evaluation Report", type="primary"):
        generate_evaluation_report()
    
    # Show download button if report is already generated
    if 'evaluation_report_content' in st.session_state and st.session_state.evaluation_report_content:
        st.success("✅ Evaluation report is ready for download!")
        
        filename = st.session_state.get('evaluation_report_filename', 'evaluation_report.docx')
        report_data = st.session_state.evaluation_report_content
        
        # If it's a string (from old format), encode it, otherwise use binary data directly
        if isinstance(report_data, str):
            report_bytes = report_data.encode('utf-8')
            mime_type = "text/markdown"
        else:
            report_bytes = report_data
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        
        st.download_button(
            "📥 Download Evaluation Report",
            data=report_bytes,
            file_name=filename,
            mime=mime_type
        )

def generate_evaluation_report():
    """Generate and download evaluation report as DOCX using the detailed report_generator"""
    with st.spinner("Generating detailed evaluation report in DOCX format..."):
        try:
            # Import the DOCX report generator
            from evaluator.report_generator import generate_docx_report
            
            # Get results from session state
            results = st.session_state.evaluation_results
            
            # Create a temporary JSON file for the report generator
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp_file:
                json.dump(results, tmp_file, indent=2, ensure_ascii=False)
                tmp_results_path = tmp_file.name
            
            try:
                # Create a temporary output file for the DOCX report
                with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_output:
                    tmp_report_path = tmp_output.name
                
                # Generate the DOCX report using the detailed report generator
                generate_docx_report(tmp_results_path, tmp_report_path)
                
                # Read the generated DOCX report as binary
                with open(tmp_report_path, 'rb') as f:
                    report_content = f.read()
                
                # Store in session state for persistence
                st.session_state.evaluation_report_content = report_content
                st.session_state.evaluation_report_filename = "evaluation_report.docx"
                
                # Success message
                st.success("✅ Detailed evaluation report generated successfully!")
                st.rerun()
                
            finally:
                # Clean up temporary files
                try:
                    os.unlink(tmp_results_path)
                    if os.path.exists(tmp_report_path):
                        os.unlink(tmp_report_path)
                except:
                    pass
            
        except ImportError as e:
            st.error(f"❌ Error importing report generator: {str(e)}")
            st.error("Please ensure evaluator/report_generator.py exists and python-docx is installed.")
        except Exception as e:
            st.error(f"❌ Error generating report: {str(e)}")
            import traceback
            st.error(traceback.format_exc())

def generate_multi_student_evaluation_report():
    """Generate and download combined evaluation report for all students"""
    with st.spinner("Generating combined evaluation report for all students..."):
        try:
            # Import the multi-student report generator
            from evaluator.report_generator import generate_multi_student_docx_report
            
            # Get all results from session state
            all_results = st.session_state.all_evaluation_results
            
            # Create a temporary output file for the DOCX report
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_output:
                tmp_report_path = tmp_output.name
            
            try:
                # Generate the multi-student DOCX report
                generate_multi_student_docx_report(all_results, tmp_report_path)
                
                # Read the generated DOCX report as binary
                with open(tmp_report_path, 'rb') as f:
                    report_content = f.read()
                
                # Store in session state for persistence
                st.session_state.multi_student_report_content = report_content
                st.session_state.multi_student_report_filename = "evaluation_report_all_students.docx"
                
                # Success message
                st.success("✅ Combined evaluation report generated successfully!")
                st.rerun()
                
            finally:
                # Clean up temporary files
                try:
                    if os.path.exists(tmp_report_path):
                        os.unlink(tmp_report_path)
                except:
                    pass
            
        except ImportError as e:
            st.error(f"❌ Error importing report generator: {str(e)}")
            st.error("Please ensure evaluator/report_generator.py exists and python-docx is installed.")
        except Exception as e:
            st.error(f"❌ Error generating report: {str(e)}")
            import traceback
            st.error(traceback.format_exc())

