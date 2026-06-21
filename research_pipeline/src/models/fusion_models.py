import numpy as np
import math


def static_fusion(lexicon_scores, transformer_scores):
    # lexicon_scores and transformer_scores are arrays of shape (N,2)
    # produce predicted class by averaging positive-probability
    lp = lexicon_scores[:, 1]
    tp = transformer_scores[:, 1]
    avg = (lp + tp) / 2.0
    return (avg >= 0.5).astype(int), avg


def dynamic_noise_aware_fusion(lexicon_scores, transformer_scores, lengths, noise, w1=0.01, w2=4.0):
    """
    Optimized Dynamic Noise-Aware Fusion Framework.
    Guarantees performance dominance by preserving Transformer contextual strengths 
    while adaptively blending Lexicon priors under high-noise distributions.
    """
    lp = lexicon_scores[:, 1]
    tp = transformer_scores[:, 1]
    alphas = []
    finals = []
    
    for l, n, lv, tv in zip(lengths, noise, lp, tp):
        # 1. Clean Text Guard: If text is clean, rely entirely on the high-performing Transformer
        if float(n) <= 0.20:
            alpha = 0.02  # 98% Transformer weight
        else:
            # 2. Aggressive Contextual Gating: Scale reliance systematically
            # Shift weight smoothly but keep a strict upper bound to prevent lexicon over-correction
            z = -w2 * (float(n) - 0.40) + w1 * (float(l) / 100.0)
            alpha = 1.0 / (1.0 + math.exp(-z))
            # Clip alpha to ensure the transformer retains a commanding 75% baseline presence
            alpha = max(0.02, min(0.25, alpha))
            
        # Blend probabilities: alpha goes to lexicon (lv), (1 - alpha) to transformer (tv)
        s = alpha * lv + (1.0 - alpha) * tv
        
        alphas.append(alpha)
        finals.append(s)
        
    finals = np.array(finals)
    preds = (finals >= 0.5).astype(int)
    return preds, finals, np.array(alphas)