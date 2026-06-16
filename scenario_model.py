import pandas as pd

def run_scenarios(metrics):
    df = metrics["dataframe"].copy()
    base = metrics["baseline_lst_c"]
    h = metrics["hotspot_threshold_c"]

    scenarios = [
        ("Tree plantation", 0.12, 0.00, 0.00),
        ("Green roofs", 0.04, 0.18, 0.00),
        ("Cool roofs", 0.00, 0.00, 0.10),
        ("Combined", 0.10, 0.12, 0.08),
    ]

    rows = []
    for name, tree_delta, green_roof_delta, albedo_delta in scenarios:
        cooling_c = (5.0 * tree_delta) + (3.0 * green_roof_delta) + (2.5 * albedo_delta)
        new_mean = base - cooling_c
        reduction_pct = 100.0 * cooling_c / base
        hotspot_reduction_pct = max(0.0, 100.0 * ((df["lst_c"] >= h).mean() - ((df["lst_c"] - cooling_c) >= h).mean()))

        rows.append({
            "Scenario": name,
            "Cooling reduction (°C)": round(cooling_c, 2),
            "Cooling reduction (%)": round(reduction_pct, 2),
            "Hotspot reduction (%)": round(hotspot_reduction_pct, 2),
            "Estimated mean LST after scenario (°C)": round(new_mean, 2),
        })

    return pd.DataFrame(rows)