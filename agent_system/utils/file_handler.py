"""
File handling utility for the agent system.

This module provides a FileHandler class for reading and writing text and JSON files
with robust error handling and logging.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("agent_system")

class FileHandlerError(Exception):
    """Custom exception for file handling errors."""
    pass

class FileHandler:
    """A utility class for file operations with error handling and logging."""
    
    def __init__(self, base_dir: Union[str, Path] = None):
        """
        Initialize the FileHandler with an optional base directory.
        
        Args:
            base_dir: Base directory for file operations. Defaults to project root.
        """
        if base_dir is None:
            self.base_dir = Path.cwd()
        else:
            self.base_dir = Path(base_dir)
    
    def _resolve_path(self, path: Union[str, Path]) -> Path:
        """
        Resolve a path relative to the base directory.
        
        Args:
            path: Path to resolve
            
        Returns:
            Resolved Path object
        """
        path_obj = Path(path)
        if not path_obj.is_absolute():
            path_obj = self.base_dir / path_obj
        return path_obj
    
    def read_text(self, path: Union[str, Path]) -> str:
        """
        Read text from a file.
        
        Args:
            path: Path to the file
            
        Returns:
            Content of the file as string
            
        Raises:
            FileHandlerError: If file cannot be read
        """
        try:
            resolved_path = self._resolve_path(path)
            logger.debug(f"Reading text from {resolved_path}")
            return resolved_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to read text file {path}: {type(e).__name__}: {e}", exc_info=True)
            raise FileHandlerError(f"Failed to read file '{path}': {str(e)}") from e
    
    def write_text(self, path: Union[str, Path], content: str) -> None:
        """
        Write text to a file.
        
        Args:
            path: Path to the file
            content: Content to write
            
        Raises:
            FileHandlerError: If file cannot be written
        """
        try:
            resolved_path = self._resolve_path(path)
            # Create directories if they don't exist
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Writing text to {resolved_path}")
            resolved_path.write_text(content, encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to write text file {path}: {type(e).__name__}: {e}", exc_info=True)
            raise FileHandlerError(f"Failed to write file '{path}': {str(e)}") from e
    
    def read_json(self, path: Union[str, Path]) -> Any:
        """
        Read JSON data from a file.
        
        Args:
            path: Path to the JSON file
            
        Returns:
            Parsed JSON data
            
        Raises:
            FileHandlerError: If file cannot be read or JSON is invalid
        """
        try:
            resolved_path = self._resolve_path(path)
            logger.debug(f"Reading JSON from {resolved_path}")
            content = resolved_path.read_text(encoding='utf-8')
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {path}: {e}", exc_info=True)
            raise FileHandlerError(f"Invalid JSON in file '{path}': {str(e)}") from e
        except Exception as e:
            logger.error(f"Failed to read JSON file {path}: {type(e).__name__}: {e}", exc_info=True)
            raise FileHandlerError(f"Failed to read JSON file '{path}': {str(e)}") from e
    
    def write_json(self, path: Union[str, Path], data: Any) -> None:
        """
        Write JSON data to a file.
        
        Args:
            path: Path to the JSON file
            data: Data to serialize to JSON
            
        Raises:
            FileHandlerError: If file cannot be written
        """
        try:
            resolved_path = self._resolve_path(path)
            # Create directories if they don't exist
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Writing JSON to {resolved_path}")
            resolved_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to write JSON file {path}: {type(e).__name__}: {e}", exc_info=True)
            raise FileHandlerError(f"Failed to write JSON file '{path}': {str(e)}") from e