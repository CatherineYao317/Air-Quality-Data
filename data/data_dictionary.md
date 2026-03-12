# Data Dictionary

This directory contains all datasets used in the STAT 946 Case Study 1 and 2 analyses.

> **Note on wildfire data:** All files under `data/wildfire/` are **gitignored** (the raw/clean hotspot files are 300–400 MB; wsei_features.csv and merged_with_wsei.csv, while smaller, are also gitignored as they are derived outputs).
> Reproduce them locally by running the pipeline in order:
> ```bash
> python scripts/download_cwfis_hotspots.py
> python scripts/clean_cwfis_hotspots.py
> python scripts/build_wsei_features.py
> ```

---

## Core Datasets

### `merged_10km_daily_updated.csv`
**33,535 rows × 22 columns | 3.6 MB**

The primary station-day modeling dataset for Case Study 1. Each row is one AQI
monitoring station on one calendar day. Weather and traffic observations are
spatially matched from sources within a 10 km radius of each AQI station.

| Column | Type | Description |
|--------|------|-------------|
| `Date` | date | Calendar date (YYYY-MM-DD) |
| `Station ID` | int | MECP AQI station identifier |
| `Latitude` | float | Station latitude, WGS84 |
| `Longitude` | float | Station longitude, WGS84 |
| `CO_subAQI` | float | Carbon monoxide sub-index |
| `NO2_subAQI` | float | Nitrogen dioxide sub-index |
| `O3_subAQI` | float | Ozone sub-index |
| `PM2.5_subAQI` | float | Fine particulate matter sub-index |
| `SO2_subAQI` | float | Sulphur dioxide sub-index |
| `AQI` | float | Daily AQI — max of the five sub-indices; **prediction target** |
| `MeanTemp` | float | Mean daily temperature (°C), averaged from matched weather stations |
| `TotalPrecip` | float | Total precipitation (mm) |
| `MaxTemp` | float | Maximum daily temperature (°C) |
| `MinTemp` | float | Minimum daily temperature (°C) |
| `TotalRain` | float | Total rainfall (mm); NaN when no rain or no match |
| `SnowOnGround` | float | Snow on ground depth (cm); NaN outside winter or no match |
| `MaxGustSpd` | float | Speed of maximum wind gust (km/h) |
| `wx_n` | float | Number of ECCC weather stations matched within 10 km |
| `TempRange` | float | Computed: MaxTemp − MinTemp (°C) |
| `TotalTraffic` | float | Total traffic volume from cameras within 10 km |
| `tr_n` | float | Number of traffic cameras matched within 10 km |

**Known limitation:** Wind *direction* is absent. It is added by
`scripts/build_wsei_features.py` when constructing the Case Study 2 dataset.

---

### `weather_ON_2022_2024.csv`
**138,061 rows × 39 columns | 16 MB**

Raw daily weather observations from Environment and Climate Change Canada (ECCC)
for Ontario stations, 2022–2024. Used as the source for matching meteorological
variables onto AQI stations in `merged_10km_daily_updated.csv` and for extracting
wind direction for WSEI computation.

Key columns relevant to Case Study 2:

| Column | Description |
|--------|-------------|
| `Station ID` | ECCC climate station identifier |
| `Latitude (y)` | Station latitude |
| `Longitude (x)` | Station longitude |
| `Date/Time` | Observation date |
| `Dir of Max Gust (10s deg)` | Direction of maximum wind gust in **tens of degrees** (ECCC convention: 1 = 10°, 36 = 360° = North, 0 = calm / missing). Multiply by 10 for actual degrees. |
| `Spd of Max Gust (km/h)` | Speed of maximum wind gust (km/h) |

---

### `AirQuality_ON_2022_2024.csv`
**33,536 rows × 10 columns | 2.0 MB**

Processed daily AQI and sub-AQI values per station. Source input for the merged
dataset. Contains: `Date`, `Station ID`, `Latitude`, `Longitude`, and the five
sub-AQI columns plus `AQI`.

---

### `traffic_ON_2022_2024.csv`
**3,610 rows × ~1,000+ columns | 12 MB**

Wide-format traffic camera data. Rows are camera locations; columns are daily
traffic counts (column names: `x2022_04_26`, `x2022_04_27`, …). Metadata columns
include `longitude`, `latitude`, and `traffic_source`. Pivoted and spatially
matched to AQI stations when building the merged dataset.

---

## Case Study 2 Wildfire Datasets (`data/wildfire/`)

All files in this folder are gitignored. Reproduce via the scripts listed above.

---

### `hotspots_clean.csv.gz`
**4,940,484 rows × 34 columns | ~313 MB (compressed)**

Analysis-ready CWFIS Fire M3 Daily Hotspot data for Canada, 2022–2024. Produced
by `scripts/clean_cwfis_hotspots.py`. See `scripts/README.md` for full cleaning
documentation.

Key columns:

| Column | Description |
|--------|-------------|
| `date` | Calendar day (UTC, no timezone) |
| `lat`, `lon` | Hotspot location (WGS84) |
| `hfi` | Head Fire Intensity (kW/m) — primary intensity proxy; log(1+hfi) used in WSEI |
| `frp` | Fire Radiative Power (MW) — alternative intensity proxy |
| `tfc` | Total Fuel Consumption (kg/m²) — alternative intensity proxy |
| `ws`, `wd` | Wind speed (km/h) and direction (°) at hotspot location |
| `ffmc`–`fwi` | Canadian Forest Fire Weather Index components |
| `agency` | Provincial fire agency (e.g. ON, BC, AB) |

---

### `wsei_features.csv`
**33,535 rows × 16+ columns | ~few MB (compressed)**

Intermediate WSEI feature cache. Produced by `scripts/build_wsei_features.py`.
One row per (AQI station, calendar date). Load this to skip the expensive spatial
computation when iterating on modeling.

| Column | Description |
|--------|-------------|
| `Station ID` | AQI station identifier |
| `Date` | Calendar date |
| `wind_dir_deg` | Circular-mean wind direction (°, FROM direction, met. convention); NaN if no match |
| `wind_spd_kmh` | Mean wind gust speed (km/h) from matched ECCC stations |
| `wsei_hfi_k0` – `wsei_hfi_k3` | WSEI using log(1+hfi) intensity at lag 0–3 days |
| `wsei_frp_k0` – `wsei_frp_k3` | WSEI using log(1+frp) intensity — sensitivity check |
| `wsei_tfc_k0` – `wsei_tfc_k3` | WSEI using log(1+tfc) intensity — sensitivity check |
| `wsei_hfi_max3d` | max(wsei_hfi_k0 … k3) — peak single-day exposure in 3-day window |
| `wsei_hfi_sum3d` | sum(wsei_hfi_k0 … k3) — cumulative 3-day smoke exposure |

---

### `merged_with_wsei.csv`
**33,535 rows | ~few MB (compressed)**

**The primary Case Study 2 modeling input.** Contains all columns from
`merged_10km_daily_updated.csv` plus `wind_dir_deg` and all WSEI columns from
`wsei_features.csv`. Load this directly in modeling notebooks.

---

## WSEI Formula and Design Decisions

The Wildfire Smoke Exposure Index aggregates hotspot-level fire activity into a
station-day covariate that accounts for distance decay, wind transport, and
multi-day persistence:

```
WSEI(s, t, k) = Σ_f  log(1 + I_f) × K(d(s,f)) × W(Δθ_{s,f}, v_{s,t-k})
```

where `f` indexes hotspots on day `t − k`, and `k = 0, 1, 2, 3`.

---

### Distance Kernel: Cauchy — `K(d) = 1 / (1 + (d / 500 km)²)`

| Property | Value |
|----------|-------|
| At d = 0 km | K = 1.0 |
| At d = 500 km | K = 0.5 |
| At d = 1,000 km | K = 0.2 |
| At d = 2,000 km | K = 0.05 (hard cutoff applied here) |

**Pros:**
- Smooth, continuous — no artificial discontinuity at any distance
- Well-behaved at d = 0 (unlike pure inverse-distance which diverges)
- One interpretable parameter: d₀ = half-weight distance (500 km)
- Power-law tail allows occasional long-range smoke plumes to contribute

**Cons:**
- d₀ = 500 km is a modelling assumption; run sensitivity at 250 km and 1,000 km
- Never reaches exactly zero (residual contribution from very distant fires;
  mitigated by the 2,000 km hard cutoff)
- Heavier tail than Gaussian — may over-weight large but distant fire complexes

**Alternatives considered:**
- Gaussian `exp(−d²/2σ²)`: faster dropoff, but needs two tuning decisions (σ
  and a separate hard cutoff)
- Exponential `exp(−d/λ)`: lighter tail than Cauchy, similar to atmospheric
  dispersion but less evidence for this specific choice

---

### Wind Alignment: `W(Δθ, v) = v × max(0, cos(Δθ))`

Δθ = (bearing from station to hotspot) − (station wind-from direction)

The hotspot is **upwind** of the station when Δθ ≈ 0° (wind blows directly from
hotspot toward station). The cosine weighting gives full weight at 0°, half-weight
at 60°, and zero weight at ±90° (perpendicular or headwind directions).

| Scenario | Δθ | cos(Δθ) | Interpretation |
|----------|----|---------|----------------|
| Hotspot directly upwind | 0° | 1.0 | Full weight |
| 45° off-axis | 45° | 0.71 | Reduced weight |
| Perpendicular | 90° | 0.0 | No contribution |
| Downwind of station | 180° | −1.0 → clamped 0 | No contribution |

Scales linearly with wind speed `v` (km/h): stronger wind → more efficient transport.

**Special cases:**
- `wind_dir_deg = NaN` or 0 (calm): directional alignment set to 0.5 (neutral)
- `wind_spd_kmh = NaN`: replaced with 1.0 (no speed scaling)

**Pros:**
- Physically intuitive and easy to explain to stakeholders
- Zero contribution from headwind or crosswind hotspots — reduces noise
- No additional bandwidth parameters

**Cons:**
- Cosine function has a broad acceptance angle (±90°); Gaussian alignment would
  be more selective
- Uses station wind direction as a proxy for the transport path, which is a
  simplification (smoke transport is governed by the full wind field aloft)
- Single-day wind at the station — does not account for multi-day trajectory

**Alternative considered:** Gaussian alignment `exp(−Δθ²/2σ_θ²)` with σ_θ ≈ 30°
gives sharper directional focus but adds a tuning parameter.

---

### Lag Structure: k = 0, 1, 2, 3 days

Smoke from distant fires takes time to reach monitoring stations. Lags up to 3
days capture both same-day local fires and transported smoke from regional events.
Beyond 3 days, fire activity correlation with local AQI diminishes substantially.

---

### Distance Cutoff: 2,000 km

Hotspots beyond 2,000 km contribute K < 0.05 under the Cauchy kernel. Applying
this hard cutoff reduces per-iteration computation by > 80% with negligible loss
of signal. North American wildfire smoke plumes that travel > 2,000 km are rare
and typically diluted below AQI-measurable thresholds.
