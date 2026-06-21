import Link from 'next/link';
import { ArrowRight, Cpu, Sparkles } from 'lucide-react';

const examples = [
  'Hey yaar, this movie is bomb 💥',
  'यह ठीक नहीं है, I am confused',
  'lol 😂 that was a terrible idea',
];

export default function HeroSection() {
  return (
    <section className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-glass backdrop-blur-xl lg:p-12">
      <div className="flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
        <div className="max-w-2xl space-y-6">
          <span className="inline-flex items-center gap-2 rounded-full bg-cyan/10 px-4 py-2 text-sm font-semibold text-cyan">
            <Sparkles className="h-4 w-4" /> Research + Product
          </span>
          <h1 className="text-4xl font-semibold leading-tight text-white sm:text-5xl">
            Dynamic Noise Aware Lexicon
            <br />
            <span className="text-cyan">Transformer Fusion Framework</span>
          </h1>
          <p className="max-w-xl text-slate-300 sm:text-lg">
            Dynamic Noise-Aware Sentiment Analysis for Code-Mixed Social Media Text. Explore how noise quantification and hybrid fusion improve robustness across English, Hindi, and Hinglish inputs.
          </p>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Link href="/sentiment" className="inline-flex items-center justify-center rounded-full bg-cyan px-6 py-3 text-sm font-semibold text-deep transition hover:bg-cyan/90">
              Try Demo
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
            <Link href="#architecture" className="inline-flex items-center justify-center rounded-full border border-white/10 bg-white/5 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/10">
              View Research
            </Link>
          </div>
        </div>
        <div className="grid w-full max-w-xl gap-4 sm:grid-cols-2">
          {examples.map((example) => (
            <div key={example} className="rounded-[1.5rem] border border-white/10 bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 p-5 text-sm text-slate-200 shadow-glass">
              <p className="font-semibold text-cyan">Example Input</p>
              <p className="mt-3 leading-relaxed">{example}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
