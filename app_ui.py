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
    N = 0.25 * E + 0.25 * R + 0.30 * C + 0.20 * S
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


st.set_page_config(page_title="Dynamic Fusion Sentiment", page_icon="🧠", layout="centered")
st.title("Dynamic Noise-Aware Sentiment Studio")
st.caption("Hinglish and code-mixed text analysis")

text_input = st.text_area("Enter social text", value=DEFAULT_TEXT, height=120)

if st.button("Analyze Sentiment", use_container_width=True):
    if not text_input.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("Analyzing..."):
            try:
                payload = call_backend(text_input)
                result = payload["results_sample"][0]
                noise = compute_noise_breakdown(text_input)
            except Exception as exc:
                st.error(f"Backend request failed: {exc}")
                st.stop()

        label = result["sentiment"].capitalize()
        confidence = result["confidence"]
        if label.lower() == "positive":
            st.success(f"Predicted Sentiment: {label}")
        elif label.lower() == "negative":
            st.error(f"Predicted Sentiment: {label}")
        else:
            st.info(f"Predicted Sentiment: {label}")

        st.metric("Prediction", label, f"{confidence:.1%} confidence")

        st.subheader("Noise Breakdown")
        cols = st.columns(5)
        for idx, (key, value) in enumerate(noise.items()):
            with cols[idx]:
                st.metric(key, f"{value:.3f}")

        with st.expander("Detailed breakdown"):
            st.json({"backend_response": payload, "noise_scores": noise})
