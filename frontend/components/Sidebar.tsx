import Link from 'next/link'

const links = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/sentiment', label: 'Sentiment' },
  { href: '/noise-analysis', label: 'Noise Analysis' },
  { href: '/datasets', label: 'Datasets' },
  { href: '/training', label: 'Training' },
  { href: '/experiments', label: 'Experiments' },
  { href: '/model-comparison', label: 'Model Comparison' },
  { href: '/settings', label: 'Settings' },
]

export default function Sidebar() {
  return (
    <div className="sticky top-6 rounded-md border border-surface/10 bg-surface/5 p-4">
      <ul className="flex flex-col gap-2">
        {links.map((l) => (
          <li key={l.href}>
            <Link href={l.href} className="block rounded px-3 py-2 hover:bg-surface/10">
              {l.label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
