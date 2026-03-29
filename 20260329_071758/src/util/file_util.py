import os
import logging
from typing import Optional
from pathlib import Path

# Configure logger
logger = logging.getLogger('file_util')

class FileHandlingError(Exception):
    """Custom exception for file handling operations."""
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.original_exception = original_exception

def read_file(path: str) -> str:
    """
    Read content from a file.
    
    Args:
        path (str): Path to the file to read
        
    Returns:
        str: Content of the file
        
    Raises:
        FileHandlingError: If the file cannot be read
    """
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Failed to read file {path}: {e}")
        raise FileHandlingError(f"Failed to read file {path}", e)

def write_file(path: str, content: str) -> None:
    """
    Write content to a file.
    
    Args:
        path (str): Path to the file to write
        content (str): Content to write to the file
        
    Raises:
        FileHandlingError: If the file cannot be written
    """
    try:
        # Ensure directory exists
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        logger.error(f"Failed to write file {path}: {e}")
        raise FileHandlingError(f"Failed to write file {path}", e)