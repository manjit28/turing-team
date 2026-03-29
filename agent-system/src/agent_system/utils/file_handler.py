#!/usr/bin/env python3
"""
File I/O helper module for the agent system.
Provides thread-safe file reading and writing with robust error handling and logging.
"""

import logging
import threading
from pathlib import Path
from typing import Optional

# Logger for this module
logger = logging.getLogger("agent_system")

class FileHandlerError(Exception):
    """Custom exception for file handling errors."""
    pass

class FileHandler:
    """Thread-safe file I/O helper class."""
    
    def __init__(self):
        self._lock = threading.Lock()
    
    def read_file(self, path: str, encoding: str = "utf-8") -> str:
        """
        Read content from a file.
        
        Args:
            path: Path to the file to read
            encoding: Text encoding to use (default: utf-8)
            
        Returns:
            Content of the file as string
            
        Raises:
            FileHandlerError: If file cannot be read
        """
        try:
            with open(path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read file '{path}': {str(e)}", exc_info=True)
            raise FileHandlerError(f"Failed to read file '{path}': {str(e)}") from e
    
    def write_file(self, path: str, content: str, encoding: str = "utf-8", mode: str = "w") -> None:
        """
        Write content to a file.
        
        Args:
            path: Path to the file to write
            content: Content to write to the file
            encoding: Text encoding to use (default: utf-8)
            mode: File open mode (default: 'w' for write, 'a' for append)
            
        Raises:
            FileHandlerError: If file cannot be written
        """
        try:
            # Create directory if it doesn't exist
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            
            with self._lock:
                with open(path, mode, encoding=encoding) as f:
                    f.write(content)
        except Exception as e:
            logger.error(f"Failed to write file '{path}': {str(e)}", exc_info=True)
            raise FileHandlerError(f"Failed to write file '{path}': {str(e)}") from e

def main():
    """CLI for manual testing of the FileHandler."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CLI for FileHandler testing")
    parser.add_argument("--read", help="Read file path")
    parser.add_argument("--write", help="Write file path")
    parser.add_argument("--content", help="Content to write")
    parser.add_argument("--append", action="store_true", help="Append mode instead of write")
    
    args = parser.parse_args()
    
    handler = FileHandler()
    
    if args.read:
        try:
            content = handler.read_file(args.read)
            print(content)
        except FileHandlerError as e:
            print(f"Error: {e}")
            return 1
    
    if args.write and args.content:
        try:
            mode = "a" if args.append else "w"
            handler.write_file(args.write, args.content, mode=mode)
            print(f"Successfully wrote to {args.write}")
        except FileHandlerError as e:
            print(f"Error: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    exit(main())