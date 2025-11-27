"""Input validation functions for the message printer API."""


def validate_name(name: str | None) -> str:
    """Validate name meets requirements.
    
    Args:
        name: Raw name from user input
        
    Returns:
        Validated and trimmed name
        
    Raises:
        ValueError: If name is invalid (empty, too long, or None)
    """
    if name is None:
        raise ValueError("Name is required")
    
    trimmed = name.strip()
    
    if not trimmed:
        raise ValueError("Name cannot be empty or whitespace only")
    
    if len(trimmed) > 50:
        raise ValueError(f"Name too long: {len(trimmed)} characters (max 50)")
    
    return trimmed


def validate_message_content(content: str | None) -> str:
    """Validate message content meets requirements.
    
    Args:
        content: Raw message content from user input
        
    Returns:
        Validated and trimmed message content
        
    Raises:
        ValueError: If content is invalid (empty, too long, or None)
    """
    if content is None:
        raise ValueError("Content is required")
    
    trimmed = content.strip()
    
    if not trimmed:
        raise ValueError("Content cannot be empty or whitespace only")
    
    if len(trimmed) > 280:
        raise ValueError(f"Content too long: {len(trimmed)} characters (max 280)")
    
    return trimmed


def validate_message_id(message_id: str | None) -> str:
    """Validate message ID is present.
    
    Args:
        message_id: Message ID from user input
        
    Returns:
        Validated message ID
        
    Raises:
        ValueError: If message_id is invalid (empty or None)
    """
    if message_id is None:
        raise ValueError("Message ID is required")
    
    trimmed = message_id.strip()
    
    if not trimmed:
        raise ValueError("Message ID cannot be empty")
    
    return trimmed

