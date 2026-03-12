# Analysis Folder

This folder contains the core data processing, modelling, and validation workflows for both Case Studies. Case Study 1 covers traffic-AQI forecasting and temporal pattern analysis; Case Study 2 covers wildfire-aware next-day AQI forecasting.


## File Overview

### 00_smoke_test.py
Lightweight validation script used for CI.  
Ensures the environment, dependencies, and key pipelines execute successfully.  
Supports reproducibility via automated checks (uv + Quarto pipeline).

### CS2Q2.ipynb
Case Study 2 — RQ2 forecasting analysis:
- Loads `data/wildfire/merged_with_wsei.csv` (produced by `scripts/build_wsei_features.py`)
- Chronological 80/20 train/test split with IterativeImputer (fitted on train only)
- Trains and evaluates three model families (OLS, NN, LSTM) in baseline vs. +wildfire configurations
- Reports overall and top-decile (extreme AQI days) RMSE/MAE
- Saves trained weights to `model/CS2RQ2_models/`

Cell outputs are committed — viewable directly on GitHub without re-running.

### AQProcess.ipynb
Air quality data preprocessing:
- Data cleaning and filtering  
- Missingness assessment  
- Feature engineering  
- Station-level consistency checks  

Forms the foundation for both Q1 and Q2 modelling.

### WX_TRProcess.ipynb
Weather and traffic preprocessing:
- Temporal alignment of meteorology and traffic volume  
- Lag feature construction (e.g., previous-day predictors)  
- Quality checks and imputation  

Outputs structured inputs for forecasting models.

### Merge.ipynb
Data integration workflow:
- Merges air quality, weather, and traffic datasets  
- Ensures time-index alignment  
- Produces modelling-ready datasets  

Acts as the bridge between preprocessing and modelling.


### Q1.ipynb
AQI data specific to research question 1 forecasting analysis:
- Time-based train/test split  
- Model training (OLS, ElasticNet, XGBoost, MLP)  
- Hyperparameter tuning with TimeSeries CV  
- Out-of-sample performance evaluation (RMSE, MAE)  

Supports model comparison and production candidate selection.

## Purpose

This folder contains the full analytical pipeline from raw data processing to model-ready datasets and forecasting evaluation. It is designed to be reproducible, modular, and CI-compatible to support production-grade analytics for public-sector decision-making.

