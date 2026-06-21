const items = [
  {
    title: 'Sentiment Playground',
    description: 'Test code-mixed sentences with noise-aware sentiment metrics and fusion insights.',
  },
  {
    title: 'Dataset Manager',
    description: 'Upload datasets, inspect distributions, and preview sample records.',
  },
  {
    title: 'Experiment Tracking',
    description: 'Monitor training progress, experiment metrics, and model comparisons.',
  },
  {
    title: 'API Access',
    description: 'Use REST endpoints to integrate the fusion model into applications.',
  },
];

export default function FeaturesSection() {
  return (
    <section className="mt-14">
      <div className="grid gap-6 lg:grid-cols-2">
        {items.map((item) => (
          <div key={item.title} className="rounded-[1.75rem] border border-white/10 bg-white/5 p-8 shadow-glass transition hover:-translate-y-1 hover:bg-white/10">
            <h3 className="text-xl font-semibold text-white">{item.title}</h3>
            <p className="mt-4 text-slate-300">{item.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
