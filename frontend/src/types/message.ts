/**
 * Message type definition
 * 
 * IMPORTANT: The `printed` field is a STRING ("true" or "false"), 
 * not a boolean. This is due to DynamoDB GSI constraints.
 */
export interface Message {
  id: string;
  name: string; // Sender name (1-50 characters)
  content: string;
  created_at: string; // ISO 8601 timestamp
  printed: 'true' | 'false'; // String, not boolean!
  printed_at: string | null; // ISO 8601 timestamp or null
}

/**
 * Request payload for creating a new message
 */
export interface CreateMessageRequest {
  name: string; // Sender name (required, 1-50 characters)
  content: string;
}

/**
 * Response from GET /messages/recent
 */
export interface RecentMessagesResponse {
  messages: Message[];
}

/**
 * Error response from Chalice backend
 */
export interface ApiError {
  Code: string;
  Message: string;
}

