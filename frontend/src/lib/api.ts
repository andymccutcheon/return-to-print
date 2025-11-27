import type { Message, CreateMessageRequest, RecentMessagesResponse, ApiError } from '@/types/message';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

if (!API_BASE_URL) {
  throw new Error('NEXT_PUBLIC_API_BASE_URL environment variable is not set');
}

/**
 * Custom error class for API errors
 */
export class ApiRequestError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiRequestError';
  }
}

/**
 * Create a new message
 * 
 * @param content - Message content (1-280 characters)
 * @returns The created message object
 * @throws {ApiRequestError} If the request fails or validation fails
 */
export async function createMessage(content: string): Promise<Message> {
  const trimmedContent = content.trim();
  
  // Client-side validation
  if (!trimmedContent) {
    throw new ApiRequestError('Message content cannot be empty', 400);
  }
  
  if (trimmedContent.length > 280) {
    throw new ApiRequestError(`Message too long: ${trimmedContent.length} characters (max 280)`, 400);
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content: trimmedContent } as CreateMessageRequest),
    });
    
    if (!response.ok) {
      // Parse Chalice error format
      const errorData: ApiError = await response.json();
      throw new ApiRequestError(
        errorData.Message || 'Failed to create message',
        response.status,
        errorData.Code
      );
    }
    
    const message: Message = await response.json();
    return message;
  } catch (error) {
    if (error instanceof ApiRequestError) {
      throw error;
    }
    
    // Network or other errors
    throw new ApiRequestError(
      error instanceof Error ? error.message : 'Network error occurred',
      0
    );
  }
}

/**
 * Get recent messages (max 10, newest first)
 * 
 * @returns Array of recent messages
 * @throws {ApiRequestError} If the request fails
 */
export async function getRecentMessages(): Promise<Message[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/messages/recent`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new ApiRequestError(
        errorData.Message || 'Failed to fetch messages',
        response.status,
        errorData.Code
      );
    }
    
    const data: RecentMessagesResponse = await response.json();
    return data.messages || [];
  } catch (error) {
    if (error instanceof ApiRequestError) {
      throw error;
    }
    
    // Network or other errors
    throw new ApiRequestError(
      error instanceof Error ? error.message : 'Network error occurred',
      0
    );
  }
}

/**
 * Format a timestamp for display
 * 
 * @param timestamp - ISO 8601 timestamp string
 * @returns Formatted date/time string
 */
export function formatTimestamp(timestamp: string): string {
  try {
    const date = new Date(timestamp);
    
    // Format as: "Nov 24, 2025 at 3:45 PM"
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  } catch {
    return timestamp;
  }
}

/**
 * Get a relative time string (e.g., "2 minutes ago")
 * 
 * @param timestamp - ISO 8601 timestamp string
 * @returns Relative time string
 */
export function getRelativeTime(timestamp: string): string {
  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffSecs < 60) {
      return 'just now';
    } else if (diffMins < 60) {
      return `${diffMins} ${diffMins === 1 ? 'minute' : 'minutes'} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} ${diffHours === 1 ? 'hour' : 'hours'} ago`;
    } else {
      return `${diffDays} ${diffDays === 1 ? 'day' : 'days'} ago`;
    }
  } catch {
    return '';
  }
}

