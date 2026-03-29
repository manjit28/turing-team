import os
import json
import logging
import threading
import time
from pathlib import Path
from typing import Optional, Any, Union
from contextlib import contextmanager

# Configure logging
logger = logging.getLogger("agent_system")

class FileHandlerError(Exception):
    """Base exception for FileHandler errors."""
    pass

class PathValidationError(FileHandlerError):
    """Raised when a path is invalid or outside allowed boundaries."""
    pass

class FileHandler:
    """Thread-safe file I/O helper with robust error handling and logging."""
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize FileHandler with optional base path.
        
        Args:
            base_path: Base directory for all file operations. Defaults to current working directory.
        """
        self._base_path = Path(base_path) if base_path else Path.cwd()
        self._lock = threading.Lock()
        self._max_retries = 3
        self._retry_backoff = 1.0  # seconds
        
    def _validate_path(self, path: str) -> Path:
        """
        Validate and resolve file path relative to base path.
        
        Args:
            path: Path to validate
            
        Returns:
            Resolved Path object
            
        Raises:
            PathValidationError: If path is invalid or outside base path
        """
        try:
            # Resolve path relative to base
            resolved_path = (self._base_path / path).resolve()
            
            # Check if path is within base directory
            if not resolved_path.is_relative_to(self._base_path):
                raise PathValidationError(
                    f"Path '{path}' is outside the configured base path '{self._base_path}'"
                )
                
            return resolved_path
        except Exception as e:
            raise PathValidationError(f"Invalid path '{path}': {str(e)}")
    
    def _retry_operation(self, operation, *args, **kwargs):
        """
        Execute operation with exponential backoff retry logic.
        
        Args:
            operation: Function to execute
            *args: Arguments for operation
            **kwargs: Keyword arguments for operation
            
        Returns:
            Result of operation
            
        Raises:
            Exception: If all retry attempts fail
        """
        last_exception = None
        
        for attempt in range(self._max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self._max_retries - 1:  # Don't sleep on the last attempt
                    sleep_time = self._retry_backoff * (2 ** attempt)
                    logger.warning(
                        f"File operation failed (attempt {attempt + 1}/{self._max_retries}): "
                        f"{str(e)}. Retrying in {sleep_time:.2f}s..."
                    )
                    time.sleep(sleep_time)
                else:
                    logger.error(
                        f"File operation failed after {self._max_retries} attempts: {str(e)}"
                    )
                    
        raise last_exception
    
    def read_file(self, path: str, encoding: str = "utf-8") -> str:
        """
        Read file content as string.
        
        Args:
            path: Path to file
            encoding: File encoding (default: utf-8)
            
        Returns:
            File content as string
            
        Raises:
            FileHandlerError: If file cannot be read
        """
        def _read_file_operation():
            try:
                resolved_path = self._validate_path(path)
                with open(resolved_path, 'r', encoding=encoding) as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Failed to read file '{path}': {str(e)}", exc_info=True)
                raise FileHandlerError(f"Failed to read file '{path}': {str(e)}")
        
        return self._retry_operation(_read_file_operation)
    
    def write_file(self, path: str, content: str, encoding: str = "utf-8", mode: str = "w") -> None:
        """
        Write content to file.
        
        Args:
            path: Path to file
            content: Content to write
            encoding: File encoding (default: utf-8)
            mode: File mode (default: 'w')
            
        Raises:
            FileHandlerError: If file cannot be written
        """
        def _write_file_operation():
            try:
                resolved_path = self._validate_path(path)
                
                # Create directory if it doesn't exist
                resolved_path.parent.mkdir(parents=True, exist_ok=True)
                
                with self._lock:  # Thread safety
                    with open(resolved_path, mode, encoding=encoding) as f:
                        f.write(content)
                        
            except Exception as e:
                logger.error(f"Failed to write file '{path}': {str(e)}", exc_info=True)
                raise FileHandlerError(f"Failed to write file '{path}': {str(e)}")
        
        self._retry_operation(_write_file_operation)
    
    def read_json(self, path: str) -> Any:
        """
        Read and parse JSON from file.
        
        Args:
            path: Path to JSON file
            
        Returns:
            Parsed JSON data
            
        Raises:
            FileHandlerError: If file cannot be read or parsed
        """
        content = self.read_file(path)
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from '{path}': {str(e)}")
            raise FileHandlerError(f"Invalid JSON in file '{path}': {str(e)}")
    
    def write_json(self, path: str, data: Any) -> None:
        """
        Write data as JSON to file.
        
        Args:
            path: Path to output file
            data: Data to serialize as JSON
            
        Raises:
            FileHandlerError: If file cannot be written
        """
        json_content = json.dumps(data, indent=2)
        self.write_file(path, json_content)

def main():
    """CLI interface for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="FileHandler CLI")
    parser.add_argument("--read", help="Read file")
    parser.add_argument("--write", help="Write file")
    parser.add_argument("--content", help="Content to write")
    parser.add_argument("--base-path", help="Base path for operations")
    
    args = parser.parse_args()
    
    handler = FileHandler(args.base_path)
    
    if args.read:
        try:
            content = handler.read_file(args.read)
            print(content)
        except Exception as e:
            print(f"Error reading {args.read}: {e}")
    
    elif args.write and args.content:
        try:
            handler.write_file(args.write, args.content)
            print(f"Wrote to {args.write}")
        except Exception as e:
            print(f"Error writing to {args.write}: {e}")

if __name__ == "__main__":
    main()