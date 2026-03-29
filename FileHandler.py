"""
FileHandler module for safe file operations with path validation and retry logic.
"""

import os
import json
import threading
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
from contextlib import contextmanager

# Custom exceptions
class FileHandlerError(Exception):
    """Base exception for FileHandler errors."""
    pass

class PathValidationError(FileHandlerError):
    """Raised when path validation fails."""
    pass

class FileHandler:
    """Thread-safe file handler with path validation and retry logic."""
    
    def __init__(self, read_base_path: str = "/tmp", write_base_path: str = "/tmp", 
                 max_retries: int = 3, retry_delay: float = 0.1):
        """
        Initialize FileHandler with base paths for read and write operations.
        
        Args:
            read_base_path: Base path for read operations
            write_base_path: Base path for write operations  
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (seconds)
        """
        self.read_base_path = Path(read_base_path).resolve()
        self.write_base_path = Path(write_base_path).resolve()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._lock = threading.Lock()
        
        # Verify base paths exist
        if not self.read_base_path.exists():
            raise FileHandlerError(f"Read base path does not exist: {self.read_base_path}")
        if not self.write_base_path.exists():
            raise FileHandlerError(f"Write base path does not exist: {self.write_base_path}")

    def _validate_path(self, path: Union[str, Path], is_write: bool = False) -> Path:
        """
        Validate and resolve file path, ensuring it's within the allowed base path.
        
        Args:
            path: Path to validate
            is_write: Whether this is a write operation
            
        Returns:
            Resolved Path object
            
        Raises:
            PathValidationError: If path is invalid or outside allowed scope
        """
        # Convert to Path object if it's a string
        path_obj = Path(path)
        
        # Resolve the path to get absolute path (removes . and ..)
        resolved_path = path_obj.resolve()
        
        # Check if path is within allowed base path
        base_path = self.write_base_path if is_write else self.read_base_path
        
        # Check if the resolved path is within base path
        try:
            resolved_path.relative_to(base_path)
        except ValueError:
            raise PathValidationError(
                f"Path '{path}' is outside allowed base path '{base_path}'"
            )
            
        return resolved_path

    def _retry_operation(self, operation, *args, **kwargs):
        """
        Retry an operation with exponential backoff.
        
        Args:
            operation: Function to retry
            *args: Arguments for operation
            **kwargs: Keyword arguments for operation
            
        Returns:
            Result of operation
            
        Raises:
            Exception: Last exception raised by operation
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    import time
                    time.sleep(self.retry_delay * (2 ** attempt))
                else:
                    # Final attempt - re-raise
                    raise last_exception

    def read_file(self, path: Union[str, Path], encoding: str = "utf-8") -> str:
        """
        Read file content as string.
        
        Args:
            path: Path to file
            encoding: File encoding
            
        Returns:
            File content as string
            
        Raises:
            PathValidationError: If path validation fails
            FileHandlerError: If file cannot be read
        """
        validated_path = self._validate_path(path, is_write=False)
        
        def _read():
            try:
                with open(validated_path, "r", encoding=encoding) as f:
                    return f.read()
            except Exception as e:
                raise FileHandlerError(f"Failed to read file '{validated_path}': {str(e)}")
        
        return self._retry_operation(_read)

    def read_json(self, path: Union[str, Path], encoding: str = "utf-8") -> Any:
        """
        Read JSON file content.
        
        Args:
            path: Path to JSON file
            encoding: File encoding
            
        Returns:
            JSON data
            
        Raises:
            PathValidationError: If path validation fails
            FileHandlerError: If JSON cannot be parsed or file cannot be read
        """
        validated_path = self._validate_path(path, is_write=False)
        
        def _read_json():
            try:
                with open(validated_path, "r", encoding=encoding) as f:
                    return json.load(f)
            except Exception as e:
                raise FileHandlerError(f"Failed to read JSON file '{validated_path}': {str(e)}")
        
        return self._retry_operation(_read_json)

    def write_file(self, path: Union[str, Path], content: str, 
                   encoding: str = "utf-8", mode: str = "w") -> None:
        """
        Write string content to file.
        
        Args:
            path: Path to file
            content: Content to write
            encoding: File encoding
            mode: Write mode ("w" or "a")
            
        Raises:
            PathValidationError: If path validation fails
            FileHandlerError: If file cannot be written
        """
        validated_path = self._validate_path(path, is_write=True)
        
        def _write():
            try:
                with open(validated_path, mode, encoding=encoding) as f:
                    f.write(content)
            except Exception as e:
                raise FileHandlerError(f"Failed to write file '{validated_path}': {str(e)}")
        
        # Use lock for write operations to ensure thread safety
        with self._lock:
            self._retry_operation(_write)

    def write_json(self, path: Union[str, Path], data: Any, 
                   encoding: str = "utf-8", indent: int = 2) -> None:
        """
        Write data as JSON to file.
        
        Args:
            path: Path to JSON file
            data: Data to serialize
            encoding: File encoding
            indent: JSON indentation
            
        Raises:
            PathValidationError: If path validation fails
            FileHandlerError: If data cannot be serialized or file cannot be written
        """
        validated_path = self._validate_path(path, is_write=True)
        
        def _write_json():
            try:
                with open(validated_path, "w", encoding=encoding) as f:
                    json.dump(data, f, indent=indent)
            except Exception as e:
                raise FileHandlerError(f"Failed to write JSON file '{validated_path}': {str(e)}")
        
        # Use lock for write operations to ensure thread safety
        with self._lock:
            self._retry_operation(_write_json)

    def file_exists(self, path: Union[str, Path]) -> bool:
        """
        Check if file exists.
        
        Args:
            path: Path to check
            
        Returns:
            True if file exists, False otherwise
        """
        validated_path = self._validate_path(path, is_write=False)
        return validated_path.exists() and validated_path.is_file()

    def get_file_info(self, path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get file information.
        
        Args:
            path: Path to file
            
        Returns:
            Dictionary with file information
            
        Raises:
            PathValidationError: If path validation fails
            FileHandlerError: If file cannot be accessed
        """
        validated_path = self._validate_path(path, is_write=False)
        
        def _get_info():
            try:
                stat = validated_path.stat()
                return {
                    "size": stat.st_size,
                    "created": stat.st_ctime,
                    "modified": stat.st_mtime,
                    "is_file": validated_path.is_file(),
                    "is_dir": validated_path.is_dir()
                }
            except Exception as e:
                raise FileHandlerError(f"Failed to get file info for '{validated_path}': {str(e)}")
        
        return self._retry_operation(_get_info)

    def append_to_file(self, path: Union[str, Path], content: str, 
                       encoding: str = "utf-8") -> None:
        """
        Append content to file.
        
        Args:
            path: Path to file
            content: Content to append
            encoding: File encoding
            
        Raises:
            PathValidationError: If path validation fails
            FileHandlerError: If file cannot be written
        """
        validated_path = self._validate_path(path, is_write=True)
        
        def _append():
            try:
                with open(validated_path, "a", encoding=encoding) as f:
                    f.write(content)
            except Exception as e:
                raise FileHandlerError(f"Failed to append to file '{validated_path}': {str(e)}")
        
        # Use lock for write operations to ensure thread safety
        with self._lock:
            self._retry_operation(_append)

    def delete_file(self, path: Union[str, Path]) -> None:
        """
        Delete file.
        
        Args:
            path: Path to file
            
        Raises:
            PathValidationError: If path validation fails
            FileHandlerError: If file cannot be deleted
        """
        validated_path = self._validate_path(path, is_write=True)
        
        def _delete():
            try:
                validated_path.unlink()
            except Exception as e:
                raise FileHandlerError(f"Failed to delete file '{validated_path}': {str(e)}")
        
        # Use lock for write operations to ensure thread safety
        with self._lock:
            self._retry_operation(_delete)

    def move_file(self, src: Union[str, Path], dst: Union[str, Path]) -> None:
        """
        Move file from source to destination.
        
        Args:
            src: Source path
            dst: Destination path
            
        Raises:
            PathValidationError: If path validation fails
            FileHandlerError: If file cannot be moved
        """
        src_path = self._validate_path(src, is_write=True)
        dst_path = self._validate_path(dst, is_write=True)
        
        def _move():
            try:
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                src_path.rename(dst_path)
            except Exception as e:
                raise FileHandlerError(f"Failed to move file from '{src_path}' to '{dst_path}': {str(e)}")
        
        # Use lock for write operations to ensure thread safety
        with self._lock:
            self._retry_operation(_move)

    def list_directory(self, path: Union[str, Path]) -> list:
        """
        List directory contents.
        
        Args:
            path: Directory path to list
            
        Returns:
            List of file/directory names
            
        Raises:
            PathValidationError: If path validation fails
            FileHandlerError: If directory cannot be accessed
        """
        validated_path = self._validate_path(path, is_write=False)
        
        def _list():
            try:
                return [f.name for f in validated_path.iterdir()]
            except Exception as e:
                raise FileHandlerError(f"Failed to list directory '{validated_path}': {str(e)}")
        
        return self._retry_operation(_list)

    def create_directory(self, path: Union[str, Path]) -> None:
        """
        Create directory.
        
        Args:
            path: Directory path to create
            
        Raises:
            PathValidationError: If path validation fails
            FileHandlerError: If directory cannot be created
        """
        validated_path = self._validate_path(path, is_write=True)
        
        def _create_dir():
            try:
                validated_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise FileHandlerError(f"Failed to create directory '{validated_path}': {str(e)}")
        
        # Use lock for write operations to ensure thread safety
        with self._lock:
            self._retry_operation(_create_dir)

    @contextmanager
    def lock(self):
        """Context manager for acquiring the internal lock."""
        with self._lock:
            yield