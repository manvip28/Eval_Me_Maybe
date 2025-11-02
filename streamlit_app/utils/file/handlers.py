import streamlit as st
import os
import tempfile
import shutil
from pathlib import Path
import json
from typing import Optional, Dict, Any
import uuid

# Import storage client for persistent file operations
try:
    import sys
    # Add project root to path to find storage (not streamlit_app/utils)
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from storage import get_storage_client, should_use_temp_local
    from dotenv import load_dotenv
    # Load .env file from project root explicitly
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
    else:
        load_dotenv(override=True)
    _storage_available = True
except ImportError:
    _storage_available = False

def handle_file_upload(uploaded_file, file_type: str) -> Optional[str]:
    """
    Handle file upload and save to blob storage or local storage
    
    Args:
        uploaded_file: Streamlit uploaded file object
        file_type: Type of file ('textbook', 'answer_key', 'student_answer')
    
    Returns:
        Blob path or local path to saved file or None if error
    """
    if uploaded_file is None:
        return None
    
    try:
        # Determine file extension
        file_extension = get_file_extension(uploaded_file.name)
        
        # Create unique filename
        filename = f"{file_type}_{uuid.uuid4().hex[:8]}{file_extension}"
        
        # Get file data
        file_data = uploaded_file.getbuffer()
        
        # Try to save to blob storage if available and configured
        if _storage_available:
            try:
                # Force reload to ensure latest env vars are picked up
                import os
                from dotenv import load_dotenv
                # Load from project root explicitly
                env_path = project_root / ".env"
                if env_path.exists():
                    load_dotenv(env_path, override=True)
                else:
                    load_dotenv(override=True)
                
                # Get storage client
                try:
                    storage = get_storage_client(force_reload=True)
                    is_blob = storage.is_blob_storage()
                except Exception as init_error:
                    # Show error during upload
                    st.error(f"❌ **Failed to initialize storage client during upload:** {str(init_error)}")
                    import traceback
                    with st.expander("🔍 Error Details", expanded=False):
                        st.code(traceback.format_exc())
                    raise  # Re-raise to trigger the exception handler below
                
                if is_blob:
                    # Save directly to blob storage
                    blob_path = f"uploads/{file_type}/{filename}"
                    try:
                        # Write to blob storage
                        storage.write_file(blob_path, bytes(file_data))
                        
                        # Verify the file was saved
                        if not storage.exists(blob_path):
                            raise Exception(f"Blob storage write failed - file does not exist after upload")
                        
                        # Show simple success message
                        st.success("File uploaded successfully!")
                        
                        return blob_path  # Return blob path as primary path
                    except Exception as blob_error:
                        # Blob write failed, show detailed error
                        st.error(f"❌ **Failed to save to blob storage:** {str(blob_error)}")
                        import traceback
                        with st.expander("🔍 Blob Storage Error Details", expanded=True):
                            st.code(traceback.format_exc())
                        # Re-raise to trigger fallback to local storage
                        raise
                else:
                    # Local storage - save locally
                    # Show why it's using local storage if blob was expected
                    if storage_type_env == 'blob':
                        st.error(f"❌ **PROBLEM DETECTED:** STORAGE_TYPE is 'blob' but storage client returned local storage.")
                        st.error(f"   This means the StorageClient initialization failed or fell back to local.")
                        st.error(f"   Check your Azure credentials and connection string.")
                        st.error(f"   **Storage Type from client:** `{storage.storage_type}`")
                    else:
                        st.info(f"ℹ️ Using local storage (STORAGE_TYPE is '{storage_type_env}')")
                    
                    # Save to local storage
                    local_dir = Path("local_uploads") / file_type
                    local_dir.mkdir(parents=True, exist_ok=True)
                    local_path = local_dir / filename
                    with open(local_path, "wb") as f:
                        f.write(file_data)
                    
                    return str(local_path)
            except Exception as e:
                error_msg = str(e)
                import traceback
                st.error(f"❌ Failed to save to blob storage: {error_msg}")
                st.error(f"Error details: {traceback.format_exc()}")
                # Fall through to local storage
        
        # Local storage fallback
        local_dir = Path("local_uploads") / file_type
        local_dir.mkdir(parents=True, exist_ok=True)
        file_path = local_dir / filename
        
        with open(file_path, "wb") as f:
            f.write(file_data)
        
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


def save_json_data(data: Dict[Any, Any], filename: str) -> str:
    """
    Save data to JSON file in temporary directory
    
    Args:
        data: Data to save
        filename: Name of the file
    
    Returns:
        Path to saved file
    """
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp_file:
        json.dump(data, tmp_file, indent=2, ensure_ascii=False)
        file_path = tmp_file.name
    
    return file_path

def load_json_data(file_path: str) -> Optional[Dict[Any, Any]]:
    """
    Load data from JSON file (supports both local and blob storage)
    
    Args:
        file_path: Path to JSON file (local path or blob path)
    
    Returns:
        Loaded data or None if error
    """
    try:
        # Temp files should always be local
        if should_use_temp_local(file_path) or not _storage_available:
            # Use local file system
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Try blob storage for persistent files
            storage = get_storage_client()
            if storage.is_blob_storage():
                # Check if it's a blob path or local path
                if Path(file_path).exists():
                    # Local file exists, use it
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                else:
                    # Try blob storage
                    return storage.read_json(file_path)
            else:
                # Local storage, use file system
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
    except FileNotFoundError:
        # If file not found locally, try blob storage if available
        if _storage_available and not should_use_temp_local(file_path):
            try:
                storage = get_storage_client()
                if storage.is_blob_storage() and storage.exists(file_path):
                    return storage.read_json(file_path)
            except Exception:
                pass
        st.error(f"File not found: {file_path}")
        return None
    except Exception as e:
        st.error(f"Error loading JSON file: {str(e)}")
        return None

def create_download_link(file_path: str, filename: str, mime_type: str) -> str:
    """
    Create download link for file (supports both local and blob storage)
    
    Args:
        file_path: Path to file (local path or blob path)
        filename: Name for downloaded file
        mime_type: MIME type for file
    
    Returns:
        Download link
    """
    try:
        # Temp files should always be local
        if should_use_temp_local(file_path) or not _storage_available:
            # Use local file system
            with open(file_path, 'rb') as f:
                file_data = f.read()
        else:
            # Try blob storage for persistent files
            storage = get_storage_client()
            if storage.is_blob_storage():
                # Check if it's a blob path or local path
                if Path(file_path).exists():
                    # Local file exists, use it
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                else:
                    # Try blob storage
                    file_data = storage.read_file(file_path)
            else:
                # Local storage, use file system
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



