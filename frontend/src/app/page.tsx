'use client';

import { useState } from 'react';
import { MessageForm } from '@/components/MessageForm';
import { MessageList } from '@/components/MessageList';

export default function Home() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  function handleMessageSuccess() {
    // Trigger a refresh of the message list
    setRefreshTrigger(prev => prev + 1);
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white border-b-2 border-gray-200 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <svg 
                className="w-6 h-6 text-white" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
                aria-hidden="true"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" 
                />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-gray-900">
                Pennant
              </h1>
              <p className="text-sm text-gray-600">
                Send messages to the thermal printer
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8 md:py-12">
        <div className="grid gap-8 md:gap-12">
          {/* Message Submission Section */}
          <section className="bg-white rounded-xl shadow-lg p-6 md:p-8 border-2 border-gray-200">
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-2">
                Send a Message
              </h2>
              <p className="text-sm text-gray-600">
                Your message will be queued and printed on a thermal receipt printer.
                Keep it under 280 characters!
              </p>
            </div>
            <MessageForm onSuccess={handleMessageSuccess} />
          </section>

          {/* Recent Messages Section */}
          <section className="bg-white rounded-xl shadow-lg p-6 md:p-8 border-2 border-gray-200">
            <MessageList refreshTrigger={refreshTrigger} />
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 pb-8 text-center text-sm text-gray-500">
        <p>
          A public art installation by{' '}
          <a 
            href="https://returntoprint.xyz" 
            className="text-blue-600 hover:text-blue-800 font-medium"
            target="_blank"
            rel="noopener noreferrer"
          >
            Return to Print
          </a>
        </p>
      </footer>
    </div>
  );
}
