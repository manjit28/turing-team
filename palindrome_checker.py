def is_palindrome(s):
    """
    Check if a string is a palindrome, ignoring case and non-alphanumeric characters.
    
    Args:
        s (str): The string to check
        
    Returns:
        bool: True if the string is a palindrome, False otherwise
    """
    # Convert to lowercase and keep only alphanumeric characters
    cleaned = ''.join(char.lower() for char in s if char.isalnum())
    
    # Compare the string with its reverse
    return cleaned == cleaned[::-1]