'use client';

import { useState, FormEvent } from 'react';
import { createMessage, ApiRequestError } from '@/lib/api';

interface MessageFormProps {
  onSuccess?: () => void;
}

export function MessageForm({ onSuccess }: MessageFormProps) {
  const [content, setContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const charCount = content.length;
  const maxChars = 280;
  const isOverLimit = charCount > maxChars;
  const isNearLimit = charCount >= 260 && charCount <= maxChars;
  const trimmedContent = content.trim();
  const isValid = trimmedContent.length > 0 && !isOverLimit;

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    
    // Clear previous messages
    setError(null);
    setSuccessMessage(null);
    
    // Validate
    if (!trimmedContent) {
      setError('Message cannot be empty');
      return;
    }
    
    if (isOverLimit) {
      setError(`Message is too long (${charCount} characters, max ${maxChars})`);
      return;
    }
    
    setIsLoading(true);
    
    try {
      await createMessage(trimmedContent);
      
      // Success!
      setContent('');
      setSuccessMessage('Message sent! It will be printed soon.');
      
      // Call success callback
      if (onSuccess) {
        onSuccess();
      }
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError(err.message);
      } else {
        setError('Failed to send message. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-4">
      <div className="space-y-2">
        <label htmlFor="message" className="block text-sm font-medium">
          Your Message
        </label>
        <textarea
          id="message"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Type your message to be printed..."
          rows={4}
          maxLength={300} // Allow typing a bit over to show error
          disabled={isLoading}
          className={`
            w-full px-4 py-3 rounded-lg border-2 
            font-mono text-base resize-none
            focus:outline-none focus:ring-2 focus:ring-offset-2
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-colors
            ${isOverLimit 
              ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
              : isNearLimit
                ? 'border-yellow-500 focus:border-yellow-500 focus:ring-yellow-500'
                : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
            }
          `}
          aria-describedby="char-count error-message"
        />
        
        <div 
          id="char-count"
          className={`
            text-sm font-mono text-right
            transition-colors
            ${isOverLimit 
              ? 'text-red-600 font-bold' 
              : isNearLimit
                ? 'text-yellow-600 font-semibold'
                : 'text-gray-600'
            }
          `}
          aria-live="polite"
        >
          {charCount} / {maxChars} characters
        </div>
      </div>

      {error && (
        <div 
          id="error-message"
          className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-800 text-sm"
          role="alert"
        >
          {error}
        </div>
      )}

      {successMessage && (
        <div 
          className="p-3 rounded-lg bg-green-50 border border-green-200 text-green-800 text-sm"
          role="status"
        >
          ✓ {successMessage}
        </div>
      )}

      <button
        type="submit"
        disabled={!isValid || isLoading}
        className={`
          w-full px-6 py-3 rounded-lg font-semibold text-base
          transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
          ${!isValid || isLoading
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800 shadow-md hover:shadow-lg'
          }
        `}
        aria-busy={isLoading}
      >
        {isLoading ? (
          <span className="flex items-center justify-center">
            <svg 
              className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" 
              xmlns="http://www.w3.org/2000/svg" 
              fill="none" 
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle 
                className="opacity-25" 
                cx="12" 
                cy="12" 
                r="10" 
                stroke="currentColor" 
                strokeWidth="4"
              />
              <path 
                className="opacity-75" 
                fill="currentColor" 
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            Sending...
          </span>
        ) : (
          'Send to Printer'
        )}
      </button>
    </form>
  );
}

