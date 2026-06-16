import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Fake data mimicking what GEE returns for Mumbai
np.random.seed(42)
n = 200
df = pd.DataFrame({
    "lat": np.random.uniform(18.85, 19.15, n),
    "lon": np.random.uniform(72.75, 73.05, n),
    "lst_c": np.random.uniform(28.0, 48.0, n),
})

center_lat = float(df["lat"].mean())
center_lon = float(df["lon"].mean())
zmin_val = float(df["lst_c"].min())
zmax_val = float(df["lst_c"].max())

fig = go.Figure(go.Densitymap(
    lat=df["lat"],
    lon=df["lon"],
    z=df["lst_c"],
    radius=15,
    colorscale="YlOrRd",
    zmin=zmin_val,
    zmax=zmax_val,
    opacity=0.8,
))

fig.update_layout(
    map_style="open-street-map",
    map_center={"lat": center_lat, "lon": center_lon},
    map_zoom=10,
    margin=dict(l=0, r=0, t=0, b=0),
)

fig.write_html("test_map.html")
print("Written test_map.html — open it in your browser")
