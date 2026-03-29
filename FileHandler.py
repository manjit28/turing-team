import json
import logging
import os
import time
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileHandlerError(Exception):
    """Custom exception for FileHandler errors."""
    pass


class FileHandler:
    """
    A thread-safe file handler for reading, writing, appending, and managing files.

    This class provides methods for file operations with built-in retry logic,
    thread safety, and validation of file paths to prevent directory traversal
    vulnerabilities.
    """

    def __init__(self, base_path: str = "."):
        """
        Initialize the FileHandler with a base path.

        :param base_path: The base directory for all file operations.
        """
        self.base_path = Path(base_path).resolve()
        self._lock = Lock()

    def _validate_path(self, file_path: Union[str, Path]) -> Path:
        """
        Validate and resolve the file path to prevent directory traversal.

        :param file_path: The file path to validate.
        :return: The resolved and validated path.
        :raises FileHandlerError: If the path is outside the base directory.
        """
        # Resolve the path to handle relative paths and symbolic links
        resolved_path = Path(file_path).resolve()

        # Check if the resolved path is within the base directory
        try:
            resolved_path.relative_to(self.base_path)
        except ValueError:
            raise FileHandlerError(
                f"Path '{file_path}' is outside the base directory '{self.base_path}'"
            )

        return resolved_path

    def _retry_operation(self, operation, max_retries: int = 3, delay: float = 1.0):
        """
        Retry a file operation with exponential backoff.

        :param operation: The operation to retry.
        :param max_retries: Maximum number of retries.
        :param delay: Initial delay between retries.
        :return: The result of the operation.
        :raises FileHandlerError: If all retries fail.
        """
        last_exception = None

        for attempt in range(max_retries):
            try:
                return operation()
            except (OSError, IOError) as e:
                last_exception = e
                if attempt < max_retries - 1:  # Don't sleep on the last attempt
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise FileHandlerError(
                        f"Operation failed after {max_retries} attempts: {e}"
                    ) from e

        raise FileHandlerError(
            f"Operation failed after {max_retries} attempts: {last_exception}"
        )

    def read_file(self, file_path: str) -> str:
        """
        Read the contents of a file.

        :param file_path: The path to the file to read.
        :return: The contents of the file.
        :raises FileHandlerError: If the file cannot be read.
        """
        def _read():
            with self._lock:
                resolved_path = self._validate_path(file_path)
                try:
                    with open(resolved_path, "r", encoding="utf-8") as f:
                        return f.read()
                except Exception as e:
                    raise FileHandlerError(f"Failed to read file '{file_path}': {e}")

        return self._retry_operation(_read)

    def read_json(self, file_path: str) -> Dict[str, Any]:
        """
        Read a JSON file and return its contents as a dictionary.

        :param file_path: The path to the JSON file.
        :return: The contents of the JSON file as a dictionary.
        :raises FileHandlerError: If the file cannot be read or is not valid JSON.
        """
        def _read_json():
            with self._lock:
                resolved_path = self._validate_path(file_path)
                try:
                    with open(resolved_path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception as e:
                    raise FileHandlerError(f"Failed to read JSON file '{file_path}': {e}")

        return self._retry_operation(_read_json)

    def write_file(self, file_path: str, content: str) -> None:
        """
        Write content to a file.

        :param file_path: The path to the file to write.
        :param content: The content to write to the file.
        :raises FileHandlerError: If the file cannot be written.
        """
        def _write():
            with self._lock:
                resolved_path = self._validate_path(file_path)
                try:
                    # Ensure the directory exists
                    resolved_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(resolved_path, "w", encoding="utf-8") as f:
                        f.write(content)
                except Exception as e:
                    raise FileHandlerError(f"Failed to write file '{file_path}': {e}")

        self._retry_operation(_write)

    def append_to_file(self, file_path: str, content: str) -> None:
        """
        Append content to a file.

        :param file_path: The path to the file to append to.
        :param content: The content to append to the file.
        :raises FileHandlerError: If the file cannot be appended to.
        """
        def _append():
            with self._lock:
                resolved_path = self._validate_path(file_path)
                try:
                    # Ensure the directory exists
                    resolved_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(resolved_path, "a", encoding="utf-8") as f:
                        f.write(content)
                except Exception as e:
                    raise FileHandlerError(f"Failed to append to file '{file_path}': {e}")

        self._retry_operation(_append)

    def delete_file(self, file_path: str) -> None:
        """
        Delete a file.

        :param file_path: The path to the file to delete.
        :raises FileHandlerError: If the file cannot be deleted.
        """
        def _delete():
            with self._lock:
                resolved_path = self._validate_path(file_path)
                try:
                    os.remove(resolved_path)
                except Exception as e:
                    raise FileHandlerError(f"Failed to delete file '{file_path}': {e}")

        self._retry_operation(_delete)

    def move_file(self, src_path: str, dest_path: str) -> None:
        """
        Move a file from source to destination.

        :param src_path: The source file path.
        :param dest_path: The destination file path.
        :raises FileHandlerError: If the file cannot be moved.
        """
        def _move():
            with self._lock:
                src_resolved = self._validate_path(src_path)
                dest_resolved = self._validate_path(dest_path)
                try:
                    # Ensure the destination directory exists
                    dest_resolved.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(src_resolved, dest_resolved)
                except Exception as e:
                    raise FileHandlerError(
                        f"Failed to move file from '{src_path}' to '{dest_path}': {e}"
                    )

        self._retry_operation(_move)

    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.

        :param file_path: The path to the file to check.
        :return: True if the file exists, False otherwise.
        """
        with self._lock:
            resolved_path = self._validate_path(file_path)
            return resolved_path.is_file()

    def get_file_size(self, file_path: str) -> int:
        """
        Get the size of a file in bytes.

        :param file_path: The path to the file.
        :return: The size of the file in bytes.
        :raises FileHandlerError: If the file cannot be accessed.
        """
        def _get_size():
            with self._lock:
                resolved_path = self._validate_path(file_path)
                try:
                    return resolved_path.stat().st_size
                except Exception as e:
                    raise FileHandlerError(f"Failed to get file size for '{file_path}': {e}")

        return self._retry_operation(_get_size)

    def list_files(self, directory_path: str = ".") -> list:
        """
        List all files in a directory.

        :param directory_path: The directory to list files in.
        :return: A list of file paths.
        :raises FileHandlerError: If the directory cannot be accessed.
        """
        def _list_files():
            with self._lock:
                resolved_path = self._validate_path(directory_path)
                try:
                    return [str(f) for f in resolved_path.iterdir() if f.is_file()]
                except Exception as e:
                    raise FileHandlerError(f"Failed to list files in '{directory_path}': {e}")

        return self._retry_operation(_list_files)