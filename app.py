import streamlit as st
import pandas as pd
import requests
import folium

from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Ecobici CDMX Dashboard",
    layout="wide"
)

# ======================================================
# HEADER
# ======================================================
def show_header(text_title: str):

    col1, col2 = st.columns([1, 6])

    with col1:
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/3/32/Universidad_Panamericana_Logo_Dorado.jpg",
            width=180
        )

    with col2:
        st.title(text_title)
        st.caption("📘 Developed for: Business Intelligence (Graduate Level)")
        st.caption("Instructor: Edgar Avalos-Gauna (2026), Universidad Panamericana")


# ======================================================
# LOAD ECOBICI DATA
# ======================================================
@st.cache_data
def load_ecobici_data():

    url = "https://gbfs.mex.lyftbikes.com/gbfs/gbfs.json"

    # Main request
    response = requests.get(url)
    response.raise_for_status()

    feeds = response.json()['data']['es']['feeds']

    # Find feed URLs
    station_info_url = next(
        feed['url']
        for feed in feeds
        if feed['name'] == 'station_information'
    )

    station_status_url = next(
        feed['url']
        for feed in feeds
        if feed['name'] == 'station_status'
    )

    # Download datasets
    station_info = requests.get(
        station_info_url
    ).json()['data']['stations']

    station_status = requests.get(
        station_status_url
    ).json()['data']['stations']

    # Convert to DataFrames
    df_info = pd.DataFrame(station_info)

    df_status = pd.DataFrame(station_status)[[
        'station_id',
        'num_bikes_available',
        'num_docks_available',
        'is_installed',
        'is_renting'
    ]]

    # Merge datasets
    df = df_info.merge(
        df_status,
        on='station_id',
        how='left'
    )

    return df


# ======================================================
# CONTAINERS
# ======================================================
header_container = st.container()
main_container = st.container()

# ======================================================
# HEADER
# ======================================================
with header_container:
    show_header("Ecobici CDMX Dashboard")

# ======================================================
# MAIN CONTENT
# ======================================================
with main_container:

    # Load data
    df = load_ecobici_data()

    # ==================================================
    # KPIs
    # ==================================================
    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
        st.metric(
            "Stations",
            df.shape[0]
        )

    with kpi2:
        st.metric(
            "Available Bikes",
            int(df['num_bikes_available'].sum())
        )

    with kpi3:
        st.metric(
            "Available Docks",
            int(df['num_docks_available'].sum())
        )

    st.divider()

    # ==================================================
    # TABLE + MAP LAYOUT
    # ==================================================
    left_col, right_col = st.columns([1.2, 1])

    # --------------------------------------------------
    # TABLE
    # --------------------------------------------------
    with left_col:

        st.subheader("Ecobici Stations")

        st.dataframe(
            df[[
                'name',
                'capacity',
                'num_bikes_available',
                'num_docks_available'
            ]],
            use_container_width=True,
            height=500
        )

    # --------------------------------------------------
    # MAP
    # --------------------------------------------------
    with right_col:

        st.subheader("Stations Map")

        # Center map
        centroide_lat = df['lat'].mean()
        centroide_lon = df['lon'].mean()

        # Create map
        mapa = folium.Map(
            location=[centroide_lat, centroide_lon],
            zoom_start=12,
            tiles="CartoDB positron"
        )

        # Cluster layer
        marker_cluster = MarkerCluster().add_to(mapa)

        # Add markers
        for _, row in df.iterrows():

            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=5,
                popup=f"""
                <b>{row['name']}</b><br>
                Bikes Available: {row['num_bikes_available']}<br>
                Docks Available: {row['num_docks_available']}
                """,
                fill=True
            ).add_to(marker_cluster)

        # Render map
        st_folium(
            mapa,
            width=700,
            height=500
        )
