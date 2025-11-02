import streamlit as st
import os
import json
import tempfile
import subprocess
from pathlib import Path
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add the parent directory to the path to import your existing modules
parent_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(parent_dir))

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

def process_answer_evaluation(answer_key_file, student_answer_file):
    """Process answer evaluation with progress tracking"""
    try:
        # Initialize progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Save uploaded files
        status_text.text("📁 Saving uploaded files...")
        progress_bar.progress(10)
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(answer_key_file.name).suffix) as tmp_answer_key:
            tmp_answer_key.write(answer_key_file.getbuffer())
            temp_answer_key_path = tmp_answer_key.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(student_answer_file.name).suffix) as tmp_student:
            tmp_student.write(student_answer_file.getbuffer())
            temp_student_path = tmp_student.name
        
        # Step 2: Process files
        status_text.text("🔄 Processing files...")
        progress_bar.progress(30)
        
        # Step 3: Run evaluation
        status_text.text("📊 Running evaluation...")
        progress_bar.progress(70)
        
        try:
            # Get the parent directory
            parent_dir = Path(__file__).parent.parent.parent.parent
            
            # Run evaluation using subprocess
            cmd = [
                sys.executable,
                "-m", "evaluator.answer_evaluator",
                temp_student_path,
                temp_answer_key_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=parent_dir)
            
            if result.returncode == 0:
                # Step 4: Complete
                status_text.text("✅ Evaluation completed!")
                progress_bar.progress(100)
                
                st.success("🎉 Evaluation completed successfully!")
                st.info("Check the evaluation results in your project directory.")
                
                # Show output
                with st.expander("📋 Evaluation Output"):
                    st.text(result.stdout)
            else:
                st.error("❌ Error during evaluation:")
                st.error(result.stderr)
                
        except Exception as e:
            st.error(f"❌ Error during evaluation: {str(e)}")
        
        finally:
            # Clean up temporary files
            try:
                os.unlink(temp_answer_key_path)
                os.unlink(temp_student_path)
            except:
                pass
                
    except Exception as e:
        st.error(f"❌ Error processing files: {str(e)}")

def process_multiple_student_evaluations(answer_key_file, student_answer_files):
    """Process evaluation for multiple student answer files"""
    try:
        all_results = []
        total_students = len(student_answer_files)
        
        # Initialize progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Save answer key once
        status_text.text("📁 Saving answer key...")
        progress_bar.progress(5)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(answer_key_file.name).suffix) as tmp_answer_key:
            tmp_answer_key.write(answer_key_file.getbuffer())
            temp_answer_key_path = tmp_answer_key.name
        
        # Determine answer key extension
        answer_key_extension = Path(answer_key_file.name).suffix.lower()
        
        # Convert answer key to JSON once
        status_text.text("🔄 Converting answer key to JSON...")
        progress_bar.progress(10)
        
        from utils.pipeline.integration import convert_file_to_json
        converted_answer_key_path = convert_file_to_json(temp_answer_key_path, answer_key_extension, "answer_key")
        
        if not converted_answer_key_path:
            st.error("❌ Failed to convert answer key to JSON format.")
            return
        
        # Process each student answer
        for idx, student_answer_file in enumerate(student_answer_files):
            student_name = Path(student_answer_file.name).stem
            
            progress = 10 + int((idx / total_students) * 85)
            status_text.text(f"📊 Evaluating Student {idx + 1}/{total_students}: {student_name}...")
            progress_bar.progress(progress)
            
            try:
                # Save student file
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(student_answer_file.name).suffix) as tmp_student:
                    tmp_student.write(student_answer_file.getbuffer())
                    temp_student_path = tmp_student.name
                
                # Convert student file to JSON
                student_extension = Path(student_answer_file.name).suffix.lower()
                converted_student_path = convert_file_to_json(temp_student_path, student_extension, "student")
                
                if not converted_student_path:
                    st.warning(f"⚠️ Failed to convert {student_name} to JSON format. Skipping...")
                    continue
                
                # Run evaluation
                from evaluator.answer_evaluator import evaluate_from_json_files
                results = evaluate_from_json_files(converted_student_path, converted_answer_key_path)
                
                if results:
                    # Add student identifier to results
                    results['student_name'] = student_name
                    results['student_filename'] = student_answer_file.name
                    all_results.append(results)
                
                # Clean up temporary files
                try:
                    os.unlink(temp_student_path)
                    if converted_student_path:
                        os.unlink(converted_student_path)
                except:
                    pass
                    
            except Exception as e:
                st.warning(f"⚠️ Error evaluating {student_name}: {str(e)}")
                continue
        
        # Final cleanup
        try:
            os.unlink(temp_answer_key_path)
            if converted_answer_key_path:
                os.unlink(converted_answer_key_path)
        except:
            pass
        
        # Store all results
        if all_results:
            status_text.text("✅ All evaluations completed!")
            progress_bar.progress(100)
            
            st.session_state.all_evaluation_results = all_results
            st.success(f"🎉 Successfully evaluated {len(all_results)} student(s)!")
            st.info("👆 Check the results in the Evaluation Results section below.")
        else:
            st.error("❌ No evaluations completed successfully.")
        
    except Exception as e:
        st.error(f"❌ Error processing multiple student evaluations: {str(e)}")
        import traceback
        st.error(traceback.format_exc())

def generate_evaluation_report():
    """Generate and download evaluation report"""
    try:
        # Get the parent directory
        parent_dir = Path(__file__).parent.parent.parent.parent
        
        # Check if evaluation results exist
        results_file = parent_dir / "evaluation_results.json"
        if results_file.exists():
            # Generate report using subprocess
            cmd = [
                sys.executable,
                str(parent_dir / "evaluator" / "report_generator.py"),
                "--results", str(results_file),
                "--output", "evaluation_report.md"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=parent_dir)
            
            if result.returncode == 0:
                st.success("🎉 Evaluation report generated successfully!")
                
                # Provide download link
                report_path = parent_dir / "evaluation_report.md"
                if report_path.exists():
                    with open(report_path, 'rb') as f:
                        st.download_button(
                            "📄 Download Evaluation Report",
                            data=f.read(),
                            file_name="evaluation_report.md",
                            mime="text/markdown"
                        )
            else:
                st.error("❌ Error generating report:")
                st.error(result.stderr)
        else:
            st.error("❌ No evaluation results found. Please run evaluation first.")
        
    except Exception as e:
        st.error(f"❌ Error generating report: {str(e)}")

