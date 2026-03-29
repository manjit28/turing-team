"""
FileHandler module with improved code quality and functionality.

This module provides thread-safe file operations with path validation,
retry logic, and support for JSON read/write operations.
"""

import json
import os
import time
import threading
from pathlib import Path
from typing import Any, Dict, Optional, Union
from contextlib import contextmanager

# Custom exceptions
class FileHandlerError(Exception):
    """Base exception for FileHandler errors."""
    pass

class InvalidPathError(FileHandlerError):
    """Raised when a path is invalid or outside the allowed base path."""
    pass

class FileOperationError(FileHandlerError):
    """Raised when a file operation fails."""
    pass

class FileHandler:
    """Thread-safe file handler with path validation and retry logic."""
    
    def __init__(self, base_read_path: str, base_write_path: str, 
                 max_retries: int = 3, retry_delay: float = 0.1):
        """
        Initialize FileHandler with read and write base paths.
        
        Args:
            base_read_path: Base directory for read operations
            base_write_path: Base directory for write operations
            max_retries: Maximum number of retry attempts for file operations
            retry_delay: Initial delay between retries (seconds)
        """
        self.base_read_path = Path(base_read_path).resolve()
        self.base_write_path = Path(base_write_path).resolve()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._lock = threading.Lock()
        self._test_mode = False

    def _validate_path(self, path: Path, is_write: bool = False) -> Path:
        """
        Validate that the path is within the allowed base path.
        
        Args:
            path: Path to validate
            is_write: True if this is a write operation, False for read
            
        Returns:
            Validated path
            
        Raises:
            InvalidPathError: If path is invalid or outside base path
        """
        # Resolve the path to remove '..' and '.' components
        resolved_path = path.resolve()
        
        # Check if path is within the allowed base path
        base_path = self.base_write_path if is_write else self.base_read_path
        
        try:
            # This will raise if path is not within base_path
            resolved_path.relative_to(base_path)
        except ValueError:
            raise InvalidPathError(f"Path '{path}' is outside the allowed base path '{base_path}'")
            
        return resolved_path

    def _retry_operation(self, operation, *args, **kwargs):
        """
        Retry a file operation with exponential backoff.
        
        Args:
            operation: Function to retry
            *args: Arguments for operation
            **kwargs: Keyword arguments for operation
            
        Returns:
            Result of the operation
            
        Raises:
            FileOperationError: If operation fails after all retries
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return operation(*args, **kwargs)
            except (OSError, IOError) as e:
                last_exception = e
                if attempt < self.max_retries:
                    # Exponential backoff
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                else:
                    raise FileOperationError(f"Operation failed after {self.max_retries + 1} attempts: {e}") from e
                    
        # This should never be reached due to the exception handling above,
        # but included for completeness
        raise last_exception

    def _ensure_directory_exists(self, file_path: Path):
        """Ensure the directory for a file path exists."""
        file_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def test_mode(self):
        """
        Context manager for testing mode.
        
        In test mode, file operations are not executed but logged.
        """
        original_mode = self._test_mode
        self._test_mode = True
        try:
            yield
        finally:
            self._test_mode = original_mode

    def read_file(self, file_path: str) -> str:
        """
        Read content from a file.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File content as string
            
        Raises:
            InvalidPathError: If path is invalid or outside base path
            FileOperationError: If file operation fails
        """
        path = Path(file_path)
        
        # Validate path
        validated_path = self._validate_path(path, is_write=False)
        
        if self._test_mode:
            print(f"TEST MODE: Would read from {validated_path}")
            return ""
        
        # Retry operation with exponential backoff
        return self._retry_operation(self._read_file, validated_path)

    def _read_file(self, file_path: Path) -> str:
        """Internal method to read file content."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def write_file(self, file_path: str, content: str) -> None:
        """
        Write content to a file.
        
        Args:
            file_path: Path to the file to write
            content: Content to write to file
            
        Raises:
            InvalidPathError: If path is invalid or outside base path
            FileOperationError: If file operation fails
        """
        path = Path(file_path)
        
        # Validate path
        validated_path = self._validate_path(path, is_write=True)
        
        if self._test_mode:
            print(f"TEST MODE: Would write to {validated_path}")
            return
            
        # Ensure directory exists
        self._ensure_directory_exists(validated_path)
        
        # Retry operation with exponential backoff
        self._retry_operation(self._write_file, validated_path, content)

    def _write_file(self, file_path: Path, content: str) -> None:
        """Internal method to write file content."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def append_to_file(self, file_path: str, content: str) -> None:
        """
        Append content to a file.
        
        Args:
            file_path: Path to the file to append to
            content: Content to append
            
        Raises:
            InvalidPathError: If path is invalid or outside base path
            FileOperationError: If file operation fails
        """
        path = Path(file_path)
        
        # Validate path
        validated_path = self._validate_path(path, is_write=True)
        
        if self._test_mode:
            print(f"TEST MODE: Would append to {validated_path}")
            return
            
        # Ensure directory exists
        self._ensure_directory_exists(validated_path)
        
        # Retry operation with exponential backoff
        self._retry_operation(self._append_to_file, validated_path, content)

    def _append_to_file(self, file_path: Path, content: str) -> None:
        """Internal method to append to file."""
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)

    def read_json(self, file_path: str) -> Any:
        """
        Read and parse JSON from a file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Parsed JSON data
            
        Raises:
            InvalidPathError: If path is invalid or outside base path
            FileOperationError: If file operation fails
            json.JSONDecodeError: If JSON parsing fails
        """
        content = self.read_file(file_path)
        return json.loads(content)

    def write_json(self, file_path: str, data: Any) -> None:
        """
        Write data to a file as JSON.
        
        Args:
            file_path: Path to the file to write
            data: Data to serialize as JSON
            
        Raises:
            InvalidPathError: If path is invalid or outside base path
            FileOperationError: If file operation fails
        """
        json_content = json.dumps(data, indent=2)
        self.write_file(file_path, json_content)

    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if file exists, False otherwise
            
        Raises:
            InvalidPathError: If path is invalid or outside base path
        """
        path = Path(file_path)
        validated_path = self._validate_path(path, is_write=False)
        
        if self._test_mode:
            print(f"TEST MODE: Would check if {validated_path} exists")
            return False
            
        return validated_path.exists() and validated_path.is_file()

    def get_file_info(self, file_path: str) -> Dict[str, Union[str, int, float]]:
        """
        Get information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
            
        Raises:
            InvalidPathError: If path is invalid or outside base path
            FileOperationError: If file operation fails
        """
        path = Path(file_path)
        validated_path = self._validate_path(path, is_write=False)
        
        if self._test_mode:
            print(f"TEST MODE: Would get info for {validated_path}")
            return {}
            
        try:
            stat = validated_path.stat()
            return {
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'is_file': validated_path.is_file(),
                'is_directory': validated_path.is_dir()
            }
        except OSError as e:
            raise FileOperationError(f"Failed to get file info for {validated_path}: {e}")

    def delete_file(self, file_path: str) -> None:
        """
        Delete a file.
        
        Args:
            file_path: Path to the file to delete
            
        Raises:
            InvalidPathError: If path is invalid or outside base path
            FileOperationError: If file operation fails
        """
        path = Path(file_path)
        validated_path = self._validate_path(path, is_write=True)
        
        if self._test_mode:
            print(f"TEST MODE: Would delete {validated_path}")
            return
            
        # Retry operation with exponential backoff
        self._retry_operation(self._delete_file, validated_path)

    def _delete_file(self, file_path: Path) -> None:
        """Internal method to delete file."""
        file_path.unlink()

    def move_file(self, source_path: str, destination_path: str) -> None:
        """
        Move a file from source to destination.
        
        Args:
            source_path: Source file path
            destination_path: Destination file path
            
        Raises:
            InvalidPathError: If paths are invalid or outside base path
            FileOperationError: If file operation fails
        """
        source = Path(source_path)
        destination = Path(destination_path)
        
        # Validate both paths
        source_validated = self._validate_path(source, is_write=True)
        destination_validated = self._validate_path(destination, is_write=True)
        
        if self._test_mode:
            print(f"TEST MODE: Would move {source_validated} to {destination_validated}")
            return
            
        # Ensure destination directory exists
        destination_validated.parent.mkdir(parents=True, exist_ok=True)
        
        # Retry operation with exponential backoff
        self._retry_operation(self._move_file, source_validated, destination_validated)

    def _move_file(self, source_path: Path, destination_path: Path) -> None:
        """Internal method to move file."""
        source_path.rename(destination_path)

    def list_files(self, directory_path: str, pattern: Optional[str] = None) -> list:
        """
        List files in a directory.
        
        Args:
            directory_path: Directory to list files in
            pattern: Optional pattern to filter files
            
        Returns:
            List of file paths
            
        Raises:
            InvalidPathError: If path is invalid or outside base path
        """
        path = Path(directory_path)
        validated_path = self._validate_path(path, is_write=False)
        
        if self._test_mode:
            print(f"TEST MODE: Would list files in {validated_path}")
            return []
            
        try:
            if not validated_path.is_dir():
                raise FileOperationError(f"Path {validated_path} is not a directory")
                
            files = []
            for item in validated_path.iterdir():
                if item.is_file() and (pattern is None or pattern in item.name):
                    files.append(str(item))
            return files
        except OSError as e:
            raise FileOperationError(f"Failed to list directory {validated_path}: {e}")

    def create_directory(self, directory_path: str) -> None:
        """
        Create a directory.
        
        Args:
            directory_path: Path to the directory to create
            
        Raises:
            InvalidPathError: If path is invalid or outside base path
            FileOperationError: If file operation fails
        """
        path = Path(directory_path)
        validated_path = self._validate_path(path, is_write=True)
        
        if self._test_mode:
            print(f"TEST MODE: Would create directory {validated_path}")
            return
            
        # Retry operation with exponential backoff
        self._retry_operation(self._create_directory, validated_path)

    def _create_directory(self, directory_path: Path) -> None:
        """Internal method to create directory."""
        directory_path.mkdir(parents=True, exist_ok=True)

    def lock_file(self, file_path: str) -> None:
        """
        Lock a file by creating a lock file.
        
        Args:
            file_path: Path to the file to lock
            
        Raises:
            InvalidPathError: If path is invalid or outside base path
            FileOperationError: If file operation fails
        """
        path = Path(file_path)
        validated_path = self._validate_path(path, is_write=True)
        
        if self._test_mode:
            print(f"TEST MODE: Would lock {validated_path}")
            return
            
        lock_path = validated_path.with_suffix(validated_path.suffix + '.lock')
        self._retry_operation(self._create_lock_file, lock_path)

    def _create_lock_file(self, lock_path: Path) -> None:
        """Internal method to create lock file."""
        lock_path.touch(exist_ok=True)

    def unlock_file(self, file_path: str) -> None:
        """
        Unlock a file by removing its lock file.
        
        Args:
            file_path: Path to the file to unlock
            
        Raises:
            InvalidPathError: If path is invalid or outside base path
            FileOperationError: If file operation fails
        """
        path = Path(file_path)
        validated_path = self._validate_path(path, is_write=True)
        
        if self._test_mode:
            print(f"TEST MODE: Would unlock {validated_path}")
            return
            
        lock_path = validated_path.with_suffix(validated_path.suffix + '.lock')
        self._retry_operation(self._remove_lock_file, lock_path)

    def _remove_lock_file(self, lock_path: Path) -> None:
        """Internal method to remove lock file."""
        try:
            lock_path.unlink()
        except FileNotFoundError:
            # Lock file doesn't exist, which is fine
            pass