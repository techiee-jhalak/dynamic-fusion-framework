# Discussion Summary

## Why Dynamic Fusion Worked
Dynamic Fusion adds robustness by adaptively weighting lexicon and transformer predictions based on text length and noise characteristics.

## Why Noise Quantification Helped
Noise quantification exposed code-mixing, emoji density, and symbol signals that help the fusion layer decide when to trust lexicon or transformer outputs.

## Impact of Code-Mixing
Code-mixed tweets have higher noise scores and benefit from the dynamic fusion mechanism because the transformer alone can be less reliable.

## Role of VADER
VADER provides fast lexicon-based polarity scores and anchors performance on noisy, emoji-rich sentences.

## Role of DistilBERT
DistilBERT contributes contextual understanding and high semantic accuracy, especially in longer or less noisy text segments.

## Limitations
The current dataset is small and uses a sample CSV. BERTweet is loaded without a task-specific classifier head, so real production evaluation should include fine-tuning.

## Practical Implications
A dynamic noise-aware fusion approach is suitable for production sentiment systems on social media, where code-mixing and informal noise are common.
