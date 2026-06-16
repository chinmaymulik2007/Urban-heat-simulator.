from geopy.geocoders import Nominatim
import ee

_geolocator = Nominatim(user_agent="urban_heat_simulator")

def geocode_city(city_name):
    loc = _geolocator.geocode(city_name)
    if loc is None:
        return None
    return {
        "display_name": loc.address,
        "lat": loc.latitude,
        "lon": loc.longitude,
    }

def city_buffer_geometry(lat, lon, buffer_m):
    pt = ee.Geometry.Point([lon, lat])
    return pt.buffer(buffer_m)