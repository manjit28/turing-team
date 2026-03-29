'''
File handler utility for the agent system.
Provides robust file operations with error handling and logging.
'''
import json
import logging
from pathlib import Path
from typing import Any, Union

# Configure logger
logger = logging.getLogger("agent_system")


class FileHandlerError(Exception):
    """Custom exception for file handling errors."""
    pass


class FileHandler:
    """A utility class for handling file operations with robust error handling."""
    
    def __init__(self, base_dir: Union[str, Path] = "."):
        """
        Initialize the FileHandler with a base directory.
        
        Args:
            base_dir: Base directory for all file operations. Defaults to current directory.
        """
        self.base_dir = Path(base_dir).resolve()
        
    def _resolve_path(self, path: Union[str, Path]) -> Path:
        """
        Resolve a path relative to the base directory.
        
        Args:
            path: The file path to resolve.
            
        Returns:
            Resolved absolute path.
        """
        return (self.base_dir / path).resolve()
        
    def read_text(self, path: Union[str, Path]) -> str:
        """
        Read text content from a file.
        
        Args:
            path: Path to the file to read.
            
        Returns:
            File content as string.
            
        Raises:
            FileHandlerError: If file cannot be read.
        """
        try:
            resolved_path = self._resolve_path(path)
            logger.debug(f"Reading text file: {resolved_path}")
            return resolved_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to read text file '{path}': {str(e)}", exc_info=True)
            raise FileHandlerError(f"Could not read file '{path}': {str(e)}") from e
            
    def write_text(self, path: Union[str, Path], content: str) -> None:
        """
        Write text content to a file.
        
        Args:
            path: Path to the file to write.
            content: Content to write to the file.
            
        Raises:
            FileHandlerError: If file cannot be written.
        """
        try:
            resolved_path = self._resolve_path(path)
            # Ensure directory exists
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Writing text file: {resolved_path}")
            resolved_path.write_text(content, encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to write text file '{path}': {str(e)}", exc_info=True)
            raise FileHandlerError(f"Could not write file '{path}': {str(e)}") from e
            
    def read_json(self, path: Union[str, Path]) -> Any:
        """
        Read JSON content from a file.
        
        Args:
            path: Path to the JSON file to read.
            
        Returns:
            Parsed JSON data.
            
        Raises:
            FileHandlerError: If file cannot be read or parsed.
        """
        try:
            resolved_path = self._resolve_path(path)
            logger.debug(f"Reading JSON file: {resolved_path}")
            content = resolved_path.read_text(encoding='utf-8')
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from file '{path}': {str(e)}", exc_info=True)
            raise FileHandlerError(f"Invalid JSON in file '{path}': {str(e)}") from e
        except Exception as e:
            logger.error(f"Failed to read JSON file '{path}': {str(e)}", exc_info=True)
            raise FileHandlerError(f"Could not read JSON file '{path}': {str(e)}") from e
            
    def write_json(self, path: Union[str, Path], data: Any) -> None:
        """
        Write data to a JSON file.
        
        Args:
            path: Path to the JSON file to write.
            data: Data to serialize to JSON.
            
        Raises:
            FileHandlerError: If file cannot be written.
        """
        try:
            resolved_path = self._resolve_path(path)
            # Ensure directory exists
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Writing JSON file: {resolved_path}")
            resolved_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to write JSON file '{path}': {str(e)}", exc_info=True)
            raise FileHandlerError(f"Could not write JSON file '{path}': {str(e)}") from e
