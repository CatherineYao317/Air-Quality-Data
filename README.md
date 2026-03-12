# Air-Quality-Data

This repository contains the full analytical pipeline, modelling framework, and reporting outputs for our Ontario air quality study — spanning two case studies.

## Research Questions

### Case Study 1
- **CS1-RQ1** – How are daily pollutant levels (NO / AQI) associated with traffic volume after controlling for meteorology, and does the relationship vary by season?
- **CS1-RQ2** – How do pollutant concentrations vary by hour of day and weekday vs. weekend, and do these temporal patterns differ by season or station?

### Case Study 2
- **CS2-RQ1** – Does wildfire exposure (WSEI) explain the extreme AQI spikes that Case Study 1 models systematically failed to capture? *(Bayesian hierarchical regression, R/brms)*
- **CS2-RQ2** – Does adding WSEI features improve next-day AQI point-forecast accuracy, particularly on extreme days (top-decile AQI)? *(OLS / Neural Network / LSTM comparison, Python)*
- **CS2-RQ3** – Can we build a stable, interpretable wildfire-risk score that supports operational health advisories? *(Bayesian hierarchical logistic regression, R/brms)*

---

## Repository Structure

```text
Air-Quality-Data/
│
├── .github/workflows/
│   ├── README.md
│   └── pipeline.yml               ← CI: smoke test + Q1/CS1-Q2 + Quarto render
│
├── analysis/
│   ├── 00_smoke_test.py           ← lightweight CI validation
│   ├── AQProcess.ipynb            ← AQI cleaning & standardisation
│   ├── WX_TRProcess.ipynb         ← weather & traffic preprocessing
│   ├── Merge.ipynb                ← spatial join → merged_10km_daily_updated.csv
│   ├── Q1.ipynb                   ← CS1-RQ1 modelling
│   └── CS2Q2.ipynb                ← CS2-RQ2 modelling (OLS / NN / LSTM) ★
│
├── data/
│   ├── Q1_data/                   ← pre-split CS1 test sets (committed)
│   ├── wildfire/                  ← NOT committed (300–400 MB); generate with scripts/
│   │   ├── raw/                   ← downloaded ZIPs + extracted CSVs
│   │   ├── hotspots_2022_2024_canada.csv.gz
│   │   ├── hotspots_clean.csv.gz
│   │   ├── wsei_features.csv      ← intermediate WSEI cache
│   │   └── merged_with_wsei.csv   ← full CS2 modelling dataset
│   ├── air_quality_csv/
│   ├── AirQuality_ON_2022_2024.csv
│   ├── Hourly_AQI_EPA.xlsb
│   ├── data_dictionary.md         ← full data dictionary + WSEI design rationale
│   ├── merged_10km_daily_updated.csv
│   ├── traffic_ON_2022_2024.csv
│   └── weather_ON_2022_2024.csv
│
├── model/
│   ├── CS2RQ2_models/             ← CS2-RQ2 pretrained weights (committed) ★
│   │   ├── ols_baseline.pkl
│   │   ├── ols_wildfire.pkl
│   │   ├── nn_baseline.joblib
│   │   ├── nn_wildfire.joblib
│   │   ├── lstm_baseline.pt
│   │   ├── lstm_wildfire.pt
│   │   ├── lstm_metadata.json     ← feature columns + architecture notes
│   │   └── model_registry.json
│   ├── Q1_models/                 ← CS1 pretrained weights (committed)
│   │   ├── ols_pipe.joblib
│   │   ├── elasticnet_best.joblib
│   │   ├── xgb_best.joblib
│   │   └── mlp_best.joblib
│   ├── CS2Q1&3 Analysis.qmd      ← CS2-RQ1 & RQ3 Bayesian analysis (R/brms) ★
│   ├── Model Fitting to question 2.ipynb  ← CS1-RQ2 mixed-effects modelling
│   ├── Q1.ipynb
│   └── README.md
│
├── outputs/
│   └── figures/
│
├── report/
│   ├── FinalSlides.pdf            ← rendered presentation (committed)
│   ├── Group3PresentationSlides.pdf
│   ├── PresentationSlides.qmd
│   ├── final_report_with_code_included.qmd
│   ├── final_report_without_code.qmd
│   └── ...
│
├── scripts/
│   ├── download_cwfis_hotspots.py ← Step 1: download CWFIS data
│   ├── clean_cwfis_hotspots.py    ← Step 2: clean hotspots
│   ├── build_wsei_features.py     ← Step 3: compute WSEI + merge
│   ├── Q1_script.py               ← CS1 modelling (used by CI)
│   ├── run.sh                     ← CI entry point
│   └── README.md                  ← detailed script documentation
│
└── support/
    ├── Case Study Overview - STAT 946 - Winter 2026.pdf
    └── STAT946 Case2 Assignment5 Proposal - Group 3.pdf
```

---

## Data Sources

### Case Study 1

| # | Dataset | File | Notes |
|---|---------|------|-------|
| 1 | Ontario Air Quality (2022–2024) | `AirQuality_ON_2022_2024.csv` | Hourly station-level pollutants |
| 2 | EPA AQI Reference | `Hourly_AQI_EPA.xlsb` | AQI standardisation |
| 3 | Ontario Traffic (2022–2024) | `traffic_ON_2022_2024.csv` | Camera-based volume counts |
| 4 | Ontario Weather (2022–2024) | `weather_ON_2022_2024.csv` | Temp, wind, precipitation |
| 5 | Spatially Merged Dataset | `merged_10km_daily_updated.csv` | AQI + weather + traffic within 10 km |

### Case Study 2

| # | Dataset | File | Notes |
|---|---------|------|-------|
| 6 | CWFIS Wildfire Hotspots (2022–2024) | `data/wildfire/hotspots_clean.csv.gz` | 4.94 M hotspots; **not committed** |
| 7 | WSEI Features | `data/wildfire/wsei_features.csv` | Per station × day; **not committed** |
| 8 | CS2 Modelling Dataset | `data/wildfire/merged_with_wsei.csv` | Full input for CS2-RQ1/2/3; **not committed** |

> **Wildfire data is not committed to GitHub** (files are 300–400 MB). Reproduce locally by running the three scripts in `scripts/` — see [Case Study 2 Data Pipeline](#case-study-2-data-pipeline) below.

See `data/data_dictionary.md` for column-level documentation and WSEI formula derivation.

---

## Processing Pipeline

### Case Study 1

| Step | Notebook | Output |
|------|----------|--------|
| 1 – AQI processing | `analysis/AQProcess.ipynb` | Cleaned, standardised AQI |
| 2 – Weather & traffic | `analysis/WX_TRProcess.ipynb` | Aggregated weather + traffic features |
| 3 – Spatial merge | `analysis/Merge.ipynb` | `merged_10km_daily_updated.csv` |
| 4 – CS1-RQ1 modelling | `analysis/Q1.ipynb` | OLS / ElasticNet / XGBoost / MLP |
| 5 – CS1-RQ2 modelling | `model/Model Fitting to question 2.ipynb` | Mixed-effects + GAM |

### Case Study 2 Data Pipeline

Run these three scripts **in order** to build the wildfire dataset from scratch:

```bash
python scripts/download_cwfis_hotspots.py   # ~20 min, downloads 400 MB
python scripts/clean_cwfis_hotspots.py      # ~2 min
python scripts/build_wsei_features.py       # ~5–15 min (CPU-bound)
```

See `scripts/README.md` for detailed descriptions and expected outputs.

### Case Study 2 Modelling

| Step | File | Language | Notes |
|------|------|----------|-------|
| CS2-RQ2 forecast models | `analysis/CS2Q2.ipynb` | Python | OLS / NN / LSTM; outputs committed |
| CS2-RQ1 & RQ3 Bayesian | `model/CS2Q1&3 Analysis.qmd` | R (brms) | Requires `merged_with_wsei.csv`; see below |

---

## Pretrained Models

### Case Study 2 — `model/CS2RQ2_models/`

All six RQ2 model weights are committed to the repository. `lstm_metadata.json` records the feature columns and architecture details needed to reconstruct and load the LSTM weights.

| File | Description |
|------|-------------|
| `ols_baseline.pkl` | OLS without wildfire features |
| `ols_wildfire.pkl` | OLS with WSEI features |
| `nn_baseline.joblib` | MLP without wildfire features |
| `nn_wildfire.joblib` | MLP with WSEI features |
| `lstm_baseline.pt` | LSTM without wildfire features |
| `lstm_wildfire.pt` | LSTM with WSEI features |

### Case Study 1 — `model/Q1_models/`

| File | Description |
|------|-------------|
| `ols_pipe.joblib` | Linear baseline |
| `elasticnet_best.joblib` | Regularised linear model |
| `xgb_best.joblib` | Gradient boosting |
| `mlp_best.joblib` | Neural network |

---

## Reports

| File | Description |
|------|-------------|
| `report/FinalSlides.pdf` | Final group presentation (committed) |
| `report/PresentationSlides.qmd` | Quarto source for the slides |
| `report/final_report_without_code.qmd` | Main report (rendered by CI pipeline) |
| `report/final_report_with_code_included.qmd` | Report with full code listings |
| `model/CS2Q1&3 Analysis.qmd` | CS2-RQ1 & RQ3 Bayesian analysis source |

---

## CI/CD Pipeline

The automated pipeline is defined in `.github/workflows/pipeline.yml`.

It is triggered on every push to `main` and can also be run manually via **workflow_dispatch** (Actions tab → "Analysis Pipeline (uv + Quarto)" → Run workflow).

**What the CI pipeline does:**
1. Installs Python dependencies via `uv sync --frozen`
2. Runs `scripts/Q1_script.py` (CS1-RQ1: generates tables and figures)
3. Executes `model/Model Fitting to question 2.ipynb` (CS1-RQ2: generates figures)
4. Renders `report/final_report_without_code.qmd` via Quarto → PDF
5. Uploads the PDF as a downloadable Actions artifact

Estimated runtime: **~3 minutes**

> **CS2 analyses are not run in CI** — the wildfire data pipeline requires downloading ~400 MB of external data, and the LSTM training is resource-intensive. See the reproducibility section below.

---

## Reproducibility

### Case Study 1
Fully reproducible via the CI pipeline. Pretrained model weights are committed; the pipeline loads them for evaluation without re-running hyperparameter tuning.

### Case Study 2

The CS2 analyses cannot run in CI due to data size and compute requirements. Reproducibility is demonstrated as follows:

| Component | Evidence in repo | How to reproduce locally |
|-----------|-----------------|--------------------------|
| Wildfire data pipeline | `scripts/` with documented steps | Run the 3 scripts above in order |
| CS2-RQ2 models (OLS/NN/LSTM) | Trained weights committed in `model/CS2RQ2_models/` | Run `analysis/CS2Q2.ipynb` end-to-end |
| CS2-RQ2 results | Cell outputs committed in `analysis/CS2Q2.ipynb` | Viewable directly on GitHub |
| CS2-RQ1 & RQ3 (Bayesian) | Analysis in `model/CS2Q1&3 Analysis.qmd`; results summarised in `report/FinalSlides.pdf` | Run QMD locally with R + brms (seed = 946) |

**To reproduce CS2-RQ2 locally:**
```bash
# 1. Build the wildfire dataset (see above)
# 2. Open and run the notebook
jupyter notebook analysis/CS2Q2.ipynb
```

**To reproduce CS2-RQ1 and CS2-RQ3 locally (requires R):**
```r
# Install required packages
install.packages(c("tidyverse", "brms", "bayesplot", "posterior", "tidybayes", "mgcv", "janitor"))

# Ensure data/wildfire/merged_with_wsei.csv exists (run the 3 data scripts above), then render:
quarto render "model/CS2Q1&3 Analysis.qmd"
# MCMC chains: 4 × 2,000 iterations, seed = 946
# Runtime: ~5–15 minutes
```

---

## How to Run the CI Pipeline (Case Study 1)

1. Go to the **Actions** tab at the top of the repository.
2. In the left-hand sidebar, click **"Analysis Pipeline (uv + Quarto)"**.
3. Click **"Run workflow"** → **"Run workflow"** (green button).
4. The full pipeline executes (~3 minutes) and uploads the rendered report as a ZIP artifact.

---

## Intended Audience

This repository is designed for academic evaluation, reproducible analytics demonstration, and public-sector environmental analytics. It supports evidence-based insights for Ontario municipal environmental offices and the Ministry of the Environment.
