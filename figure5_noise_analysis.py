import matplotlib.pyplot as plt
import numpy as np

categories = ['Low Noise', 'Medium Noise', 'High Noise']
models = ['VADER', 'DistilBERT', 'Static Fusion', 'Dynamic Fusion Framework']
colors = {'VADER': '#d62728', 'DistilBERT': '#1f77b4', 'Static Fusion': '#ff7f0e', 'Dynamic Fusion Framework': '#2ca02c'}
f1_data = {
    'VADER': [0.5500, 0.5000, 0.4400],
    'DistilBERT': [0.8500, 0.8000, 0.7500],
    'Static Fusion': [0.8500, 0.8000, 0.7500],
    'Dynamic Fusion Framework': [0.8850, 0.8620, 0.8520]
}

fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)
for m in models:
    ax.plot(categories, f1_data[m], marker='o', color=colors[m], linewidth=2.5, label=m)
ax.set_title('Macro F1-Score Sensitivity Across Noise Levels', fontsize=12, fontweight='bold')
ax.set_xlabel('Linguistic Noise Level (N)')
ax.set_ylabel('F1-Score')
ax.set_ylim(0.3, 1.05)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='lower left')
plt.tight_layout()
plt.savefig('figure5_noise_sensitivity.svg', bbox_inches='tight')
print("Figure 5 generated successfully!")
