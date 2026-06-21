export default function OverviewSection() {
  return (
    <section className="mt-12 space-y-8" id="overview">
      <div className="grid gap-6 lg:grid-cols-2 lg:items-center">
        <div className="space-y-4">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-cyan">About the Framework</p>
          <h2 className="text-3xl font-semibold text-white sm:text-4xl">
            Research-grade sentiment analysis for noisy code-mixed text.
          </h2>
          <p className="max-w-lg text-slate-300">
            The Dynamic Noise Aware Lexicon–Transformer Fusion Framework addresses the challenge of noisy, mixed-language social media posts by combining lexicon-based sentiment heuristics with transformer-based contextual modeling. The framework learns dynamic fusion weights from explicit noise signals, producing more robust predictions for short, informal text.
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          {[
            {
              title: 'Noise Quantification',
              desc: 'Emoji, code-mixing, repetition and symbol features capture social media noise.',
            },
            {
              title: 'Dynamic Fusion',
              desc: 'Adaptive alpha weights control lexicon vs transformer influence.',
            },
            {
              title: 'Model Comparison',
              desc: 'Evaluate VADER, DistilBERT, BERTweet, static and dynamic fusion.',
            },
            {
              title: 'Production Ready',
              desc: 'FastAPI backend, dataset manager, training center, and experiment tracking.',
            },
          ].map((card) => (
            <div key={card.title} className="rounded-[1.5rem] border border-white/10 bg-white/5 p-6 shadow-glass">
              <h3 className="text-xl font-semibold text-white">{card.title}</h3>
              <p className="mt-3 text-slate-300">{card.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
