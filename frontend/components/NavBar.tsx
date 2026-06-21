import Link from 'next/link'

export default function NavBar() {
  return (
    <header className="w-full border-b border-surface/20 bg-surface/10">
      <div className="mx-auto flex max-w-[1400px] items-center justify-between gap-4 px-4 py-3 lg:px-8">
        <Link href="/" className="text-lg font-semibold">
          Dynamic Noise Aware Lexicon–Transformer Fusion Framework
        </Link>
        <nav className="hidden gap-4 sm:flex">
          <Link href="/dashboard" className="hover:underline">Dashboard</Link>
          <Link href="/sentiment" className="hover:underline">Sentiment</Link>
          <Link href="/noise-analysis" className="hover:underline">Noise</Link>
          <Link href="/datasets" className="hover:underline">Datasets</Link>
          <Link href="/training" className="hover:underline">Training</Link>
          <Link href="/experiments" className="hover:underline">Experiments</Link>
          <Link href="/model-comparison" className="hover:underline">Models</Link>
          <Link href="/settings" className="hover:underline">Settings</Link>
        </nav>
      </div>
    </header>
  )
}
