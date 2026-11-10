from pathlib import Path
import argparse
import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from phishguard.pipeline import build_model

ROOT = Path(__file__).resolve().parent
DEFAULT_DATA = ROOT / "data" / "demo_urls.csv"
MODEL_PATH = ROOT / "models" / "phishguard.joblib"


def main():
    parser = argparse.ArgumentParser(description="Train PhishGuard URL classifier")
    parser.add_argument("--data", default=str(DEFAULT_DATA), help="CSV with url,label columns")
    args = parser.parse_args()

    data = pd.read_csv(args.data)
    if not {"url", "label"}.issubset(data.columns):
        raise SystemExit("CSV must contain columns: url,label")
    data = data.dropna(subset=["url", "label"]).drop_duplicates("url")
    data["label"] = data["label"].astype(int)
    if set(data["label"].unique()) != {0, 1}:
        raise SystemExit("Training data must contain both labels: 0=legitimate, 1=phishing")
    if len(data) < 20:
        raise SystemExit("Use at least 20 labelled rows; substantially more is recommended.")

    X_train, X_test, y_train, y_test = train_test_split(
        data["url"].astype(str), data["label"],
        test_size=0.25, random_state=42, stratify=data["label"]
    )
    model = build_model()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]
    print("\nEvaluation on hold-out split")
    print(classification_report(y_test, predictions,
          target_names=["Legitimate", "Phishing"], zero_division=0))
    print("Confusion matrix [rows=true, cols=predicted]:")
    print(confusion_matrix(y_test, predictions))
    print(f"ROC-AUC: {roc_auc_score(y_test, probabilities):.3f}")

    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump({
        "model": model,
        "metadata": {
            "training_rows": int(len(data)),
            "warning": "Demo model if trained on data/demo_urls.csv. Replace with a large, recent, vetted dataset."
        }
    }, MODEL_PATH)
    print(f"Saved model: {MODEL_PATH}")


if __name__ == "__main__":
    main()
