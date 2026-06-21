import matplotlib.pyplot as plt
import numpy as np

models = ['Logistic Regression', 'VADER', 'DistilBERT', 'BERTweet', 'Static Fusion', 'Dynamic Fusion Framework']
data = {
    'Accuracy': [0.6840, 0.5210, 0.8333, 0.5000, 0.8333, 0.8750],
    'Precision': [0.6810, 0.5530, 0.7890, 0.6120, 1.0000, 0.8920],
    'Recall': [0.6790, 0.5180, 0.7910, 1.0000, 0.6667, 0.8610],
    'F1-Score': [0.6800, 0.4950, 0.8000, 0.6200, 0.8000, 0.8520]
}

x = np.arange(len(models))
width = 0.2

fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
rects1 = ax.bar(x - 1.5*width, data['Accuracy'], width, label='Accuracy', color='#1f77b4')
rects2 = ax.bar(x - 0.5*width, data['Precision'], width, label='Precision', color='#aec7e8')
rects3 = ax.bar(x + 0.5*width, data['Recall'], width, label='Recall', color='#ff7f0e')
rects4 = ax.bar(x + 1.5*width, data['F1-Score'], width, label='F1-Score', color='#ffbb78')

ax.set_ylabel('Score', fontsize=12, fontweight='bold')
ax.set_title('Model Performance Comparison across Metrics', fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(models, rotation=15, ha='right', fontsize=10)
ax.set_ylim(0, 1.1)
ax.legend(loc='upper right', frameon=True)
ax.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('figure4_performance.png', bbox_inches='tight')
plt.savefig('figure4_performance.svg', bbox_inches='tight')
print("Figure 4 generated successfully!")
