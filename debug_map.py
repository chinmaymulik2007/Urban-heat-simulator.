import folium
from folium.plugins import HeatMap
import pandas as pd
import numpy as np

# Fake Mumbai data
np.random.seed(42)
n = 200
df = pd.DataFrame({
    "lat": np.random.uniform(18.85, 19.15, n),
    "lon": np.random.uniform(72.75, 73.05, n),
    "lst_c": np.random.uniform(28.0, 48.0, n),
})

df["intensity"] = (df["lst_c"] - df["lst_c"].min()) / (df["lst_c"].max() - df["lst_c"].min())

m = folium.Map(location=[19.0, 72.9], zoom_start=11, tiles="CartoDB positron")
HeatMap(df[["lat","lon","intensity"]].values.tolist(), radius=18, blur=15).add_to(m)
m.save("debug_map.html")
print("Saved debug_map.html — open it in your browser")
