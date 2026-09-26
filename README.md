# IPL Match Predictor — Deployment

This folder is a self-contained, ready-to-deploy Streamlit app built on the model
trained in `IPL_Version_2_Fixed.ipynb` (one level up).

## Fix applied in this version

The raw `IPL_2021_2025_matches.csv` contains two names for the same franchise —
**"Royal Challengers Bangalore"** (pre-2024) and **"Royal Challengers Bengaluru"**
(post-rebrand). The original notebook trained on the data without merging them,
which silently created **11 encoded teams instead of 10**, split RCB's match
history and titles across two identities, and meant `team_data.py` (which only
has styling/info for "Royal Challengers Bengaluru") couldn't recognize the older
name in the dashboard.

`IPL_Version_2_Fixed.ipynb` adds a one-line normalization right after loading the
CSV (`team1`, `team2`, `toss_winner`, `winner` columns) so RCB is treated as a
single team throughout cleaning, feature engineering, training, and the dashboard.
With that fix, the notebook now reproduces the intended result: **10 teams**,
**XGBoost** selected as the best algorithm, **~54.3% held-out accuracy** on the
2025 season — matching what this deploy folder expects.

All five `.pkl` artifacts in this folder were regenerated from the fixed notebook,
so they're consistent with each other (previously, artifacts from different notebook
runs could disagree on the team count).

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit dashboard (team profiles, stadium info, head-to-head history, standings, live prediction) |
| `team_data.py` | Static reference data: franchise colors, home grounds, founding years, IPL titles, stadium capacities |
| `requirements.txt` | Python dependencies |
| `ipl_best_model.pkl` | Trained model — **XGBoost**, ~54.3% held-out accuracy (auto-updates to whichever algorithm wins the notebook's comparison) |
| `ipl_best_model_name.pkl` | Name of the winning algorithm, shown in the app header |
| `ipl_best_features.pkl` | Feature list the model expects, in order |
| `ipl_team_encoder.pkl` | `LabelEncoder` used to encode team names (10 classes) |
| `df_v2_full.pkl` | Full engineered match history (needed at prediction time to compute recent-form/head-to-head features, and to power the dashboard's history tables and charts) |

### Dashboard features

- **Hero banner** — dynamic gradient that blends the two selected teams' colors, with live stat chips (model name, seasons, matches)
- **VS matchup banner** — circular team badges + animated confidence styling on the winner reveal (with `st.balloons()` on prediction)
- **Franchise dossier cards** — glass-style gradient cards with home ground, city, founding year, IPL titles (with years), current record, and last-5-match form as colored pills
- **Head-to-head radar chart** — 4-axis comparison (overall win %, recent form, head-to-head rate, batting-first win %)
- **Tabbed navigation** — Franchise Dossiers / Head-to-Head / Form & Trends / Stadium Intel / Standings, so the page isn't one long scroll
- **Head-to-head tab** — win-share donut chart + the full match-by-match history table between the two selected teams
- **Form & Trends tab** — season-by-season win rate line chart, 2021–2025
- **Stadium Intel tab** — pick any of the 21 venues to see matches hosted, approximate capacity, batting-first win rate, toss-advantage rate, and each team's personal record there
- **Prediction panel** — custom gradient probability bars (not a generic chart) + a confidence label (Toss-up / Slight Lean / Clear Edge / Strong Favorite)
- **Standings tab** — sortable win/loss table for any season in the dataset

## 1. Run locally

```bash
cd deploy
pip install -r requirements.txt
streamlit run app.py
```

Streamlit will open the app at `http://localhost:8501`.

## 2. Deploy for free — Streamlit Community Cloud (recommended, easiest)

1. Push this `deploy/` folder to a public (or private) GitHub repo, with `app.py`,
   `requirements.txt`, and the five `.pkl` files at the repo root (or note the subfolder
   path when configuring the app).
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Click **New app**, select the repo/branch, and set the main file path to `app.py`.
4. Click **Deploy**. Streamlit Cloud installs `requirements.txt` automatically and gives
   you a public URL (`https://<your-app>.streamlit.app`) in a couple of minutes.

## 3. Alternative — Render / Railway / Hugging Face Spaces

Any host that runs a Python web process works the same way:

- **Hugging Face Spaces**: create a new Space, choose the "Streamlit" SDK, and push these
  files — it builds and hosts automatically, free tier available.
- **Render**: create a new Web Service from your repo, set the start command to
  `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`, and set the build
  command to `pip install -r requirements.txt`.
- **Railway**: similar — a `Procfile` with
  `web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0` works.

## 4. Retraining / updating the model

If you retrain the model (new season's data, different features, different algorithm),
re-export the five `.pkl` files from `IPL_Version_2_Fixed.ipynb` with the same names used
here (`joblib.dump(...)`), drop them into this folder, and redeploy — `app.py` doesn't need
to change unless the feature engineering itself changes.

## Notes / limitations

- Model accuracy is **~54%** on the single held-out 2025 season — a modest edge over a
  coin flip, not a reliable betting signal. The app includes an explicit disclaimer.
- The "Royal Challengers Bangalore" → "Royal Challengers Bengaluru" 2024 rename is now
  normalized to a single team name throughout the data and model (see "Fix applied" above).
- Predictions use the **full match history** (`df_v2_full.pkl`) to compute recent-form and
  head-to-head features, so they reflect "form as of the end of the dataset" (2025 season),
  not a specific future date.
- Stadium capacities and franchise metadata in `team_data.py` are approximate, stable
  reference facts — update them there if a franchise rebrands, relocates, or wins a
  future title.
- The notebook's Version 2 experiment (adding overall/venue/batting-first historical rates)
  actually *hurt* accuracy on this small dataset (~277 training matches) — more history
  features add noise faster than signal here. The deployed model deliberately uses the
  leaner Version 1 feature set.
