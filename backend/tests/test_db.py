"""Unit tests for database operations.

Note: These tests use moto to mock DynamoDB. Install with: pip install moto[dynamodb]
"""

import pytest
import sys
import os
from datetime import datetime
from moto import mock_aws
import boto3

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'message_printer_api'))


@pytest.fixture
def dynamodb_table():
    """Create a mock DynamoDB table for testing."""
    with mock_aws():
        # Create DynamoDB resource
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        
        # Create table
        table = dynamodb.create_table(
            TableName='return-to-print-messages-prod',
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'printed', 'AttributeType': 'S'},
                {'AttributeName': 'created_at', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'PrintedStatusIndex',
                    'KeySchema': [
                        {'AttributeName': 'printed', 'KeyType': 'HASH'},
                        {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            BillingMode='PROVISIONED',
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        yield table


@mock_aws
class TestDatabaseOperations:
    """Tests for DynamoDB operations."""
    
    def test_create_message(self, dynamodb_table):
        """Test creating a message in the database."""
        from chalicelib import db
        
        # Create message
        message = db.create_message("Test message content")
        
        # Verify message structure
        assert 'id' in message
        assert message['content'] == "Test message content"
        assert message['printed'] == 'false'
        assert message['printed_at'] is None
        assert 'created_at' in message
        
        # Verify created_at is ISO format
        datetime.fromisoformat(message['created_at'].replace('Z', '+00:00'))
    
    def test_get_recent_messages_empty(self, dynamodb_table):
        """Test getting recent messages when table is empty."""
        from chalicelib import db
        
        messages = db.get_recent_messages()
        assert messages == []
    
    def test_get_recent_messages_sorted(self, dynamodb_table):
        """Test that recent messages are sorted by created_at descending."""
        from chalicelib import db
        import time
        
        # Create multiple messages with slight delays
        msg1 = db.create_message("First message")
        time.sleep(0.01)
        msg2 = db.create_message("Second message")
        time.sleep(0.01)
        msg3 = db.create_message("Third message")
        
        # Get recent messages
        messages = db.get_recent_messages()
        
        # Verify order (newest first)
        assert len(messages) == 3
        assert messages[0]['id'] == msg3['id']
        assert messages[1]['id'] == msg2['id']
        assert messages[2]['id'] == msg1['id']
    
    def test_get_recent_messages_limit(self, dynamodb_table):
        """Test that get_recent_messages respects the limit."""
        from chalicelib import db
        
        # Create 15 messages
        for i in range(15):
            db.create_message(f"Message {i}")
        
        # Get only 10
        messages = db.get_recent_messages(limit=10)
        assert len(messages) == 10
    
    def test_get_next_unprinted_none(self, dynamodb_table):
        """Test getting next unprinted when no messages exist."""
        from chalicelib import db
        
        message = db.get_next_unprinted()
        assert message is None
    
    def test_get_next_unprinted_returns_oldest(self, dynamodb_table):
        """Test that get_next_unprinted returns the oldest unprinted message."""
        from chalicelib import db
        import time
        
        # Create multiple messages
        msg1 = db.create_message("First message")
        time.sleep(0.01)
        msg2 = db.create_message("Second message")
        time.sleep(0.01)
        msg3 = db.create_message("Third message")
        
        # Get next unprinted
        next_msg = db.get_next_unprinted()
        
        # Should be the oldest (first)
        assert next_msg is not None
        assert next_msg['id'] == msg1['id']
    
    def test_get_next_unprinted_skips_printed(self, dynamodb_table):
        """Test that get_next_unprinted skips already printed messages."""
        from chalicelib import db
        import time
        
        # Create messages
        msg1 = db.create_message("First message")
        time.sleep(0.01)
        msg2 = db.create_message("Second message")
        
        # Mark first as printed
        db.mark_message_printed(msg1['id'])
        
        # Get next unprinted
        next_msg = db.get_next_unprinted()
        
        # Should be the second message
        assert next_msg is not None
        assert next_msg['id'] == msg2['id']
    
    def test_mark_message_printed(self, dynamodb_table):
        """Test marking a message as printed."""
        from chalicelib import db
        
        # Create message
        message = db.create_message("Test message")
        
        # Mark as printed
        db.mark_message_printed(message['id'])
        
        # Verify by getting item directly
        table = dynamodb_table
        response = table.get_item(Key={'id': message['id']})
        item = response['Item']
        
        assert item['printed'] == 'true'
        assert item['printed_at'] is not None
        
        # Verify printed_at is ISO format
        datetime.fromisoformat(item['printed_at'].replace('Z', '+00:00'))
    
    def test_mark_message_printed_idempotent(self, dynamodb_table):
        """Test that marking a message printed is idempotent."""
        from chalicelib import db
        
        # Create message
        message = db.create_message("Test message")
        
        # Mark as printed twice
        db.mark_message_printed(message['id'])
        db.mark_message_printed(message['id'])
        
        # Should not raise error
        table = dynamodb_table
        response = table.get_item(Key={'id': message['id']})
        item = response['Item']
        assert item['printed'] == 'true'

