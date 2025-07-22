import streamlit as st
import requests
from datetime import date
from streamlit_folium import folium_static
import folium

API_KEY = "Svf76eKbNaiczYmWzlaYLQwe36o1t1l0umNfvd8v"  # Replace with your NASA API key

st.set_page_config(page_title="NASA Mission Dashboard", layout="wide")

# ---------- APOD ----------
def load_apod():
    url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else None

# ---------- EPIC ----------
def load_epic(date_str):
    url = f"https://epic.gsfc.nasa.gov/api/natural/date/{date_str}?api_key={API_KEY}"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else None

def build_epic_url(img_info):
    dt = img_info["date"].split()[0]
    yyyy, mm, dd = dt.split("-")
    img = img_info["image"]
    return f"https://epic.gsfc.nasa.gov/archive/natural/{yyyy}/{mm}/{dd}/jpg/{img}.jpg"

# ---------- GIBS ----------
def add_gibs_layer(map_obj, date_str, layer_name, gibs_layer_id, file_ext="jpg"):
    url = f"https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/{gibs_layer_id}/default/{date_str}/GoogleMapsCompatible_Level9/{{z}}/{{y}}/{{x}}.{file_ext}"
    folium.raster_layers.TileLayer(
        tiles=url,
        attr=f"NASA GIBS - {layer_name}",
        name=layer_name,
        overlay=True,
        control=True,
        opacity=0.8,
    ).add_to(map_obj)

# ---------- UI ----------
st.title("🚀 NASA Mission Control Dashboard")

tab1, tab2, tab3 = st.tabs(["🌌 APOD", "🌍 EPIC Earth", "🛰️ GIBS Satellite Map"])

# -- APOD TAB --
with tab1:
    apod = load_apod()
    if apod:
        st.header(apod["title"])
        st.image(apod["url"], caption=apod.get("copyright", "NASA"))
        st.write(apod["explanation"])
        st.write(f"📅 Date: {apod['date']}")
    else:
        st.error("Could not load APOD.")

# -- EPIC TAB --
with tab2:
    st.header("🌍 EPIC Earth Imagery")
    selected_date = st.date_input("Select a date for EPIC", date.today())
    epic_images = load_epic(selected_date.isoformat())

    if epic_images:
        st.success(f"Found {len(epic_images)} images")
        for img in epic_images[:6]:  # Limit display to first 6
            url = build_epic_url(img)
            st.image(url, caption=img['caption'], use_column_width=True)
    else:
        st.warning("No EPIC images found for this date.")

# -- GIBS TAB --
with tab3:
    st.header("🛰️ NASA GIBS Satellite Map")
    map_date = st.date_input("Select GIBS date", date.today())
    map_date_str = map_date.strftime("%Y-%m-%d")

    m = folium.Map(location=[20, 0], zoom_start=2, tiles=None)

    # Add layers
    add_gibs_layer(m, map_date_str, "MODIS Terra - True Color", "MODIS_Terra_CorrectedReflectance_TrueColor")
    add_gibs_layer(m, map_date_str, "FIRMS Active Fires", "FIRMS_VIIRS_SNPP_NRT", file_ext="png")
    add_gibs_layer(m, map_date_str, "VIIRS Night Lights", "VIIRS_SNPP_DayNightBand_ENCC", file_ext="jpg")

    folium.LayerControl().add_to(m)
    folium_static(m)
