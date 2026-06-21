import './globals.css';
import type { Metadata } from 'next';
import NavBar from '@/components/NavBar';
import Sidebar from '@/components/Sidebar';

export const metadata: Metadata = {
  title: 'Dynamic Noise Aware Lexicon–Transformer Fusion Framework',
  description: 'Dynamic Noise-Aware Sentiment Analysis for Code-Mixed Social Media Text.',
  metadataBase: new URL('http://localhost:3000'),
  openGraph: {
    title: 'Dynamic Noise Aware Lexicon–Transformer Fusion Framework',
    description: 'Dynamic Noise-Aware Sentiment Analysis for Code-Mixed Social Media Text.',
    type: 'website',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-deep text-slate-100 antialiased">
        <NavBar />
        <div className="mx-auto flex w-full max-w-[1400px] gap-6 px-4 py-6 lg:px-8">
          <aside className="hidden w-64 shrink-0 lg:block">
            <Sidebar />
          </aside>
          <main className="min-h-[80vh] w-full rounded-md bg-surface/30 p-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
