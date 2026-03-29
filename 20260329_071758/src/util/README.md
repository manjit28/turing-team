# File Handling Utility

This utility provides basic file read/write operations with proper error handling and logging.

## Functions

- `read_file(path: str) -> str`: Reads content from a file
- `write_file(path: str, content: str) -> None`: Writes content to a file

## Usage

```python
from util.file_util import read_file, write_file, FileHandlingError

try:
    content = read_file('/path/to/file.txt')
    write_file('/path/to/output.txt', content)
except FileHandlingError as e:
    print(f"File operation failed: {e}")
```

## Error Handling

The utility raises `FileHandlingError` on any I/O error, which wraps the original exception for debugging.