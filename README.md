# Urban Heat Mitigation Simulator

## Setup
1. Install dependencies:
   pip install -r requirements.txt

2. Configure Streamlit secrets:
   .streamlit/secrets.toml

3. Run:
   streamlit run app.py

## Notes
- Uses Google Earth Engine Landsat 8 Collection 2 Level 2.
- User enters city name and the app fetches data for that city.
- Outputs baseline heat, hotspots, and scenario cooling estimates.