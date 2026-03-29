# File Handler Utility

A thread-safe file I/O helper module for the agent system with robust error handling and logging.

## Features

- Thread-safe file reading and writing operations
- Comprehensive error handling with custom exceptions
- Logging integration using the `agent_system` logger
- Support for different encodings and file modes
- Automatic directory creation when writing files

## API

### `FileHandler` Class

#### Methods

- `read_file(path: str, encoding: str = "utf-8") -> str`
  - Reads content from a file
  - Raises `FileHandlerError` on failure

- `write_file(path: str, content: str, encoding: str = "utf-8", mode: str = "w") -> None`
  - Writes content to a file
  - Creates directories if needed
  - Raises `FileHandlerError` on failure

### Exceptions

- `FileHandlerError`: Custom exception raised for file I/O errors with descriptive messages

## Usage

```python
from agent_system.utils.file_handler import FileHandler

handler = FileHandler()

# Read a file
try:
    content = handler.read_file('/path/to/file.txt')
    print(content)
except FileHandlerError as e:
    print(f"Error reading file: {e}")

# Write a file
try:
    handler.write_file('/path/to/file.txt', 'Hello, World!')
except FileHandlerError as e:
    print(f"Error writing file: {e}")
```

## CLI Usage

The module includes a simple CLI for manual testing:

```bash
# Read a file
python -m agent_system.utils.file_handler --read /path/to/file.txt

# Write a file
python -m agent_system.utils.file_handler --write /path/to/file.txt --content "Hello, World!"

# Append to a file
python -m agent_system.utils.file_handler --write /path/to/file.txt --content "Additional content" --append
```