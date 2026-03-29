def atomic_write(self, file_path: str, content: str) -> bool:
        """
        Write content to file atomically by using a temporary file.
        
        This method writes content to a temporary file first, then
        renames it to the target file. This prevents corruption when
        files are being read while being written to.
        
        Args:
            file_path (str): Path to the target file
            content (str): Content to write
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate inputs
            if not file_path:
                raise ValueError("file_path cannot be empty")
            
            if content is None:
                raise ValueError("content cannot be None")
                
            # Create the directory if it doesn't exist
            import os
            from pathlib import Path
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Create temporary file in the same directory as target
            temp_dir = os.path.dirname(os.path.abspath(file_path)) or '.'
            
            # Use tempfile to create a temporary file
            import tempfile
            import shutil
            
            # Create temporary file in the same directory
            temp_fd, temp_file_path = tempfile.mkstemp(
                suffix='.tmp',
                dir=temp_dir,
                prefix=os.path.basename(file_path) + '.'
            )
            
            try:
                # Write content to temporary file
                with os.fdopen(temp_fd, 'w') as f:
                    f.write(content)
                
                # Atomic rename: move temporary file to target location
                shutil.move(temp_file_path, file_path)
                
                return True
                
            except Exception:
                # Clean up temporary file if it exists
                try:
                    os.unlink(temp_file_path)
                except:
                    pass  # Ignore cleanup errors
                raise
                
        except Exception:
            # Return False on any failure
            return False