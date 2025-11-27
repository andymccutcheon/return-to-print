import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Receipt Me - Send Messages to the Thermal Printer",
  description: "A public art installation where your messages are printed on a thermal receipt printer. Submit your message and watch it join the queue!",
  keywords: ["thermal printer", "art installation", "public art", "receipt printer", "interactive art"],
  authors: [{ name: "Receipt Me" }],
  openGraph: {
    title: "Receipt Me - Thermal Printer Messages",
    description: "Send messages to be printed on a thermal receipt printer",
    type: "website",
    siteName: "Receipt Me",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
