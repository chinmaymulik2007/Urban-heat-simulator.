import streamlit as st
import streamlit.components.v1 as components
import folium
from folium.plugins import HeatMap
import numpy as np
import pandas as pd

st.title("Map debug test")

np.random.seed(42)
n = 200
df = pd.DataFrame({
    "lat": np.random.uniform(18.85, 19.15, n),
    "lon": np.random.uniform(72.75, 73.05, n),
    "intensity": np.random.uniform(0, 1, n),
})

m = folium.Map(location=[19.0, 72.9], zoom_start=11, tiles="CartoDB positron")
HeatMap(df[["lat","lon","intensity"]].values.tolist(), radius=18, blur=15).add_to(m)

st.write("### Test 1: get_root().render()")
components.html(m.get_root().render(), height=400, scrolling=False)

st.write("### Test 2: _repr_html_()")
components.html(m._repr_html_(), height=400, scrolling=False)
