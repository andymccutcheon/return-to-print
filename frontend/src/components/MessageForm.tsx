'use client';

import { useState, FormEvent } from 'react';
import { createMessage, ApiRequestError } from '@/lib/api';

interface MessageFormProps {
  onSuccess?: () => void;
}

export function MessageForm({ onSuccess }: MessageFormProps) {
  const [name, setName] = useState('');
  const [content, setContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const trimmedName = name.trim();
  const trimmedContent = content.trim();
  const charCount = content.length;
  const maxChars = 280;
  const maxNameChars = 50;
  const isOverLimit = charCount > maxChars;
  const isNameOverLimit = name.length > maxNameChars;
  const isValid = trimmedName.length > 0 && trimmedContent.length > 0 && !isOverLimit && !isNameOverLimit;

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    
    // Clear previous messages
    setError(null);
    setSuccessMessage(null);
    
    // Validate name
    if (!trimmedName) {
      setError('NAME REQUIRED');
      return;
    }
    
    if (isNameOverLimit) {
      setError(`NAME TOO LONG (${name.length}/${maxNameChars})`);
      return;
    }
    
    // Validate content
    if (!trimmedContent) {
      setError('MESSAGE REQUIRED');
      return;
    }
    
    if (isOverLimit) {
      setError(`MESSAGE TOO LONG (${charCount}/${maxChars})`);
      return;
    }
    
    setIsLoading(true);
    
    try {
      await createMessage(trimmedName, trimmedContent);
      
      // Success!
      setName('');
      setContent('');
      setSuccessMessage('MESSAGE QUEUED FOR PRINTING');
      
      // Call success callback
      if (onSuccess) {
        onSuccess();
      }
      
      // Clear success message after 4 seconds
      setTimeout(() => {
        setSuccessMessage(null);
      }, 4000);
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError(err.message.toUpperCase());
      } else {
        setError('FAILED TO SEND. TRY AGAIN.');
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-4">
      {/* Name Field */}
      <div className="space-y-1">
        <label htmlFor="name" className="block receipt-text text-sm font-bold">
          NAME:
        </label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Your name..."
          maxLength={60}
          disabled={isLoading}
          className={`
            w-full px-3 py-2 receipt-text text-sm
            border-2 bg-white
            disabled:opacity-50 disabled:cursor-not-allowed
            ${isNameOverLimit 
              ? 'border-black bg-black text-white' 
              : 'border-black'
            }
          `}
          aria-describedby="name-counter"
        />
        <div 
          id="name-counter"
          className={`
            char-counter text-xs
            ${isNameOverLimit ? 'font-bold' : ''}
          `}
        >
          {name.length} / {maxNameChars}
        </div>
      </div>

      {/* Message Field */}
      <div className="space-y-1">
        <label htmlFor="message" className="block receipt-text text-sm font-bold">
          MSG:
        </label>
        <textarea
          id="message"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Type your message..."
          rows={5}
          maxLength={300}
          disabled={isLoading}
          className={`
            w-full px-3 py-2 receipt-text text-sm
            border-2 resize-none bg-white
            disabled:opacity-50 disabled:cursor-not-allowed
            ${isOverLimit 
              ? 'border-black bg-black text-white' 
              : 'border-black'
            }
          `}
          aria-describedby="message-counter"
        />
        <div 
          id="message-counter"
          className={`
            char-counter text-xs
            ${isOverLimit ? 'font-bold' : ''}
          `}
        >
          {charCount} / {maxChars} CHAR MAX
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div 
          className="receipt-message error"
          role="alert"
        >
          ⚠ {error}
        </div>
      )}

      {/* Success Message */}
      {successMessage && (
        <div 
          className="receipt-message success animate-paper-feed"
          role="status"
        >
          ✓ {successMessage}
        </div>
      )}

      {/* Submit Button */}
      <div className="pt-2">
        <button
          type="submit"
          disabled={!isValid || isLoading}
          className="w-full receipt-button text-sm"
          aria-busy={isLoading}
        >
          {isLoading ? (
            <span className="processing-text">PROCESSING...</span>
          ) : (
            <span>
              ┌─────────────────────┐
              <br />
              │ SUBMIT TO PRINT │
              <br />
              └─────────────────────┘
            </span>
          )}
        </button>
      </div>

      {isLoading && (
        <div className="text-center text-xs receipt-text processing-text">
          QUEUING MESSAGE...
        </div>
      )}
    </form>
  );
}
