import streamlit as st
import os
import tempfile
import shutil
from pathlib import Path
import json
from typing import Optional, Dict, Any
import uuid

def handle_file_upload(uploaded_file, file_type: str) -> Optional[str]:
    """
    Handle file upload and save to temporary directory
    
    Args:
        uploaded_file: Streamlit uploaded file object
        file_type: Type of file ('textbook', 'answer_key', 'student_answer')
    
    Returns:
        Path to saved file or None if error
    """
    if uploaded_file is None:
        return None
    
    try:
        # Create temporary directory for this session
        temp_dir = Path("temp_files") / str(uuid.uuid4())
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine file extension
        file_extension = get_file_extension(uploaded_file.name)
        
        # Create unique filename
        filename = f"{file_type}_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = temp_dir / filename
        
        # Save uploaded file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Store in session state for cleanup
        if 'temp_files' not in st.session_state:
            st.session_state.temp_files = []
        st.session_state.temp_files.append(str(file_path))
        
        return str(file_path)
        
    except Exception as e:
        st.error(f"Error handling file upload: {str(e)}")
        return None

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return Path(filename).suffix.lower()

def validate_file_type(uploaded_file, allowed_types: list) -> bool:
    """
    Validate if uploaded file is of allowed type
    
    Args:
        uploaded_file: Streamlit uploaded file object
        allowed_types: List of allowed file extensions
    
    Returns:
        True if valid, False otherwise
    """
    if uploaded_file is None:
        return False
    
    file_extension = get_file_extension(uploaded_file.name)
    return file_extension in allowed_types

def get_file_size_mb(uploaded_file) -> float:
    """Get file size in MB"""
    if uploaded_file is None:
        return 0.0
    return uploaded_file.size / (1024 * 1024)

def check_file_size_limit(uploaded_file, max_size_mb: float = 50.0) -> bool:
    """
    Check if file size is within limit
    
    Args:
        uploaded_file: Streamlit uploaded file object
        max_size_mb: Maximum file size in MB
    
    Returns:
        True if within limit, False otherwise
    """
    if uploaded_file is None:
        return True
    
    file_size_mb = get_file_size_mb(uploaded_file)
    return file_size_mb <= max_size_mb

def cleanup_temp_files():
    """Clean up temporary files"""
    if 'temp_files' in st.session_state:
        for file_path in st.session_state.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    # Also remove parent directory if empty
                    parent_dir = Path(file_path).parent
                    if parent_dir.exists() and not any(parent_dir.iterdir()):
                        parent_dir.rmdir()
            except Exception as e:
                st.warning(f"Could not clean up file {file_path}: {str(e)}")
        
        st.session_state.temp_files = []

def save_json_data(data: Dict[Any, Any], filename: str) -> str:
    """
    Save data to JSON file in temporary directory
    
    Args:
        data: Data to save
        filename: Name of the file
    
    Returns:
        Path to saved file
    """
    temp_dir = Path("temp_files") / str(uuid.uuid4())
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = temp_dir / filename
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Store in session state for cleanup
    if 'temp_files' not in st.session_state:
        st.session_state.temp_files = []
    st.session_state.temp_files.append(str(file_path))
    
    return str(file_path)

def load_json_data(file_path: str) -> Optional[Dict[Any, Any]]:
    """
    Load data from JSON file
    
    Args:
        file_path: Path to JSON file
    
    Returns:
        Loaded data or None if error
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading JSON file: {str(e)}")
        return None

def create_download_link(file_path: str, filename: str, mime_type: str) -> str:
    """
    Create download link for file
    
    Args:
        file_path: Path to file
        filename: Name for downloaded file
        mime_type: MIME type for file
    
    Returns:
        Download link
    """
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        return st.download_button(
            label=f"📄 Download {filename}",
            data=file_data,
            file_name=filename,
            mime=mime_type
        )
    except Exception as e:
        st.error(f"Error creating download link: {str(e)}")
        return None

def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get information about a file
    
    Args:
        file_path: Path to file
    
    Returns:
        Dictionary with file information
    """
    try:
        path_obj = Path(file_path)
        stat = path_obj.stat()
        
        return {
            'name': path_obj.name,
            'size': stat.st_size,
            'size_mb': stat.st_size / (1024 * 1024),
            'extension': path_obj.suffix,
            'exists': path_obj.exists(),
            'modified': stat.st_mtime
        }
    except Exception as e:
        return {
            'name': 'Unknown',
            'size': 0,
            'size_mb': 0,
            'extension': '',
            'exists': False,
            'modified': 0,
            'error': str(e)
        }

def ensure_temp_directory():
    """Ensure temporary directory exists"""
    # Use the streamlit_app directory for temp files
    temp_dir = Path(__file__).parent.parent.parent / "temp_files"
    temp_dir.mkdir(exist_ok=True)
    return temp_dir

def get_temp_directory() -> Path:
    """Get temporary directory path"""
    return ensure_temp_directory()

def cleanup_old_files(max_age_hours: int = 24):
    """
    Clean up old temporary files
    
    Args:
        max_age_hours: Maximum age of files in hours
    """
    temp_dir = get_temp_directory()
    current_time = os.path.getctime(temp_dir)
    
    for file_path in temp_dir.rglob("*"):
        if file_path.is_file():
            try:
                file_age_hours = (current_time - file_path.stat().st_mtime) / 3600
                if file_age_hours > max_age_hours:
                    file_path.unlink()
                    # Remove empty directories
                    parent = file_path.parent
                    while parent != temp_dir and not any(parent.iterdir()):
                        parent.rmdir()
                        parent = parent.parent
            except Exception:
                pass  # Ignore errors during cleanup

