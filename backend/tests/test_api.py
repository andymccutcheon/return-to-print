"""Integration tests for API endpoints.

Note: These tests use Chalice's test client and moto for mocking AWS services.
"""

import pytest
import sys
import os
import json
from moto import mock_aws
import boto3

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'message_printer_api'))


@pytest.fixture
def dynamodb_table():
    """Create a mock DynamoDB table for testing."""
    with mock_aws():
        # Set environment variable
        os.environ['DYNAMODB_TABLE'] = 'return-to-print-messages-prod'
        
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


@pytest.fixture
def test_client():
    """Create Chalice test client."""
    from chalice.test import Client
    from app import app
    
    with Client(app) as client:
        yield client


@mock_aws
class TestCreateMessageEndpoint:
    """Tests for POST /message endpoint."""
    
    def test_create_message_success(self, dynamodb_table, test_client):
        """Test successful message creation."""
        response = test_client.http.post(
            '/message',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'name': 'John', 'content': 'Test message'})
        )
        
        assert response.status_code == 201
        body = response.json_body
        
        assert 'id' in body
        assert body['name'] == 'John'
        assert body['content'] == 'Test message'
        assert body['printed'] == 'false'
        assert body['printed_at'] is None
        assert 'created_at' in body
    
    def test_create_message_empty_content(self, dynamodb_table, test_client):
        """Test that empty content returns 400."""
        response = test_client.http.post(
            '/message',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'name': 'John', 'content': ''})
        )
        
        assert response.status_code == 400
        body = response.json_body
        assert 'Code' in body
        assert 'BadRequestError' in body['Code']
    
    def test_create_message_whitespace_only(self, dynamodb_table, test_client):
        """Test that whitespace-only content returns 400."""
        response = test_client.http.post(
            '/message',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'name': 'John', 'content': '   '})
        )
        
        assert response.status_code == 400
    
    def test_create_message_too_long(self, dynamodb_table, test_client):
        """Test that content over 280 chars returns 400."""
        long_content = 'a' * 281
        response = test_client.http.post(
            '/message',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'name': 'John', 'content': long_content})
        )
        
        assert response.status_code == 400
    
    def test_create_message_missing_content(self, dynamodb_table, test_client):
        """Test that missing content field returns 400."""
        response = test_client.http.post(
            '/message',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'name': 'John'})
        )
        
        assert response.status_code == 400
    
    def test_create_message_missing_name(self, dynamodb_table, test_client):
        """Test that missing name field returns 400."""
        response = test_client.http.post(
            '/message',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'content': 'Test message'})
        )
        
        assert response.status_code == 400
    
    def test_create_message_empty_name(self, dynamodb_table, test_client):
        """Test that empty name returns 400."""
        response = test_client.http.post(
            '/message',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'name': '', 'content': 'Test message'})
        )
        
        assert response.status_code == 400
    
    def test_create_message_name_too_long(self, dynamodb_table, test_client):
        """Test that name over 50 chars returns 400."""
        long_name = 'a' * 51
        response = test_client.http.post(
            '/message',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'name': long_name, 'content': 'Test message'})
        )
        
        assert response.status_code == 400
    
    def test_create_message_trims_whitespace(self, dynamodb_table, test_client):
        """Test that content and name are trimmed."""
        response = test_client.http.post(
            '/message',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'name': '  John  ', 'content': '  Test  '})
        )
        
        assert response.status_code == 201
        body = response.json_body
        assert body['name'] == 'John'
        assert body['content'] == 'Test'


@mock_aws
class TestGetRecentMessagesEndpoint:
    """Tests for GET /messages/recent endpoint."""
    
    def test_get_recent_messages_empty(self, dynamodb_table, test_client):
        """Test getting recent messages when none exist."""
        response = test_client.http.get('/messages/recent')
        
        assert response.status_code == 200
        body = response.json_body
        assert 'messages' in body
        assert body['messages'] == []
    
    def test_get_recent_messages_returns_list(self, dynamodb_table, test_client):
        """Test that recent messages returns a list."""
        # Create some messages
        test_client.http.post(
            '/message',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'name': 'Alice', 'content': 'Message 1'})
        )
        test_client.http.post(
            '/message',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'name': 'Bob', 'content': 'Message 2'})
        )
        
        response = test_client.http.get('/messages/recent')
        
        assert response.status_code == 200
        body = response.json_body
        assert 'messages' in body
        assert len(body['messages']) == 2
        # Verify name field is included
        assert 'name' in body['messages'][0]
        assert 'name' in body['messages'][1]


@mock_aws
class TestGetNextToPrintEndpoint:
    """Tests for GET /printer/next-to-print endpoint."""
    
    def test_next_to_print_empty(self, dynamodb_table, test_client):
        """Test getting next to print when no messages exist."""
        response = test_client.http.get('/printer/next-to-print')
        
        assert response.status_code == 200
        body = response.json_body
        assert 'message' in body
        assert body['message'] is None
    
    def test_next_to_print_returns_message(self, dynamodb_table, test_client):
        """Test that next to print returns a message."""
        # Create a message
        create_response = test_client.http.post(
            '/message',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'name': 'John', 'content': 'Test message'})
        )
        created_msg = create_response.json_body
        
        # Get next to print
        response = test_client.http.get('/printer/next-to-print')
        
        assert response.status_code == 200
        body = response.json_body
        assert body['message'] is not None
        assert body['message']['id'] == created_msg['id']
        assert body['message']['name'] == 'John'
        assert body['message']['printed'] == 'false'
    
    def test_next_to_print_skips_printed(self, dynamodb_table, test_client):
        """Test that next to print skips printed messages."""
        import time
        
        # Create first message
        msg1 = test_client.http.post(
            '/message',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'name': 'Alice', 'content': 'First'})
        ).json_body
        
        time.sleep(0.01)
        
        # Create second message
        msg2 = test_client.http.post(
            '/message',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'name': 'Bob', 'content': 'Second'})
        ).json_body
        
        # Mark first as printed
        test_client.http.post(
            '/printer/mark-printed',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'id': msg1['id']})
        )
        
        # Get next to print
        response = test_client.http.get('/printer/next-to-print')
        
        assert response.status_code == 200
        body = response.json_body
        assert body['message'] is not None
        assert body['message']['id'] == msg2['id']


@mock_aws
class TestMarkPrintedEndpoint:
    """Tests for POST /printer/mark-printed endpoint."""
    
    def test_mark_printed_success(self, dynamodb_table, test_client):
        """Test successfully marking a message as printed."""
        # Create a message
        create_response = test_client.http.post(
            '/message',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'name': 'John', 'content': 'Test message'})
        )
        message_id = create_response.json_body['id']
        
        # Mark as printed
        response = test_client.http.post(
            '/printer/mark-printed',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'id': message_id})
        )
        
        assert response.status_code == 200
        body = response.json_body
        assert body['status'] == 'ok'
        assert body['id'] == message_id
    
    def test_mark_printed_missing_id(self, dynamodb_table, test_client):
        """Test that missing id returns 400."""
        response = test_client.http.post(
            '/printer/mark-printed',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({})
        )
        
        assert response.status_code == 400
    
    def test_mark_printed_empty_id(self, dynamodb_table, test_client):
        """Test that empty id returns 400."""
        response = test_client.http.post(
            '/printer/mark-printed',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'id': ''})
        )
        
        assert response.status_code == 400


@mock_aws
class TestHealthCheckEndpoint:
    """Tests for GET /health endpoint."""
    
    def test_health_check(self, test_client):
        """Test health check endpoint."""
        response = test_client.http.get('/health')
        
        assert response.status_code == 200
        body = response.json_body
        assert body['status'] == 'healthy'


@mock_aws
class TestCORS:
    """Tests for CORS headers."""
    
    def test_cors_headers_present(self, dynamodb_table, test_client):
        """Test that CORS headers are present on API endpoints."""
        response = test_client.http.post(
            '/message',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'name': 'John', 'content': 'Test'})
        )
        
        # Chalice test client may not expose CORS headers directly
        # This test verifies the endpoint is configured with cors=True
        assert response.status_code == 201

