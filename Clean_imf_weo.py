#!/usr/bin/env python3
# Clean WEO dataset into (Country, Indicator, Year, Value)
# Usage: python clean_weo.py --in dataset_WEO.csv --out IMF_clean.csv

import argparse
import pandas as pd
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", default="dataset_WEO.csv", help="Path to raw WEO CSV")
    ap.add_argument("--out", dest="outfile", default="IMF_clean.csv", help="Path to write cleaned CSV")
    args = ap.parse_args()

    df = pd.read_csv(args.infile, low_memory=False)

    # Keep only these countries and indicators; map to target indicator names
    countries = ["Canada", "Mexico", "United States"]
    indicator_map = {
        "Gross domestic product (GDP), Constant prices, Percent change": "GDP (constant prices, % change)",
        "All Items, Consumer price index (CPI), Period average, percent change": "CPI inflation (% change)",
    }

    # Detect year columns like "1980" ... "2030"
    year_cols = [c for c in df.columns if c.isdigit() and len(c) == 4]

    sub = df[df["COUNTRY"].isin(countries) & df["INDICATOR"].isin(indicator_map.keys())].copy()
    sub["Country"] = sub["COUNTRY"]
    sub["Indicator"] = sub["INDICATOR"].map(indicator_map)

    long_df = sub.melt(
        id_vars=["Country", "Indicator"],
        value_vars=year_cols,
        var_name="Year",
        value_name="Value",
    )

    long_df = long_df.dropna(subset=["Value"]).copy()
    long_df["Year"] = long_df["Year"].astype(int)

    # Keep 1980..2030 if present
    if year_cols:
        years = sorted(int(y) for y in year_cols)
        yr_min, yr_max = max(1980, years[0]), min(2030, years[-1])
        long_df = long_df[(long_df["Year"] >= yr_min) & (long_df["Year"] <= yr_max)]

    long_df = long_df[["Country", "Indicator", "Year", "Value"]].sort_values(
        ["Country", "Indicator", "Year"]
    )

    Path(args.outfile).parent.mkdir(parents=True, exist_ok=True)
    long_df.to_csv(args.outfile, index=False)

if __name__ == "__main__":
    main()
