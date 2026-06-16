import plotly.express as px
import numpy as np


def make_city_map(df):
    import folium
    from folium.plugins import HeatMap

    df = df.dropna(subset=["lat", "lon", "lst_c"])
    if df.empty:
        return None

    center_lat = float(df["lat"].mean())
    center_lon = float(df["lon"].mean())

    lst_min = df["lst_c"].min()
    lst_max = df["lst_c"].max()

    # Normalise lst_c to 0-1 for HeatMap intensity
    df = df.copy()
    if lst_max > lst_min:
        df["intensity"] = (df["lst_c"] - lst_min) / (lst_max - lst_min)
    else:
        df["intensity"] = 1.0

    m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles="CartoDB positron")

    heat_data = df[["lat", "lon", "intensity"]].values.tolist()

    HeatMap(
        heat_data,
        min_opacity=0.4,
        radius=18,
        blur=15,
        gradient={0.0: "blue", 0.4: "purple", 0.65: "orange", 1.0: "yellow"},
    ).add_to(m)

    # Add a title
    title_html = f"""
    <div style="position:fixed;top:10px;left:50%;transform:translateX(-50%);
                background:white;padding:6px 14px;border-radius:6px;
                font-size:14px;font-weight:bold;z-index:9999;
                box-shadow:0 2px 6px rgba(0,0,0,0.3)">
        Urban Heat Map — LST {lst_min:.1f}°C (cool) → {lst_max:.1f}°C (hot)
    </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))

    return m


def make_results_chart(df):
    fig = px.bar(
        df,
        x="Scenario",
        y="Cooling reduction (°C)",
        text="Cooling reduction (°C)",
        title="Estimated cooling by intervention",
        color="Cooling reduction (°C)",
        color_continuous_scale="Blues",
    )
    fig.update_traces(textposition="outside", texttemplate="%{text:.2f} °C")
    fig.update_layout(
        yaxis_title="Cooling reduction (°C)",
        uniformtext_minsize=8,
        coloraxis_showscale=False,
    )
    return fig