import pandas as pd
import numpy as np

def build_heat_metrics(df):
    if df.empty:
        return {
            "baseline_lst_c": 0.0,
            "hotspot_share_pct": 0.0,
            "mean_ndvi": 0.0,
            "mean_built_index": 0.0,
            "hotspot_threshold_c": 0.0,
            "dataframe": df,
        }

    df = df.dropna().copy()
    baseline_lst = float(df["lst_c"].mean())
    hotspot_threshold = float(df["lst_c"].quantile(0.85))
    hotspot_share = float((df["lst_c"] >= hotspot_threshold).mean() * 100)

    return {
        "baseline_lst_c": baseline_lst,
        "hotspot_share_pct": hotspot_share,
        "mean_ndvi": float(df["ndvi"].mean()),
        "mean_built_index": float(df["built_index"].mean()),
        "hotspot_threshold_c": hotspot_threshold,
        "dataframe": df,
    }