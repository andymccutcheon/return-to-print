"""Data models and type definitions for the message printer API."""

from typing import TypedDict, Optional


class Message(TypedDict):
    """Message data model.
    
    Attributes:
        id: Unique identifier (UUID v4)
        content: Message text content (1-280 characters)
        created_at: ISO 8601 timestamp when message was created
        printed: String "true" or "false" indicating if message has been printed
        printed_at: ISO 8601 timestamp when message was printed, or None
    """
    id: str
    content: str
    created_at: str
    printed: str  # "true" or "false" as string for DynamoDB GSI
    printed_at: Optional[str]

