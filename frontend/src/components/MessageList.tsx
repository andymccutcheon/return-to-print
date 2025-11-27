'use client';

import { useEffect, useState } from 'react';
import { getRecentMessages, ApiRequestError, formatTimestamp, getRelativeTime } from '@/lib/api';
import type { Message } from '@/types/message';

interface MessageListProps {
  refreshTrigger?: number; // Change this value to trigger a refresh
}

export function MessageList({ refreshTrigger }: MessageListProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function fetchMessages() {
    setError(null);
    setIsLoading(true);
    
    try {
      const fetchedMessages = await getRecentMessages();
      setMessages(fetchedMessages);
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError(err.message);
      } else {
        setError('Failed to load messages. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    fetchMessages();
  }, [refreshTrigger]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Recent Messages</h2>
        <div className="space-y-3" aria-label="Loading messages">
          {[...Array(3)].map((_, i) => (
            <div 
              key={i}
              className="animate-pulse bg-gray-200 rounded-lg p-4 space-y-2"
            >
              <div className="h-4 bg-gray-300 rounded w-3/4"></div>
              <div className="h-3 bg-gray-300 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Recent Messages</h2>
        <div className="p-4 rounded-lg bg-red-50 border border-red-200">
          <p className="text-red-800 text-sm mb-3">{error}</p>
          <button
            onClick={fetchMessages}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm font-medium"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Recent Messages</h2>
        <div className="text-center py-12 px-4 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <svg 
            className="mx-auto h-12 w-12 text-gray-400" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
            aria-hidden="true"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" 
            />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">No messages yet</h3>
          <p className="mt-2 text-sm text-gray-600">
            Be the first to send a message to the printer!
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Recent Messages</h2>
        <button
          onClick={fetchMessages}
          className="text-sm text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1"
          title="Refresh messages"
        >
          <svg 
            className="w-4 h-4" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
            aria-hidden="true"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" 
            />
          </svg>
          Refresh
        </button>
      </div>

      <div className="space-y-3">
        {messages.map((message) => (
          <MessageItem key={message.id} message={message} />
        ))}
      </div>

      {messages.length === 10 && (
        <p className="text-xs text-gray-500 text-center italic">
          Showing most recent 10 messages
        </p>
      )}
    </div>
  );
}

function MessageItem({ message }: { message: Message }) {
  const isPrinted = message.printed === 'true'; // Remember: it's a string!
  const timestamp = formatTimestamp(message.created_at);
  const relativeTime = getRelativeTime(message.created_at);

  return (
    <article 
      className={`
        p-4 rounded-lg border-2 transition-all
        ${isPrinted 
          ? 'bg-green-50 border-green-200' 
          : 'bg-white border-gray-200'
        }
      `}
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <time 
          className="text-xs text-gray-600 font-medium"
          dateTime={message.created_at}
          title={timestamp}
        >
          {relativeTime}
        </time>
        
        {isPrinted && (
          <span 
            className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-green-200 text-green-800 text-xs font-semibold"
            title={`Printed ${message.printed_at ? formatTimestamp(message.printed_at) : ''}`}
          >
            <svg 
              className="w-3 h-3" 
              fill="currentColor" 
              viewBox="0 0 20 20"
              aria-hidden="true"
            >
              <path 
                fillRule="evenodd" 
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" 
                clipRule="evenodd" 
              />
            </svg>
            Printed
          </span>
        )}
      </div>

      <p className="text-base font-mono leading-relaxed text-gray-900 break-words whitespace-pre-wrap">
        {message.content}
      </p>
      
      {!isPrinted && (
        <div className="mt-2 flex items-center gap-1 text-xs text-gray-500">
          <svg 
            className="w-3 h-3 animate-pulse" 
            fill="currentColor" 
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <circle cx="10" cy="10" r="3" />
          </svg>
          Waiting to print...
        </div>
      )}
    </article>
  );
}

