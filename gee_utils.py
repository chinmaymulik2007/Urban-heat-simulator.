import ee
import pandas as pd
import numpy as np

def _get_key_dict():
    import os, json

    # 1. Streamlit secrets
    try:
        import streamlit as st
        if "gee_key" in st.secrets:
            raw = dict(st.secrets["gee_key"])
            
            # Reconstruct the private key string directly from the clean array lines
            if "private_key_lines" in raw:
                raw["private_key"] = "\n".join(raw["private_key_lines"]) + "\n"
                # Clear out the temporary array before returning
                del raw["private_key_lines"]
                return raw
                
            # Fallback legacy parsing if needed
            pk = raw.get("private_key", "")
            raw["private_key"] = pk.strip().replace("\\n", "\n").replace("\r\n", "\n")
            return raw
    except Exception:
        pass

    # 2. Local fallback file
    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gee-key.json")
    if os.path.exists(key_path):
        with open(key_path) as f:
            return json.load(f)

    raise FileNotFoundError("No GEE credentials found.")

def init_gee():
    import tempfile, json
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request

    key_dict   = _get_key_dict()
    project_id = key_dict["project_id"]

    scopes = [
        "https://www.googleapis.com/auth/earthengine",
        "https://www.googleapis.com/auth/cloud-platform",
    ]

    credentials = service_account.Credentials.from_service_account_info(
        key_dict, scopes=scopes
    )

    # Eagerly refresh so any auth error surfaces here with a clear message
    credentials.refresh(Request())

    ee.Initialize(credentials, project=project_id)


def _cloud_mask_landsat(image):
    qa     = image.select("QA_PIXEL")
    cloud  = qa.bitwiseAnd(1 << 3).eq(0)
    shadow = qa.bitwiseAnd(1 << 4).eq(0)
    return image.updateMask(cloud.And(shadow))


def _apply_scale(image):
    optical = image.select("SR_B.").multiply(0.0000275).add(-0.2)
    thermal = image.select("ST_B.*").multiply(0.00341802).add(149.0)
    return image.addBands(optical, None, True).addBands(thermal, None, True)


def fetch_city_heat_data(region, start_date, end_date, city_name, n_samples=1000):
    col = (
        ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        .filterDate(start_date, end_date)
        .filterBounds(region)
        .filter(ee.Filter.lt("CLOUD_COVER", 30))
        .map(_cloud_mask_landsat)
        .map(_apply_scale)
    )

    img   = col.median().clip(region)
    lst   = img.select("ST_B10").subtract(273.15).rename("lst_c")
    ndvi  = img.normalizedDifference(["SR_B5", "SR_B4"]).rename("ndvi")
    built = img.normalizedDifference(["SR_B6", "SR_B5"]).rename("built_index")
    stack = ee.Image.cat([lst, ndvi, built]).clip(region)

    samples  = stack.sample(region=region, scale=30, numPixels=n_samples, geometries=True)
    features = samples.getInfo()["features"]

    rows = []
    for f in features:
        p      = f["properties"]
        coords = f["geometry"]["coordinates"]
        rows.append({
            "city":        city_name,
            "lon":         coords[0],
            "lat":         coords[1],
            "lst_c":       p.get("lst_c"),
            "ndvi":        p.get("ndvi"),
            "built_index": p.get("built_index"),
        })

    return pd.DataFrame(rows)
