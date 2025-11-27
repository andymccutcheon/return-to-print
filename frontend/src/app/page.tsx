'use client';

import { MessageForm } from '@/components/MessageForm';

export default function Home() {
  // Get current date/time for receipt header
  const now = new Date();
  const dateStr = now.toLocaleDateString('en-GB', { 
    day: '2-digit', 
    month: '2-digit', 
    year: 'numeric' 
  }).replace(/\//g, '/');
  const timeStr = now.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false 
  });

  return (
    <div className="min-h-screen py-8 px-4">
      {/* Receipt Paper Container */}
      <main className="receipt-paper mx-auto">
        {/* Top Perforation */}
        <div className="perforation-top"></div>
        
        {/* Receipt Header */}
        <header className="px-6 pt-8 pb-4">
          <div className="receipt-header mb-3">
            <div className="text-center font-bold text-2xl mb-3">RECEIPT ME</div>
            <div className="separator-line"></div>
          </div>
          
          <div className="date-stamp text-center text-black mt-3">
            DATE: {dateStr}  TIME: {timeStr}
          </div>
        </header>

        <div className="separator-line"></div>

        {/* Form Section */}
        <section className="px-6 pt-6 pb-4">
          <div className="mb-6 text-center">
            <p className="receipt-text text-sm">
              THANKS FOR STOPPING BY!
            </p>
            <p className="receipt-text text-sm mt-1">
              SEND US A MESSAGE BELOW!
            </p>
          </div>

          <MessageForm />
        </section>

        <div className="separator-line"></div>

        {/* Footer */}
        <footer className="px-6 py-8 text-center">
          <p className="receipt-text text-xs mb-2">
            THANKS!
          </p>
          <p className="receipt-text text-xs font-bold">
            Andy, Annie, Newt & Harold
          </p>
        </footer>

        {/* Bottom Perforation */}
        <div className="perforation-bottom"></div>
      </main>
    </div>
  );
}
