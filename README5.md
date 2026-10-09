# NFHS-5 Delhi: Financial Access vs. Financial Autonomy

Single-page Streamlit dashboard built only from published aggregate figures supplied by the project
team from an NFHS-5 Delhi report excerpt. **The figures have not been verified against the original
report. Verify before external use.** Descriptive only; no causal claims; Delhi only.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (Streamlit Community Cloud)
1. Push `app.py`, `requirements.txt`, `README.md` to a GitHub repo.
2. Go to https://share.streamlit.io, sign in with GitHub, click **Create app**.
3. Choose the repo and branch, set main file to `app.py`, click **Deploy**.

## Data
All values are hard-coded in `app.py` (indicator table, rural/urban, education). Edit them there if
the original report shows different numbers. The CSV download is generated from the same tables.
