import ee
import pandas as pd
import numpy as np


def init_gee():
    import json, os, tempfile

    key_dict = None

    # 1. Try Streamlit secrets (only when running on Streamlit Cloud)
    try:
        import streamlit as st
        if "gee_key" in st.secrets:
            key_dict = dict(st.secrets["gee_key"])
    except Exception:
        pass

    # 2. Fall back to gee-key.json sitting next to this file
    if key_dict is None:
        key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gee-key.json")
        if not os.path.exists(key_path):
            raise FileNotFoundError(
                f"gee-key.json not found at {key_path}. "
                "Place the service-account key file next to gee_utils.py."
            )
        with open(key_path) as f:
            key_dict = json.load(f)

    project_id = key_dict["project_id"]
    service_account_email = key_dict["client_email"]

    # Write to a temp file so the EE SDK can read it
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        json.dump(key_dict, tmp)
        tmp_path = tmp.name

    credentials = ee.ServiceAccountCredentials(service_account_email, tmp_path)
    ee.Initialize(credentials, project=project_id)


def _cloud_mask_landsat(image):
    qa = image.select("QA_PIXEL")
    cloud = qa.bitwiseAnd(1 << 3).eq(0)
    shadow = qa.bitwiseAnd(1 << 4).eq(0)
    return image.updateMask(cloud.And(shadow))


def _apply_scale(image):
    optical = image.select("SR_B.").multiply(0.0000275).add(-0.2)
    thermal = image.select("ST_B.*").multiply(0.00341802).add(149.0)
    return image.addBands(optical, None, True).addBands(thermal, None, True)


def fetch_city_heat_data(region, start_date, end_date, city_name, n_samples=1000):
    # Dynamic check: Start with clean scenes, but loosen if empty
    col = (
        ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        .filterDate(start_date, end_date)
        .filterBounds(region)
    )

    # Fallback if strict cloud filtering returns an empty collection
    clean_col = col.filter(ee.Filter.lt("CLOUD_COVER", 40)).map(_cloud_mask_landsat)
    
    if int(clean_col.size().getInfo()) > 0:
        col = clean_col
    else:
        # If no clear images are found, accept higher cloud threshold so the app doesn't break
        col = col.filter(ee.Filter.lt("CLOUD_COVER", 80)).map(_cloud_mask_landsat)

    col = col.map(_apply_scale)
    img = col.median().clip(region)

    lst = img.select("ST_B10").subtract(273.15).rename("lst_c")
    ndvi = img.normalizedDifference(["SR_B5", "SR_B4"]).rename("ndvi")
    built = img.normalizedDifference(["SR_B6", "SR_B5"]).rename("built_index")

    stack = ee.Image.cat([lst, ndvi, built]).clip(region)

    samples = stack.sample(
        region=region,
        scale=30,
        numPixels=n_samples,
        geometries=True
    )

    features = samples.getInfo()["features"]
    rows = []
    for f in features:
        p = f["properties"]
        coords = f["geometry"]["coordinates"]
        
        # CRITICAL RENDERING FIX: 
        # Plotly WebGL mapbox engines break and go blank if None/NaN values exist in arrays.
        if p.get("lst_c") is None or p.get("ndvi") is None or p.get("built_index") is None:
            continue

        rows.append({
            "city": city_name,
            "lon": float(coords[0]),
            "lat": float(coords[1]),
            "lst_c": float(p.get("lst_c")),
            "ndvi": float(p.get("ndvi")),
            "built_index": float(p.get("built_index")),
        })

    return pd.DataFrame(rows)