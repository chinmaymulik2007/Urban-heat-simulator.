import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px

from gee_utils import init_gee, fetch_city_heat_data
from city_utils import geocode_city, city_buffer_geometry
from heat_model import build_heat_metrics
from scenario_model import run_scenarios
from viz_utils import make_city_map, make_results_chart

st.set_page_config(page_title="Urban Heat Mitigation Simulator", layout="wide")

st.title("Urban Heat Mitigation Simulator")
st.write("Enter a city name to fetch Earth Engine data and estimate cooling from interventions.")

city_name = st.text_input("City name", value="Mumbai")
buffer_km = st.slider("Analysis radius around city center (km)", 2, 50, 10)
start_date = st.date_input("Start date", value=pd.to_datetime("2025-04-01"))
end_date = st.date_input("End date", value=pd.to_datetime("2025-06-30"))

run_btn = st.button("Run simulation", type="primary")

if run_btn:
    try:
        init_gee()
        city = geocode_city(city_name)
        if city is None:
            st.error("City not found.")
            st.stop()

        region = city_buffer_geometry(city["lat"], city["lon"], buffer_km * 1000)
        st.success(f"Loaded {city['display_name']}")

        with st.spinner("Fetching Earth Engine data..."):
            raw_df = fetch_city_heat_data(region, str(start_date), str(end_date), city_name)

        metrics = build_heat_metrics(raw_df)
        scenario_df = run_scenarios(metrics)

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Baseline heat")
            st.metric("Average LST", f"{metrics['baseline_lst_c']:.2f} °C")
            st.metric("Hotspot share", f"{metrics['hotspot_share_pct']:.2f} %")
            st.metric("City area mean NDVI", f"{metrics['mean_ndvi']:.2f}")

        with col2:
            st.subheader("Map view")
            if raw_df.empty:
                st.error("No valid surface temperature data found for this city and date range.")
            else:
                folium_map = make_city_map(raw_df)
                if folium_map is not None:
                    # get_root().render() produces full standalone HTML (same as .save())
                    # unlike _repr_html_() which is a Jupyter fragment that Streamlit sandboxes
                    map_html = folium_map.get_root().render()
                    components.html(map_html, height=480, scrolling=False)

        st.subheader("Scenario results")
        st.dataframe(scenario_df, use_container_width=True, hide_index=True)

        st.subheader("Cooling impact")
        fig_bar = make_results_chart(scenario_df)
        st.plotly_chart(fig_bar, use_container_width=True)

        best = scenario_df.sort_values("Cooling reduction (%)", ascending=False).iloc[0]
        st.success(
            f"Best scenario: {best['Scenario']} | "
            f"Cooling: {best['Cooling reduction (°C)']:.2f} °C | "
            f"Reduction: {best['Cooling reduction (%)']:.2f} %"
        )

    except Exception as e:
        st.error(f"Failed: {e}")