import os
import json
import logging
import threading
from pathlib import Path
from typing import Any, Optional, Union

class FileHandlerError(Exception):
    """Base exception for file handling errors."""
    pass

class PathValidationError(FileHandlerError):
    """Raised when a path fails validation checks."""
    pass

class FileHandler:
    """A utility class for robust file operations with error handling and logging.

    This class provides thread-safe file operations with configurable base paths,
    retry logic, and comprehensive error handling.

    Args:
        read_base_path: Base directory for read operations. Defaults to current working directory.
        write_base_path: Base directory for write operations. Defaults to current working directory.
        max_retries: Maximum number of retry attempts for failed operations. Defaults to 3.
        retry_backoff: Initial backoff time in seconds for retries. Defaults to 1.
    """

    def __init__(
        self,
        read_base_path: Optional[str] = None,
        write_base_path: Optional[str] = None,
        max_retries: int = 3,
        retry_backoff: float = 1.0
    ):
        self.read_base_path = Path(read_base_path) if read_base_path else Path.cwd()
        self.write_base_path = Path(write_base_path) if write_base_path else Path.cwd()
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self._lock = threading.Lock()
        self.logger = logging.getLogger("agent_system")

    def _validate_path(self, path: Path, is_write: bool = False) -> Path:
        """Validate and resolve a path against the appropriate base path.

        Args:
            path: The path to validate.
            is_write: If True, validate against write_base_path; otherwise read_base_path.

        Returns:
            The resolved path.

        Raises:
            PathValidationError: If the path is invalid or outside the allowed base path.
        """
        base_path = self.write_base_path if is_write else self.read_base_path
        
        # Resolve the path relative to the base
        try:
            resolved_path = (base_path / path).resolve()
        except Exception as e:
            raise PathValidationError(f"Invalid path '{path}': {str(e)}")
        
        # Check if the resolved path is within the base path
        try:
            resolved_path.relative_to(base_path)
        except ValueError:
            raise PathValidationError(
                f"Path '{path}' is outside the allowed base path '{base_path}'"
            )
        
        return resolved_path

    def _retry_operation(self, operation, *args, **kwargs):
        """Execute an operation with retry logic.

        Args:
            operation: The function to execute.
            *args: Arguments for the operation.
            **kwargs: Keyword arguments for the operation.

        Returns:
            The result of the operation.

        Raises:
            FileHandlerError: If all retry attempts fail.
        """
        import time
        
        for attempt in range(self.max_retries + 1):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries:
                    raise FileHandlerError(
                        f"Operation failed after {self.max_retries + 1} attempts: {str(e)}"
                    ) from e
                
                self.logger.warning(
                    f"Operation failed on attempt {attempt + 1}: {str(e)}. Retrying in {self.retry_backoff * (2 ** attempt)}s..."
                )
                time.sleep(self.retry_backoff * (2 ** attempt))

    def read_text(self, path: str) -> str:
        """Read text content from a file.

        Args:
            path: Path to the file to read.

        Returns:
            The content of the file as a string.

        Raises:
            FileHandlerError: If the file cannot be read.
        """
        def _read_text_operation():
            try:
                resolved_path = self._validate_path(Path(path))
                with self._lock:
                    return resolved_path.read_text()
            except Exception as e:
                raise FileHandlerError(f"Failed to read text file '{path}': {str(e)}") from e
        
        return self._retry_operation(_read_text_operation)

    def write_text(self, path: str, content: str) -> None:
        """Write text content to a file.

        Args:
            path: Path to the file to write.
            content: The text content to write.

        Raises:
            FileHandlerError: If the file cannot be written.
        """
        def _write_text_operation():
            try:
                resolved_path = self._validate_path(Path(path), is_write=True)
                resolved_path.parent.mkdir(parents=True, exist_ok=True)
                with self._lock:
                    resolved_path.write_text(content)
            except Exception as e:
                raise FileHandlerError(f"Failed to write text file '{path}': {str(e)}") from e
        
        self._retry_operation(_write_text_operation)

    def read_json(self, path: str) -> Any:
        """Read JSON content from a file.

        Args:
            path: Path to the JSON file to read.

        Returns:
            The parsed JSON data.

        Raises:
            FileHandlerError: If the file cannot be read or parsed.
        """
        def _read_json_operation():
            try:
                resolved_path = self._validate_path(Path(path))
                with self._lock:
                    content = resolved_path.read_text()
                    return json.loads(content)
            except Exception as e:
                raise FileHandlerError(f"Failed to read or parse JSON file '{path}': {str(e)}") from e
        
        return self._retry_operation(_read_json_operation)

    def write_json(self, path: str, data: Any) -> None:
        """Write data to a JSON file.

        Args:
            path: Path to the JSON file to write.
            data: The data to serialize to JSON.

        Raises:
            FileHandlerError: If the file cannot be written.
        """
        def _write_json_operation():
            try:
                resolved_path = self._validate_path(Path(path), is_write=True)
                resolved_path.parent.mkdir(parents=True, exist_ok=True)
                with self._lock:
                    content = json.dumps(data, indent=2)
                    resolved_path.write_text(content)
            except Exception as e:
                raise FileHandlerError(f"Failed to write JSON file '{path}': {str(e)}") from e
        
        self._retry_operation(_write_json_operation)

    def move_file(self, source: str, destination: str) -> None:
        """Move a file from source to destination.

        Args:
            source: Source file path.
            destination: Destination file path.

        Raises:
            FileHandlerError: If the file cannot be moved.
        """
        def _move_file_operation():
            try:
                source_path = self._validate_path(Path(source))
                dest_path = self._validate_path(Path(destination), is_write=True)
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with self._lock:
                    os.replace(source_path, dest_path)
            except Exception as e:
                raise FileHandlerError(f"Failed to move file from '{source}' to '{destination}': {str(e)}") from e
        
        self._retry_operation(_move_file_operation)

    def list_files(self, directory: str) -> list:
        """List files in a directory.

        Args:
            directory: Directory path to list.

        Returns:
            List of file paths.

        Raises:
            FileHandlerError: If the directory cannot be listed.
        """
        def _list_files_operation():
            try:
                resolved_path = self._validate_path(Path(directory))
                with self._lock:
                    return [f for f in resolved_path.iterdir() if f.is_file()]
            except Exception as e:
                raise FileHandlerError(f"Failed to list files in directory '{directory}': {str(e)}") from e
        
        return self._retry_operation(_list_files_operation)

    def create_directory(self, path: str) -> None:
        """Create a directory.

        Args:
            path: Path of the directory to create.

        Raises:
            FileHandlerError: If the directory cannot be created.
        """
        def _create_directory_operation():
            try:
                resolved_path = self._validate_path(Path(path), is_write=True)
                with self._lock:
                    resolved_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise FileHandlerError(f"Failed to create directory '{path}': {str(e)}") from e
        
        self._retry_operation(_create_directory_operation)

    def delete_file(self, path: str) -> None:
        """Delete a file.

        Args:
            path: Path to the file to delete.

        Raises:
            FileHandlerError: If the file cannot be deleted.
        """
        def _delete_file_operation():
            try:
                resolved_path = self._validate_path(Path(path))
                with self._lock:
                    resolved_path.unlink()
            except Exception as e:
                raise FileHandlerError(f"Failed to delete file '{path}': {str(e)}") from e
        
        self._retry_operation(_delete_file_operation)

    def append_text(self, path: str, content: str) -> None:
        """Append text content to a file.

        Args:
            path: Path to the file to append to.
            content: The text content to append.

        Raises:
            FileHandlerError: If the file cannot be appended to.
        """
        def _append_text_operation():
            try:
                resolved_path = self._validate_path(Path(path), is_write=True)
                resolved_path.parent.mkdir(parents=True, exist_ok=True)
                with self._lock:
                    resolved_path.write_text(resolved_path.read_text() + content)
            except Exception as e:
                raise FileHandlerError(f"Failed to append to text file '{path}': {str(e)}") from e
        
        self._retry_operation(_append_text_operation)

    def lock_file(self, path: str) -> "FileLockContextManager":
        """Get a context manager for file locking.

        Args:
            path: Path to the file to lock.

        Returns:
            A context manager for the file lock.
        """
        return FileLockContextManager(self, path)

class FileLockContextManager:
    """Context manager for file locking."""

    def __init__(self, file_handler: FileHandler, path: str):
        self.file_handler = file_handler
        self.path = path
        self.lock = None

    def __enter__(self):
        # This is a placeholder implementation
        # In a production system, this would acquire an actual file lock
        self.lock = self.file_handler._lock
        self.lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock:
            self.lock.release()


if __name__ == "__main__":
    # Example usage
    handler = FileHandler()
    
    try:
        # Test writing a file
        handler.write_text("test.txt", "Hello, World!")
        print("File written successfully")
        
        # Test reading a file
        content = handler.read_text("test.txt")
        print(f"File content: {content}")
        
        # Test JSON operations
        data = {"name": "test", "value": 42}
        handler.write_json("test.json", data)
        read_data = handler.read_json("test.json")
        print(f"JSON data: {read_data}")
        
        # Test directory creation
        handler.create_directory("test_dir")
        print("Directory created successfully")
        
        # Test file moving
        handler.move_file("test.txt", "test_dir/moved_test.txt")
        print("File moved successfully")
        
        # Test file deletion
        handler.delete_file("test_dir/moved_test.txt")
        handler.delete_file("test.json")
        handler.delete_file("test_dir")  # This will fail silently if directory not empty
        print("Test completed successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()