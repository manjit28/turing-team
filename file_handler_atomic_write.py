def atomic_write(self, file_path: str, content: str, encoding: str = 'utf-8') -> bool:
    """
    Atomically write content to a file.
    
    Args:
        file_path: Path to the target file
        content: Content to write
        encoding: File encoding (default: utf-8)
        
    Returns:
        bool: True if successful, False otherwise
    """
    import os
    import tempfile
    import shutil
    import logging
    
    logger = logging.getLogger("agent_system")
    
    try:
        # Validate inputs
        if not file_path:
            raise ValueError("file_path cannot be empty")
        
        if content is None:
            content = ""
            
        # Create target directory if it doesn't exist
        target_dir = os.path.dirname(file_path)
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            
        # Create temporary file in the same directory
        temp_dir = os.path.dirname(file_path) or '.'
        temp_file = None
        
        try:
            # Create temporary file
            temp_fd, temp_path = tempfile.mkstemp(dir=temp_dir, suffix='.tmp')
            temp_file = os.fdopen(temp_fd, 'w', encoding=encoding)
            
            # Write content to temporary file
            temp_file.write(content)
            temp_file.flush()
            os.fsync(temp_fd)  # Ensure data is written to disk
            temp_file.close()
            temp_file = None  # Mark as closed
            
            # Atomically move temporary file to target location
            os.replace(temp_path, file_path)
            
            logger.debug(f"Successfully wrote to {file_path}")
            return True
            
        except Exception as e:
            # Clean up temporary file if it exists
            if temp_file:
                temp_file.close()
            if 'temp_path' in locals():
                try:
                    os.unlink(temp_path)
                except:
                    pass
            logger.error(f"Failed to write to {file_path}: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"Error in atomic_write for {file_path}: {str(e)}")
        return False