"""
Storage abstraction layer supporting both local filesystem and Azure Blob Storage.
Defaults to Azure Blob Storage unless explicitly configured otherwise.
"""
import os
import json
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, BinaryIO, Union
from dotenv import load_dotenv
from abc import ABC, abstractmethod

# Load environment variables from project root
# storage_client.py is in storage/, so project root is 1 level up
_project_root = Path(__file__).parent.parent
_env_path = _project_root / ".env"
if _env_path.exists():
    load_dotenv(_env_path, override=True)
else:
    # Fallback: try to find .env in current directory or parent directories
    load_dotenv(override=True)

# Storage configuration - defaults to Azure Blob Storage
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "blob").lower()  # 'local' or 'blob', defaults to 'blob'
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")


class StorageInterface(ABC):
    """Abstract base class for storage implementations"""
    
    @abstractmethod
    def exists(self, blob_path: str) -> bool:
        """Check if a file/blob exists"""
        pass
    
    @abstractmethod
    def read_file(self, blob_path: str) -> bytes:
        """Read file as bytes"""
        pass
    
    @abstractmethod
    def write_file(self, blob_path: str, data: bytes) -> str:
        """Write file and return path/blob_name"""
        pass
    
    @abstractmethod
    def read_json(self, blob_path: str) -> Dict[Any, Any]:
        """Read JSON file"""
        pass
    
    @abstractmethod
    def write_json(self, blob_path: str, data: Dict[Any, Any]) -> str:
        """Write JSON file and return path/blob_name"""
        pass
    
    @abstractmethod
    def delete_file(self, blob_path: str) -> bool:
        """Delete file"""
        pass
    
    @abstractmethod
    def list_files(self, prefix: str = "") -> list:
        """List files with given prefix"""
        pass
    
    @abstractmethod
    def get_local_path(self, blob_path: str) -> str:
        """Get local file path (downloads from blob if needed, returns path for local)"""
        pass


class LocalStorage(StorageInterface):
    """Local filesystem storage implementation"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()
    
    def _get_full_path(self, blob_path: str) -> Path:
        """Convert blob path to local path"""
        # Remove leading slash if present
        blob_path = blob_path.lstrip('/')
        return self.base_path / blob_path
    
    def exists(self, blob_path: str) -> bool:
        path = self._get_full_path(blob_path)
        return path.exists() and path.is_file()
    
    def read_file(self, blob_path: str) -> bytes:
        path = self._get_full_path(blob_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {blob_path}")
        with open(path, 'rb') as f:
            return f.read()
    
    def write_file(self, blob_path: str, data: bytes) -> str:
        path = self._get_full_path(blob_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)
        return str(path.relative_to(self.base_path))
    
    def read_json(self, blob_path: str) -> Dict[Any, Any]:
        path = self._get_full_path(blob_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {blob_path}")
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def write_json(self, blob_path: str, data: Dict[Any, Any]) -> str:
        path = self._get_full_path(blob_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return str(path.relative_to(self.base_path))
    
    def delete_file(self, blob_path: str) -> bool:
        path = self._get_full_path(blob_path)
        if path.exists():
            path.unlink()
            return True
        return False
    
    def list_files(self, prefix: str = "") -> list:
        base = self._get_full_path(prefix)
        if not base.exists():
            return []
        files = []
        for path in base.rglob("*"):
            if path.is_file():
                rel_path = path.relative_to(self.base_path)
                files.append(str(rel_path).replace('\\', '/'))
        return files
    
    def get_local_path(self, blob_path: str) -> str:
        """For local storage, just return the path"""
        return str(self._get_full_path(blob_path))


class BlobStorage(StorageInterface):
    """Azure Blob Storage implementation"""
    
    def __init__(self, connection_string: str, container_name: str):
        try:
            from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
            self.BlobServiceClient = BlobServiceClient
            self.BlobClient = BlobClient
            self.ContainerClient = ContainerClient
        except ImportError:
            raise ImportError("azure-storage-blob package is required. Install with: pip install azure-storage-blob")
        
        if not connection_string:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING is required for blob storage")
        if not container_name:
            raise ValueError("AZURE_CONTAINER_NAME is required for blob storage")
        
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_name = container_name
        self._ensure_container_exists()
        
        # Cache for downloaded files (to avoid re-downloading)
        self._local_cache: Dict[str, str] = {}
        self._temp_dir = Path(tempfile.gettempdir()) / "blob_cache"
        self._temp_dir.mkdir(exist_ok=True)
    
    def _ensure_container_exists(self):
        """Ensure the container exists, create if it doesn't"""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container()
        except Exception as e:
            raise RuntimeError(f"Failed to ensure container exists: {e}")
    
    def _normalize_path(self, blob_path: str) -> str:
        """Normalize blob path (remove leading slash)"""
        return blob_path.lstrip('/')
    
    def exists(self, blob_path: str) -> bool:
        blob_path = self._normalize_path(blob_path)
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=blob_path
        )
        try:
            return blob_client.exists()
        except Exception:
            return False
    
    def read_file(self, blob_path: str) -> bytes:
        blob_path = self._normalize_path(blob_path)
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=blob_path
        )
        try:
            return blob_client.download_blob().readall()
        except Exception as e:
            raise FileNotFoundError(f"File not found in blob storage: {blob_path}") from e
    
    def write_file(self, blob_path: str, data: bytes) -> str:
        blob_path = self._normalize_path(blob_path)
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=blob_path
        )
        blob_client.upload_blob(data, overwrite=True)
        return blob_path
    
    def read_json(self, blob_path: str) -> Dict[Any, Any]:
        data = self.read_file(blob_path)
        return json.loads(data.decode('utf-8'))
    
    def write_json(self, blob_path: str, data: Dict[Any, Any]) -> str:
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        return self.write_file(blob_path, json_str.encode('utf-8'))
    
    def delete_file(self, blob_path: str) -> bool:
        blob_path = self._normalize_path(blob_path)
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=blob_path
        )
        try:
            blob_client.delete_blob()
            # Remove from cache if exists
            if blob_path in self._local_cache:
                cache_path = Path(self._local_cache[blob_path])
                if cache_path.exists():
                    cache_path.unlink()
                del self._local_cache[blob_path]
            return True
        except Exception:
            return False
    
    def list_files(self, prefix: str = "") -> list:
        prefix = self._normalize_path(prefix)
        container_client = self.blob_service_client.get_container_client(self.container_name)
        files = []
        try:
            for blob in container_client.list_blobs(name_starts_with=prefix):
                files.append(blob.name)
        except Exception:
            pass
        return files
    
    def get_local_path(self, blob_path: str) -> str:
        """Download blob to local temp file and return path"""
        blob_path = self._normalize_path(blob_path)
        
        # Check cache first
        if blob_path in self._local_cache:
            cache_path = Path(self._local_cache[blob_path])
            if cache_path.exists():
                return str(cache_path)
        
        # Download and cache
        data = self.read_file(blob_path)
        cache_path = self._temp_dir / blob_path.replace('/', '_').replace('\\', '_')
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(cache_path, 'wb') as f:
            f.write(data)
        
        self._local_cache[blob_path] = str(cache_path)
        return str(cache_path)


class StorageClient:
    """
    Main storage client that automatically uses local or blob storage
    based on environment configuration.
    """
    
    def __init__(self, storage_type: Optional[str] = None):
        """
        Initialize storage client.
        
        Args:
            storage_type: 'local' or 'blob'. If None, uses STORAGE_TYPE env var or defaults to 'blob' (Azure)
        """
        # Reload env vars to ensure we have the latest values
        # Find project root (where .env file should be)
        # storage_client.py is in storage/, so project root is 1 level up
        project_root = Path(__file__).parent.parent
        env_path = project_root / ".env"
        
        # Debug: Store env path for error messages
        self._env_path = env_path
        
        if env_path.exists():
            load_dotenv(env_path, override=True)
        else:
            # Fallback: try to find .env in current directory or parent directories
            # Try to find .env by walking up the directory tree
            current = Path.cwd()
            found_env = None
            for parent in [current] + list(current.parents):
                potential_env = parent / ".env"
                if potential_env.exists():
                    found_env = potential_env
                    break
            
            if found_env:
                load_dotenv(found_env, override=True)
            else:
                load_dotenv(override=True)
        
        if storage_type is None:
            # Re-read from env after reload - default to blob (Azure)
            storage_type_raw = os.getenv("STORAGE_TYPE", "blob")
            if storage_type_raw:
                # Strip whitespace and quotes
                storage_type = storage_type_raw.strip().strip('"').strip("'").lower()
            else:
                storage_type = "blob"
        
        # Debug: Log what was detected
        # Note: This won't be visible to user but helps with debugging
        
        if storage_type == 'blob':
            # Re-read from env after reload
            connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            if connection_string:
                connection_string = connection_string.strip().strip('"').strip("'")
            container_name = os.getenv("AZURE_CONTAINER_NAME")
            if container_name:
                container_name = container_name.strip().strip('"').strip("'")
            
            if not connection_string:
                raise ValueError(
                    f"Azure Blob Storage requires AZURE_STORAGE_CONNECTION_STRING to be set. "
                    f"Either set the connection string in .env file or use STORAGE_TYPE=local. "
                    f"Checked .env at: {self._env_path} (exists: {self._env_path.exists()})"
                )
            if not container_name:
                raise ValueError(
                    f"Azure Blob Storage requires AZURE_CONTAINER_NAME to be set. "
                    f"Either set the container name in .env file or use STORAGE_TYPE=local. "
                    f"Checked .env at: {self._env_path} (exists: {self._env_path.exists()})"
                )
            try:
                self.storage = BlobStorage(connection_string, container_name)
                self.storage_type = 'blob'
            except Exception as e:
                # Wrap any initialization errors with more context
                raise RuntimeError(
                    f"Failed to initialize Azure Blob Storage: {str(e)}. "
                    f"Please check your connection string and container name. "
                    f".env file location: {self._env_path} (exists: {self._env_path.exists()})"
                ) from e
        else:
            self.storage = LocalStorage()
            self.storage_type = 'local'
    
    def exists(self, path: str) -> bool:
        """Check if file exists"""
        return self.storage.exists(path)
    
    def read_file(self, path: str) -> bytes:
        """Read file as bytes"""
        return self.storage.read_file(path)
    
    def write_file(self, path: str, data: bytes) -> str:
        """Write file and return path/blob_name"""
        return self.storage.write_file(path, data)
    
    def read_json(self, path: str) -> Dict[Any, Any]:
        """Read JSON file"""
        return self.storage.read_json(path)
    
    def write_json(self, path: str, data: Dict[Any, Any]) -> str:
        """Write JSON file and return path/blob_name"""
        return self.storage.write_json(path, data)
    
    def delete_file(self, path: str) -> bool:
        """Delete file"""
        return self.storage.delete_file(path)
    
    def list_files(self, prefix: str = "") -> list:
        """List files with given prefix"""
        return self.storage.list_files(prefix)
    
    def get_local_path(self, path: str) -> str:
        """
        Get local file path. For local storage, returns actual path.
        For blob storage, downloads to temp and returns temp path.
        
        This is useful when you need a file path for libraries that require
        actual file paths (e.g., pdf2image, PIL, etc.)
        """
        return self.storage.get_local_path(path)
    
    def is_blob_storage(self) -> bool:
        """Check if using blob storage"""
        return self.storage_type == 'blob'
    
    def is_local_storage(self) -> bool:
        """Check if using local storage"""
        return self.storage_type == 'local'


# Global storage client instance
_storage_client: Optional[StorageClient] = None


def get_storage_client(force_reload: bool = False) -> StorageClient:
    """
    Get singleton storage client instance.
    
    Args:
        force_reload: Force reload of storage client (useful when env vars change)
    
    Returns:
        StorageClient instance
    """
    global _storage_client
    if _storage_client is None or force_reload:
        _storage_client = StorageClient()
    return _storage_client


def should_use_temp_local(path: str) -> bool:
    """
    Determine if a path should always use local storage (for temp files).
    Temp files should remain local for performance.
    
    Args:
        path: File path
        
    Returns:
        True if path is a temporary file (system temp directory)
    """
    # Check if path is in system temp directory
    import tempfile
    temp_dir = Path(tempfile.gettempdir())
    path_obj = Path(path)
    
    # Check if path is absolute and under temp directory
    if path_obj.is_absolute():
        try:
            # Check if path is relative to temp directory
            path_obj.relative_to(temp_dir)
            return True
        except ValueError:
            # Path is not under temp directory
            pass
    
    # Check for common temp patterns in path string (for backwards compatibility)
    path_lower = path.lower()
    return 'temp' in path_lower or 'tmp' in path_lower

