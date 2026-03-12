"""
Clean the raw CWFIS Fire M3 hotspot data (Canada, 2022-2024).

Input:  data/wildfire/hotspots_2022_2024_canada.csv.gz
Output: data/wildfire/hotspots_clean.csv.gz

Cleaning steps
--------------
1. Parse rep_date -> proper UTC datetime; derive date (day only).
2. Drop rows with null lat, lon, or date (cannot be spatially/temporally joined).
3. Drop rows with hfi null (only 1,423; these have no intensity information).
4. Flag and drop impossible temperature outlier (temp > 100°C is physically impossible).
5. Drop cbh column (74% missing, not useful for our analysis).
6. Drop redundant columns (country already filtered; source_year derivable from date).
7. Cast columns to efficient dtypes.
8. Report a data quality summary.
"""

import pandas as pd
import numpy as np
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
IN_PATH  = REPO_ROOT / "data" / "wildfire" / "hotspots_2022_2024_canada.csv.gz"
OUT_PATH = REPO_ROOT / "data" / "wildfire" / "hotspots_clean.csv.gz"

# ── Columns to drop outright ───────────────────────────────────────────────────
# cbh: 74% null
# country: already filtered to Canada ("C")
# source_year: derivable from date
DROP_COLS = ["cbh", "country", "source_year"]

def report(label, df):
    """Print a short progress banner showing the current row count.

    Args:
        label (str): Description of the current pipeline stage.
        df (pd.DataFrame): DataFrame after the most recent cleaning step.
    """
    print(f"\n{'─'*60}")
    print(f"  {label}")
    print(f"  Rows: {len(df):,}")


def main():
    """Run the full CWFIS hotspot cleaning pipeline and save the result.

    Reads ``hotspots_2022_2024_canada.csv.gz``, applies all cleaning steps
    documented in the module docstring, and writes the analysis-ready file to
    ``hotspots_clean.csv.gz``. Prints a data-quality summary on completion.
    """
    print(f"Reading {IN_PATH} ...")
    df = pd.read_csv(IN_PATH, low_memory=False)
    report("Raw input", df)

    # ── 1. Parse dates ─────────────────────────────────────────────────────────
    df["rep_date"] = pd.to_datetime(df["rep_date"], utc=True, errors="coerce")
    # date = calendar day in UTC (no timezone attached)
    df["date"] = df["rep_date"].dt.normalize().dt.tz_localize(None)

    # ── 2. Drop rows with null lat / lon / date ────────────────────────────────
    n_before = len(df)
    df = df.dropna(subset=["lat", "lon", "date"])
    n_dropped = n_before - len(df)
    print(f"\nDropped {n_dropped:,} rows with null lat/lon/date")
    report("After spatial/temporal drop", df)

    # ── 3. Drop rows with null hfi ─────────────────────────────────────────────
    n_before = len(df)
    df = df.dropna(subset=["hfi"])
    print(f"Dropped {n_before - len(df):,} rows with null hfi")
    report("After hfi null drop", df)

    # ── 4. Flag/drop impossible temperature values ─────────────────────────────
    # temp is in °C; physically impossible above ~60°C for surface air temp
    # The data showed a max of 261°C — clearly a sensor/model error
    BAD_TEMP_THRESH = 100  # °C
    bad_temp = df["temp"] > BAD_TEMP_THRESH
    print(f"\nRows with temp > {BAD_TEMP_THRESH}°C: {bad_temp.sum():,}  "
          f"(values: {df.loc[bad_temp, 'temp'].value_counts().head(5).to_dict()})")
    df = df[~bad_temp].copy()
    report("After bad-temperature drop", df)

    # ── 5. Note on hfi = 0 ─────────────────────────────────────────────────────
    # hfi == 0 means the fire behavior model computed zero intensity
    # (e.g., non-combustible fuel type, or fire just extinguished).
    # We KEEP these rows — they are valid observations of low-intensity hotspots.
    # Downstream models can decide how to treat zeros (e.g., via log(1 + hfi)).
    n_hfi_zero = (df["hfi"] == 0).sum()
    print(f"\nRows with hfi == 0 (kept, valid low-intensity): {n_hfi_zero:,} "
          f"({100 * n_hfi_zero / len(df):.1f}%)")

    # ── 6. Drop redundant / very-high-null columns ─────────────────────────────
    cols_to_drop = [c for c in DROP_COLS if c in df.columns]
    df = df.drop(columns=cols_to_drop)
    print(f"\nDropped columns: {cols_to_drop}")

    # ── 7. Cast to efficient dtypes ────────────────────────────────────────────
    float32_cols = [
        "lat", "lon", "hfi", "frp", "tfc", "ros", "sfc", "sfl", "cfl",
        "ws", "wd", "temp", "rh", "pcp",
        "ffmc", "dmc", "dc", "bui", "isi", "fwi",
        "elev", "slope", "aspect", "greenup", "pconif",
    ]
    for col in float32_cols:
        if col in df.columns:
            df[col] = df[col].astype("float32")

    int8_cols = ["pcuring"]
    for col in int8_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int8")

    cat_cols = ["satellite", "sensor", "source", "agency", "ecozone", "fuel"]
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype("category")

    # ── 8. Final quality summary ───────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("FINAL CLEAN DATASET SUMMARY")
    print(f"{'='*60}")
    print(f"Shape: {df.shape}")
    print(f"\nDate range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"\nRows by year:")
    print(df.groupby(df["date"].dt.year).size().rename("hotspots").to_string())
    print(f"\nRows by province (agency):")
    print(df["agency"].value_counts().to_string())
    print(f"\nNull counts (non-zero only):")
    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]
    if len(nulls):
        print(nulls.to_string())
    else:
        print("  None")
    print(f"\nKey column stats (hfi, frp, tfc):")
    print(df[["hfi", "frp", "tfc"]].describe().to_string())
    print(f"\nFinal columns ({len(df.columns)}):")
    print(list(df.columns))

    # ── Save ───────────────────────────────────────────────────────────────────
    print(f"\nSaving to {OUT_PATH} ...")
    df.to_csv(OUT_PATH, index=False, compression="gzip")
    print(f"Done. File size: {OUT_PATH.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
