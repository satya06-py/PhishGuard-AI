# PhishGuard AI — Advanced Python / ML Project

PhishGuard AI is an educational phishing-URL screening prototype. It combines character-level TF-IDF patterns with engineered URL-structure features and trains a Logistic Regression classifier. The Streamlit interface supports single URL checks and batch CSV analysis.

## Important limitation

The included `data/demo_urls.csv` is a tiny demonstration dataset, not suitable for real-world security decisions. Its predictions are not reliable and may be misleading. For meaningful results, train on a large, recent, legally obtained and independently vetted dataset. Deduplicate domains, split by registered domain or time to prevent leakage, and evaluate precision, recall, PR-AUC, false-positive rate and calibration. Never use this prototype as the only security control.

## Features

- Character n-gram URL model
- Engineered URL signals: length, host/path/query structure, IP host, suspicious terms and punycode
- Hold-out evaluation
- Streamlit dashboard for single URLs
- Batch CSV scoring and downloadable results
- Human-readable heuristic red-flag explanations
- Unit tests

## VS Code setup (Windows)

1. Install Python 3.11 or 3.12 and VS Code.
2. Open this folder in VS Code using **File → Open Folder**.
3. Select **Terminal → New Terminal**.
4. Create a virtual environment:

   ```powershell
   py -3.11 -m venv .venv
   ```

5. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

   Alternatively, in Command Prompt run `.venv\Scripts\activate.bat`.

6. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

7. Train the demo model:

   ```powershell
   python train.py
   ```

8. Launch the app:

   ```powershell
   streamlit run app.py
   ```

9. Open the local URL printed in the terminal (usually `http://localhost:8501`).

## Dataset format

Create a CSV with columns `url,label`, where 0 means legitimate and 1 means phishing.

```csv
url,label
https://trusted-domain.com,0
http://fake-login.example.net/verify,1
```

Train with your dataset:

```powershell
python train.py --data data/my_urls.csv
```

The trained model is saved at `models/phishguard.joblib`.

## Tests

Install pytest and run:

```powershell
pip install pytest
pytest -q
```

## Advanced next steps

1. Use a large, recent, properly licensed phishing and benign URL dataset.
2. Split by registered domain and time to reduce leakage.
3. Add reputation features through safe, rate-limited services.
4. Add SHAP or permutation explanations after validating feature behavior.
5. Add FastAPI inference, Docker, CI tests and model monitoring.

## Structure

```text
PhishGuard_AI/
├── app.py
├── train.py
├── requirements.txt
├── data/demo_urls.csv
├── models/
├── phishguard/
│   ├── __init__.py
│   ├── features.py
│   └── pipeline.py
└── tests/test_features.py
```
