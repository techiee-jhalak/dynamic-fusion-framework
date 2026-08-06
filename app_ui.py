import os
import re
import tempfile
from collections import Counter
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000/predict")
DEFAULT_TEXT = "aaj ka mausam bohot accha hai! 😊"
K1, K2, K3, K4 = 0.25, 0.25, 0.30, 0.20


def compute_noise_breakdown(text: str):
    tokens = re.findall(r"\b\w+\b", text.lower())
    token_count = max(1, len(tokens))
    emoji_count = len(re.findall(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", text))
    repeated_tokens = sum(count - 1 for count in Counter(tokens).values() if count > 1)
    non_english_tokens = sum(1 for token in tokens if re.search(r"[\u0900-\u097F]", token))
    symbol_count = sum(1 for ch in text if ch in "!@#$%^&*()_+-=[]{}|;:'\",.<>/?")

    E = emoji_count / token_count
    R = repeated_tokens / token_count
    C = non_english_tokens / token_count
    S = symbol_count / token_count
    N = K1 * E + K2 * R + K3 * C + K4 * S
    return {"E": E, "R": R, "C": C, "S": S, "N": N}


def call_backend(text: str):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8", newline="") as handle:
        temp_path = handle.name

    try:
        pd.DataFrame([{"text": text}]).to_csv(temp_path, index=False)
        output_path = str(Path(temp_path).with_suffix(".predictions.csv"))
        response = requests.post(
            BACKEND_URL,
            json={"dataset_path": temp_path, "output_path": output_path},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()
    finally:
        for file_path in [temp_path, temp_path.replace(".csv", ".predictions.csv")]:
            if os.path.exists(file_path):
                os.remove(file_path)


st.set_page_config(
    page_title="Dynamic Fusion Sentiment",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# COLOR PALETTE OVERRIDES: RICH PASTEL CANVAS & HIGH-CONTRAST SIDEBAR K-VALUES
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Global Soft Lavender/Pastel Background (No More Bright White Body!) */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #cfbbf4 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Sidebar Styling with High-Contrast Text */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #DDD6FE 0%, #C4B5FD 100%) !important;
        border-right: 2px solid #A78BFA !important;
    }

    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #4C1D95 !important;
        font-weight: 800 !important;
    }

    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #3B0764 !important;
        font-size: 1rem !important;
    }

    /* Custom Highlight Badges for K-Values so they strictly POP out */
    .k-badge {
        background-color: #7C3AED !important;
        color: #FFFFFF !important;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-family: monospace;
        display: inline-block;
        box-shadow: 0 2px 5px rgba(124, 58, 237, 0.3);
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1300px;
    }

    /* Rich Lively Header Banner */
    .hero-container {
        background: linear-gradient(135deg, #FCE7F3 0%, #F3E8FF 50%, #E0F2FE 100%) !important;
        border: 2px solid #C084FC !important;
        border-radius: 24px;
        padding: 28px 36px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px rgba(168, 85, 247, 0.15);
    }
    
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #DB2777, #7C3AED, #2563EB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }

    /* Pastel Content Cards */
    .pastel-card {
        background: #F5F3FF !important;
        border: 2px solid #DDD6FE !important;
        border-radius: 20px;
        padding: 22px;
        box-shadow: 0 8px 20px rgba(124, 58, 237, 0.08);
    }

    /* Vibrant Sentiment Badges */
    .badge-positive {
        background-color: #D1FAE5 !important;
        color: #065F46 !important;
        padding: 8px 20px;
        border-radius: 30px;
        font-weight: 800;
        display: inline-block;
        border: 2px solid #34D399 !important;
    }

    .badge-negative {
        background-color: #FFE4E6 !important;
        color: #9F1239 !important;
        padding: 8px 20px;
        border-radius: 30px;
        font-weight: 800;
        display: inline-block;
        border: 2px solid #FB7185 !important;
    }

    .badge-neutral {
        background-color: #FEF3C7 !important;
        color: #78350F !important;
        padding: 8px 20px;
        border-radius: 30px;
        font-weight: 800;
        display: inline-block;
        border: 2px solid #FBBF24 !important;
    }

    /* Pastel Meter Visualizer */
    .noise-bar-container {
        width: 100%;
        background-color: #DDD6FE;
        border-radius: 12px;
        height: 14px;
        margin-top: 10px;
        overflow: hidden;
    }
    
    .noise-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #818CF8 0%, #FBBF24 50%, #F43F5E 100%);
        border-radius: 12px;
    }

    .formula-box {
        background: #F5F3FF !important;
        border-left: 6px solid #7C3AED !important;
        border: 2px solid #DDD6FE;
        padding: 18px 22px;
        border-radius: 16px;
    }

    /* Text Input Area Customization */
    .stTextArea textarea {
        background-color: #F8FAFC !important;
        color: #1E293B !important;
        border: 2px solid #C084FC !important;
        border-radius: 16px !important;
        font-size: 1rem !important;
    }

    /* Primary Action Button */
    .stButton button {
        background: linear-gradient(90deg, #EC4899, #8B5CF6) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        box-shadow: 0 4px 15px rgba(236, 72, 153, 0.3) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header Section
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-title">Dynamic Noise-Aware Sentiment</div>
        <div style="color: #4C1D95; font-size: 1.1rem; font-weight: 600;">
            Real-time Logit Routing & Composite Noise Analytics for Code-Mixed & Hinglish Text
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar with Bright White/Purple K-value Badges
with st.sidebar:
    st.header("⚙️ Formulation Weights")
    st.caption("Noise Composite Index Parameters ($N$)")

    st.markdown(f"**Emoji Weight ($k_1$):** <span class='k-badge'>{K1}</span>", unsafe_allow_html=True)
    st.markdown(f"**Repetition Weight ($k_2$):** <span class='k-badge'>{K2}</span>", unsafe_allow_html=True)
    st.markdown(f"**Code-Mixing Weight ($k_3$):** <span class='k-badge'>{K3}</span>", unsafe_allow_html=True)
    st.markdown(f"**Symbol Weight ($k_4$):** <span class='k-badge'>{K4}</span>", unsafe_allow_html=True)
    st.divider()

    st.latex(r"N = k_1 E + k_2 R + k_3 C + k_4 S")
    st.latex(r"\tilde{\alpha} = \frac{1}{1 + e^{-z}}")
    st.markdown("<div style='text-align: center; color: #4C1D95; font-weight: 600;'>where z = w_1 (L_0 - L) + w_2 N</div>", unsafe_allow_html=True)
    st.latex(r"P_{\text{Final}} = \alpha P_{\text{Lex}} + (1 - \alpha) P_{\text{Trans}}")

# Main Input Section
col_input, col_meta = st.columns([2, 1], gap="medium")

with col_input:
    text_input = st.text_area(
        "Analyze Text Input",
        value=DEFAULT_TEXT,
        height=140,
        placeholder="Type Hinglish, code-mixed text, or standard prose...",
    )
    analyze_btn = st.button("✨ Analyze Sentiment", use_container_width=True, type="primary")

with col_meta:
    st.markdown(
        """
        <div class="formula-box">
            <h4 style="margin: 0 0 8px 0; color: #4C1D95; font-size: 1.1rem; font-weight: 800;">Paper Parameters</h4>
            <div style="color: #5B21B6; line-height: 1.6; font-size: 0.95rem; font-weight: 500;">
                Continuous composite score calculation uses sigmoidal gating for dynamic routing between 
                <b style="color: #7C3AED;">P_{text{Lex}}</b> and <b style="color: #7C3AED;">P_{text{Trans}}</b>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Predictions & Dashboard Output
if analyze_btn:
    if not text_input.strip():
        st.warning("Please enter text before initiating analysis.")
    else:
        with st.spinner("Processing continuous logit routing..."):
            try:
                payload = call_backend(text_input)
                result = payload["results_sample"][0]
                noise = compute_noise_breakdown(text_input)
            except Exception as exc:
                st.error(f"Backend processing failure: {exc}")
                st.stop()

        label = str(result.get("sentiment", "neutral")).capitalize()
        confidence = float(result.get("confidence", 0.0))
        noise_score = float(noise.get("N", 0.0))

        st.divider()

        dash_col1, dash_col2 = st.columns([1.2, 1.8], gap="large")

        with dash_col1:
            badge_class = (
                "badge-positive"
                if label.lower() == "positive"
                else "badge-negative"
                if label.lower() == "negative"
                else "badge-neutral"
            )

            st.markdown(
                f"""
                <div class="pastel-card">
                    <div style="color: #5B21B6; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 800;">Predicted Class</div>
                    <div style="margin: 14px 0;">
                        <span class="{badge_class}">{label}</span>
                    </div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #2E1065; margin-top: 8px;">
                        {confidence:.1%} <span style="font-size: 0.95rem; font-weight: 600; color: #5B21B6;">Confidence</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            bar_width = min(100, max(0, int(noise_score * 100)))
            st.markdown(
                f"""
                <div class="pastel-card" style="margin-top: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #5B21B6; font-size: 0.85rem; font-weight: 800; text-transform: uppercase;">Composite Noise (N)</span>
                        <span style="color: #2E1065; font-weight: 800; font-size: 1.2rem;">{noise_score:.3f}</span>
                    </div>
                    <div class="noise-bar-container">
                        <div class="noise-bar-fill" style="width: {bar_width}%;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with dash_col2:
            st.markdown("<h4 style='color: #4C1D95; font-weight: 800;'>Weighted Noise Feature Decomposition</h4>", unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns(4)
            metrics_data = [
                ("Emoji (E)", noise["E"], "😊", "#E0E7FF", "#3730A3"),
                ("Repeat (R)", noise["R"], "🔂", "#DCFCE7", "#166534"),
                ("Code-Mix (C)", noise["C"], "🌐", "#FEF3C7", "#92400E"),
                ("Symbol (S)", noise["S"], "🔣", "#F3E8FF", "#5B21B6"),
            ]

            cols = [c1, c2, c3, c4]
            for idx, (title, val, icon, bg_color, text_color) in enumerate(metrics_data):
                with cols[idx]:
                    st.markdown(
                        f"""
                        <div class="pastel-card" style="text-align: center; padding: 16px 8px; background: {bg_color} !important; border: 2px solid {text_color}33;">
                            <div style="font-size: 1.4rem; margin-bottom: 4px;">{icon}</div>
                            <div style="color: {text_color}; font-size: 0.8rem; font-weight: 800;">{title}</div>
                            <div style="color: {text_color}; font-size: 1.25rem; font-weight: 800; margin-top: 4px;">{val:.3f}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("🔍 Inspect Full Payload & Routing Response"):
                st.json(
                    {
                        "label": label,
                        "confidence": confidence,
                        "noise_scores": noise,
                        "backend_response": payload,
                    }
                )