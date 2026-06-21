import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="mt-20 border-t border-white/10 pt-8 text-sm text-slate-400">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <p>© 2026 Dynamic Noise Aware Lexicon–Transformer Fusion Framework. Trusted noise-aware sentiment research.</p>
        <div className="flex flex-wrap items-center gap-4">
          <Link href="https://github.com/techiee-jhalak/dynamic-fusion-framework" className="text-cyan transition hover:text-white">
            GitHub Repository
          </Link>
          <Link href="#architecture" className="text-white/70 transition hover:text-white">
            Research
          </Link>
        </div>
      </div>
    </footer>
  );
}
