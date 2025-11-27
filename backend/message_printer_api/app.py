"""Main Chalice application for the message printer API.

This API provides endpoints for creating messages, fetching recent messages,
and managing the print queue for the Raspberry Pi worker.
"""

from chalice import Chalice, Response, BadRequestError
import logging

from chalicelib import db, validators


app = Chalice(app_name='message-printer-api')
app.log.setLevel(logging.INFO)


@app.route('/message', methods=['POST'], cors=True)
def create_message():
    """Create a new message to be printed.
    
    Request Body:
        {
            "name": "string (1-50 characters)",
            "content": "string (1-280 characters)"
        }
        
    Returns:
        201: Full message object with id, name, content, created_at, printed, printed_at
        400: Validation error (empty, too long, or missing fields)
        500: Server error
    """
    try:
        # Parse and validate request body
        body = app.current_request.json_body or {}
        app.log.info(f"Creating message from: {body.get('name', 'unknown')}")
        
        # Validate name and content
        name = validators.validate_name(body.get('name'))
        content = validators.validate_message_content(body.get('content'))
        
        # Create message in database
        message = db.create_message(name, content)
        
        app.log.info(f"Successfully created message with id: {message['id']}")
        
        return Response(
            body=message,
            status_code=201,
            headers={'Content-Type': 'application/json'}
        )
    except ValueError as e:
        # Validation error - return 400
        app.log.warning(f"Validation error: {e}")
        raise BadRequestError(str(e))
    except Exception as e:
        # Unexpected error - return 500
        app.log.error(f"Error creating message: {e}", exc_info=True)
        return Response(
            body={'error': 'Internal server error'},
            status_code=500,
            headers={'Content-Type': 'application/json'}
        )


@app.route('/messages/recent', methods=['GET'], cors=True)
def get_recent_messages():
    """Get recent messages (last 10).
    
    Returns:
        200: {"messages": [...]} - List of messages, newest first
        500: Server error
    """
    try:
        app.log.info("Fetching recent messages")
        
        # Get recent messages from database
        messages = db.get_recent_messages(limit=10)
        
        app.log.info(f"Successfully retrieved {len(messages)} recent messages")
        
        return Response(
            body={'messages': messages},
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )
    except Exception as e:
        # Unexpected error - return 500
        app.log.error(f"Error fetching recent messages: {e}", exc_info=True)
        return Response(
            body={'error': 'Internal server error'},
            status_code=500,
            headers={'Content-Type': 'application/json'}
        )


@app.route('/printer/next-to-print', methods=['GET'], cors=True)
def get_next_to_print():
    """Get the oldest unprinted message.
    
    Used by the Raspberry Pi worker to poll for messages to print.
    
    Returns:
        200: {"message": {...}} - Oldest unprinted message
        200: {"message": null} - No unprinted messages available
        500: Server error
    """
    try:
        app.log.info("Fetching next message to print")
        
        # Get oldest unprinted message using GSI
        message = db.get_next_unprinted()
        
        if message:
            app.log.info(f"Found message to print: {message['id']}")
        else:
            app.log.info("No unprinted messages available")
        
        return Response(
            body={'message': message},
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )
    except Exception as e:
        # Unexpected error - return 500
        app.log.error(f"Error fetching next message to print: {e}", exc_info=True)
        return Response(
            body={'error': 'Internal server error'},
            status_code=500,
            headers={'Content-Type': 'application/json'}
        )


@app.route('/printer/mark-printed', methods=['POST'], cors=True)
def mark_message_printed():
    """Mark a message as printed.
    
    Used by the Raspberry Pi worker after successfully printing a message.
    
    Request Body:
        {"id": "uuid-string"}
        
    Returns:
        200: {"status": "ok", "id": "uuid-string"}
        400: Missing or invalid id
        500: Server error
    """
    try:
        # Parse and validate request body
        body = app.current_request.json_body or {}
        app.log.info(f"Marking message as printed: {body.get('id')}")
        
        # Validate message ID
        message_id = validators.validate_message_id(body.get('id'))
        
        # Mark message as printed in database
        db.mark_message_printed(message_id)
        
        app.log.info(f"Successfully marked message as printed: {message_id}")
        
        return Response(
            body={'status': 'ok', 'id': message_id},
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )
    except ValueError as e:
        # Validation error - return 400
        app.log.warning(f"Validation error: {e}")
        raise BadRequestError(str(e))
    except Exception as e:
        # Unexpected error - return 500
        app.log.error(f"Error marking message as printed: {e}", exc_info=True)
        return Response(
            body={'error': 'Internal server error'},
            status_code=500,
            headers={'Content-Type': 'application/json'}
        )


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring.
    
    Returns:
        200: {"status": "healthy"}
    """
    return Response(
        body={'status': 'healthy'},
        status_code=200,
        headers={'Content-Type': 'application/json'}
    )

