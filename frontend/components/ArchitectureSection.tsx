const steps = [
  { label: 'Input Text', desc: 'Raw social media sentence with code-mixed tokens.', color: 'from-cyan to-indigo' },
  { label: 'Noise Quantification', desc: 'Compute E, R, C, S, and N scores.', color: 'from-indigo to-slate-900' },
  { label: 'Dynamic Alpha', desc: 'Calculate α = 1 / (1 + exp(-(w1(20-L)+w2N))).', color: 'from-clate-900 to-cyan' },
  { label: 'VADER + DistilBERT', desc: 'Obtain lexicon and transformer sentiment scores.', color: 'from-cyan to-slate-900' },
  { label: 'Fusion Layer', desc: 'Compute final sentiment Sfinal = αSv + (1-α)Sd.', color: 'from-indigo to-cyan' },
  { label: 'Final Prediction', desc: 'Produce sentiment label, confidence, and explanation.', color: 'from-slate-900 to-indigo' },
];

export default function ArchitectureSection() {
  return (
    <section className="mt-16 rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-glass backdrop-blur-xl" id="architecture">
      <div className="space-y-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-cyan">Framework Architecture</p>
            <h2 className="mt-3 text-3xl font-semibold text-white sm:text-4xl">Dynamic Fusion Workflow</h2>
          </div>
          <div className="rounded-full border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-300">
            α = 1 / (1 + exp(-(w1(20-L)+w2N)))
          </div>
        </div>
        <div className="grid gap-6 lg:grid-cols-3">
          {steps.map((step) => (
            <div key={step.label} className="rounded-[1.75rem] border border-white/10 bg-slate-950/70 p-6 shadow-glass">
              <span className={`inline-flex rounded-full bg-gradient-to-r ${step.color} px-4 py-2 text-xs font-semibold uppercase text-white/90`}>
                {step.label}
              </span>
              <p className="mt-4 text-slate-300">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
