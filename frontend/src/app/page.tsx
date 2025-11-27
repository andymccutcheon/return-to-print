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
    <div className="min-h-screen bg-[#FFFEF7] py-8 px-4">
      {/* Receipt Paper Container */}
      <main className="receipt-paper mx-auto">
        {/* Top Perforation */}
        <div className="perforation-top"></div>
        
        {/* Receipt Header */}
        <header className="px-6 pt-8 pb-4">
          <div className="receipt-header text-lg mb-4">
            <div className="ascii-art text-center">
═══════════════════════════
   RETURN TO PRINT
   Message Submission
═══════════════════════════
            </div>
          </div>
          
          <div className="date-stamp text-center text-black">
            DATE: {dateStr}  TIME: {timeStr}
          </div>
        </header>

        <div className="separator-line"></div>

        {/* Form Section */}
        <section className="px-6 py-6">
          <div className="mb-4 text-center">
            <p className="receipt-text text-sm">
              SUBMIT YOUR MESSAGE BELOW
            </p>
            <p className="receipt-text text-xs mt-1">
              IT WILL BE PRINTED ON A
            </p>
            <p className="receipt-text text-xs">
              THERMAL RECEIPT PRINTER
            </p>
          </div>

          <div className="separator-line my-4"></div>

          <MessageForm />
        </section>

        <div className="separator-line"></div>

        {/* Footer */}
        <footer className="px-6 py-6 text-center">
          <p className="receipt-text text-xs mb-2">
            THANK YOU FOR PRINTING
          </p>
          <p className="receipt-text text-xs font-bold">
            returntoprint.xyz
          </p>
          <div className="mt-4 text-xs">
            <div className="ascii-art text-center text-[10px] leading-tight">
-------------------------------
  A PUBLIC ART INSTALLATION
-------------------------------
            </div>
          </div>
        </footer>

        {/* Bottom Perforation */}
        <div className="perforation-bottom"></div>
      </main>
    </div>
  );
}
