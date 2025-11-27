"""DynamoDB operations for the message printer API."""

import os
import uuid
from datetime import datetime
from typing import Optional
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from .models import Message


# Initialize DynamoDB resource (reused across Lambda invocations)
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

# Table name from environment variable or default
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'return-to-print-messages-prod')
table = dynamodb.Table(TABLE_NAME)

# Global Secondary Index name
GSI_NAME = 'PrintedStatusIndex'


def create_message(content: str) -> Message:
    """Create a new message in the database.
    
    Args:
        content: Validated message content (1-280 characters)
        
    Returns:
        Created message with all fields
        
    Raises:
        Exception: If DynamoDB operation fails
    """
    message_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + 'Z'
    
    message: Message = {
        'id': message_id,
        'content': content,
        'created_at': now,
        'printed': 'false',  # String for GSI compatibility
        'printed_at': None
    }
    
    try:
        table.put_item(Item=message)
        return message
    except ClientError as e:
        raise Exception(f"Failed to create message: {e.response['Error']['Message']}")


def get_recent_messages(limit: int = 10) -> list[Message]:
    """Get recent messages, sorted by creation time descending.
    
    Args:
        limit: Maximum number of messages to return (default 10)
        
    Returns:
        List of messages, newest first
        
    Raises:
        Exception: If DynamoDB operation fails
    """
    try:
        # For small datasets, scan is acceptable
        # In production with >1000 messages, consider time-based partitioning
        response = table.scan()
        items = response.get('Items', [])
        
        # Sort by created_at descending (newest first)
        items.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Return limited results
        return items[:limit]  # type: ignore
    except ClientError as e:
        raise Exception(f"Failed to get recent messages: {e.response['Error']['Message']}")


def get_next_unprinted() -> Optional[Message]:
    """Get the oldest unprinted message using the GSI.
    
    Returns:
        Oldest unprinted message, or None if no unprinted messages exist
        
    Raises:
        Exception: If DynamoDB operation fails
    """
    try:
        # Query using Global Secondary Index for efficient lookup
        response = table.query(
            IndexName=GSI_NAME,
            KeyConditionExpression=Key('printed').eq('false'),
            ScanIndexForward=True,  # Ascending order (oldest first)
            Limit=1
        )
        
        items = response.get('Items', [])
        if not items:
            return None
        
        return items[0]  # type: ignore
    except ClientError as e:
        raise Exception(f"Failed to get next unprinted message: {e.response['Error']['Message']}")


def mark_message_printed(message_id: str) -> None:
    """Mark a message as printed with timestamp.
    
    Args:
        message_id: ID of the message to mark as printed
        
    Raises:
        Exception: If DynamoDB operation fails
    """
    now = datetime.utcnow().isoformat() + 'Z'
    
    try:
        table.update_item(
            Key={'id': message_id},
            UpdateExpression='SET printed = :p, printed_at = :t',
            ExpressionAttributeValues={
                ':p': 'true',  # String for GSI compatibility
                ':t': now
            }
        )
    except ClientError as e:
        raise Exception(f"Failed to mark message as printed: {e.response['Error']['Message']}")

