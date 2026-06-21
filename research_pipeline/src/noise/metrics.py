from typing import Dict


def compute_noise_metrics(sample_stats: Dict) -> Dict:
    # expects keys: emoji_count, token_count, repeated_tokens, non_english_tokens, symbol_count
    token_count = sample_stats.get('token_count', 1) or 1
    E = sample_stats.get('emoji_count', 0) / token_count
    R = sample_stats.get('repeated_tokens', 0) / token_count
    C = sample_stats.get('non_english_tokens', 0) / token_count
    S = sample_stats.get('symbol_count', 0) / token_count
    N = 0.25 * E + 0.25 * R + 0.30 * C + 0.20 * S
    return {'E': E, 'R': R, 'C': C, 'S': S, 'N': N}
