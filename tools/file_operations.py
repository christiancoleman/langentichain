import os
from datetime import datetime
from pathlib import Path

def read_file(file_path: str) -> str:
    """
    Read the contents of a file
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        String containing the file contents or error message
    """
    try:
        # Expand user path and make absolute
        file_path = os.path.expanduser(file_path)
        file_path = os.path.abspath(file_path)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return f"Contents of {file_path}:\n\n{content}"
        
    except PermissionError:
        return f"Error: Permission denied to read {file_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(input_string: str) -> str:
    """
    Write content to a file
    
    Args:
        input_string: String in format "filename|content" where:
            - filename is the path to write to
            - content is what to write
            
    Returns:
        Success message or error
    """
    try:
        # Parse input
        if '|' not in input_string:
            return "Error: Please use format 'filename|content' (separated by |)"
        
        parts = input_string.split('|', 1)
        if len(parts) != 2:
            return "Error: Please use format 'filename|content' (separated by |)"
            
        file_path = parts[0].strip()
        content = parts[1]
        
        # Expand user path and make absolute
        file_path = os.path.expanduser(file_path)
        file_path = os.path.abspath(file_path)
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Write the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return f"Successfully wrote {len(content)} characters to {file_path}"
        
    except PermissionError:
        return f"Error: Permission denied to write to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def list_files(directory: str = ".") -> str:
    """
    List files in a directory
    
    Args:
        directory: Path to directory (defaults to current directory)
        
    Returns:
        String listing the files and directories
    """
    try:
        # Expand user path and make absolute
        directory = os.path.expanduser(directory)
        directory = os.path.abspath(directory)
        
        if not os.path.exists(directory):
            return f"Error: Directory not found at {directory}"
            
        if not os.path.isdir(directory):
            return f"Error: {directory} is not a directory"
        
        items = []
        for item in sorted(os.listdir(directory)):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                items.append(f"[DIR]  {item}")
            else:
                size = os.path.getsize(item_path)
                items.append(f"[FILE] {item} ({size} bytes)")
        
        if items:
            return f"Contents of {directory}:\n" + "\n".join(items)
        else:
            return f"Directory {directory} is empty"
            
    except PermissionError:
        return f"Error: Permission denied to access {directory}"
    except Exception as e:
        return f"Error listing directory: {str(e)}"
