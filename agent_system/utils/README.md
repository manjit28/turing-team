# File Handler Utility

A robust file handling utility for the agent system with proper error handling and logging.

## Features

- Text file read/write operations
- JSON file read/write operations with automatic serialization/deserialization
- Comprehensive error handling with custom exceptions
- Logging integration with the agent system
- Path resolution relative to a configurable base directory
- Cross-platform compatibility

## Usage

```python
from agent_system.utils.file_handler import FileHandler, FileHandlerError

# Create a file handler with default base directory
fh = FileHandler()

# Or specify a custom base directory
fh = FileHandler("/path/to/base/directory")

# Read text file
content = fh.read_text("config.txt")

# Write text file
fh.write_text("output.txt", "Hello, world!")

# Read JSON file
data = fh.read_json("config.json")

# Write JSON file
fh.write_json("output.json", {"key": "value"})
```

## Error Handling

All operations raise `FileHandlerError` on failure with user-friendly messages. 
Detailed error information including stack traces are logged using the `agent_system` logger.

## Methods

### `read_text(path: str) -> str`
Read text content from a file.

### `write_text(path: str, content: str) -> None`
Write text content to a file.

### `read_json(path: str) -> Any`
Read and parse JSON content from a file.

### `write_json(path: str, data: Any) -> None`
Serialize data to JSON and write to a file.