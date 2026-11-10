from pathlib import Path
from urllib.parse import urlparse
import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "phishguard.joblib"

st.set_page_config(page_title="PhishGuard AI", page_icon="🛡️", layout="wide")


@st.cache_resource
def load_artifact():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


def normalise_url(url):
    url = url.strip()
    return url if "://" in url else "http://" + url


def heuristic_signals(url):
    parsed = urlparse(normalise_url(url))
    host = parsed.hostname or ""
    signals = []
    if parsed.scheme.lower() != "https":
        signals.append("The URL does not use HTTPS.")
    if "@" in url:
        signals.append("The @ symbol can make the actual destination confusing.")
    if len(host) > 35:
        signals.append("The hostname is unusually long.")
    if host.replace(".", "").isdigit():
        signals.append("The hostname looks like an IP address.")
    words = ("login", "verify", "password", "urgent", "wallet", "suspended", "account")
    found = [word for word in words if word in url.lower()]
    if found:
        signals.append("Contains high-risk wording: " + ", ".join(found) + ".")
    if "xn--" in host.lower():
        signals.append("The hostname contains an internationalised/punycode label.")
    if not signals:
        signals.append("No simple URL red flags detected; this does not prove the site is safe.")
    return signals


st.title("🛡️ PhishGuard AI")
st.caption("Machine-learning based phishing URL risk screening")
st.warning("Educational prototype. A prediction is not proof. Never enter passwords or payment details based only on this tool.")

artifact = load_artifact()
if artifact is None:
    st.error("Model not found. Run `python train.py` in the VS Code terminal, then refresh this page.")
    st.stop()

model = artifact["model"]
metadata = artifact.get("metadata", {})
with st.sidebar:
    st.header("Model information")
    st.write(f"Training rows: **{metadata.get('training_rows', 'unknown')}**")
    st.write("Character n-grams + engineered URL features + Logistic Regression")
    st.caption(metadata.get("warning", ""))

url = st.text_input("Paste a URL to check", placeholder="https://example.com/account")
if st.button("Analyze URL", type="primary") and url.strip():
    probability = float(model.predict_proba([url.strip()])[0, 1])
    left, right = st.columns([1, 2])
    with left:
        st.metric("Estimated phishing probability", f"{probability * 100:.1f}%")
        if probability >= 0.5:
            st.error("Higher phishing risk")
        else:
            st.success("Lower phishing risk")
    with right:
        st.subheader("URL review signals")
        for signal in heuristic_signals(url.strip()):
            st.write("• " + signal)
        st.progress(probability)
    st.caption("This score is not a calibrated guarantee. Verify the domain through an independent trusted channel.")

st.divider()
st.subheader("Batch analysis")
uploaded = st.file_uploader("Upload a CSV containing a column named `url`", type=["csv"])
if uploaded:
    try:
        batch = pd.read_csv(uploaded)
        if "url" not in batch.columns:
            st.error("CSV needs a column named 'url'.")
        else:
            batch["phishing_probability"] = model.predict_proba(
                batch["url"].fillna("").astype(str)
            )[:, 1]
            batch["risk"] = batch["phishing_probability"].apply(
                lambda p: "Higher risk" if p >= 0.5 else "Lower risk"
            )
            st.dataframe(batch, use_container_width=True)
            st.download_button(
                "Download results", batch.to_csv(index=False).encode("utf-8"),
                file_name="phishguard_results.csv", mime="text/csv"
            )
    except Exception as exc:
        st.error(f"Could not process CSV: {exc}")

st.caption("PhishGuard AI • Python • scikit-learn • Streamlit")
