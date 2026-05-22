import streamlit as st
import pandas as pd
import requests

# ======================================================
# HEADER
# ======================================================
def show_header(text_title: str):

    col1, col2 = st.columns([1, 6])

    with col1:
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/3/32/Universidad_Panamericana_Logo_Dorado.jpg",
            width=200
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

    # Main page
    response = requests.get(url)
    response.raise_for_status()

    feeds = response.json()['data']['es']['feeds']

    # Find required feeds
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
    station_info = requests.get(station_info_url).json()['data']['stations']
    station_status = requests.get(station_status_url).json()['data']['stations']

    # Convert to DataFrames
    df_info = pd.DataFrame(station_info)

    df_status = pd.DataFrame(station_status)[[
        'station_id',
        'num_bikes_available',
        'num_docks_available',
        'is_installed',
        'is_renting'
    ]]

    # Merge both datasets
    df = df_info.merge(
        df_status,
        on='station_id',
        how='left'
    )

    return df


# ======================================================
# PAGE LAYOUT
# ======================================================
header_container = st.container()
main_container = st.container()

with header_container:
    show_header('Ecobici CDMX Dashboard')


with main_container:

    # Load data
    df = load_ecobici_data()

    st.subheader("Ecobici Stations Data")

    st.dataframe(df)

    # Metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Stations",
            df.shape[0]
        )

    with col2:
        st.metric(
            "Available Bikes",
            int(df['num_bikes_available'].sum())
        )

    with col3:
        st.metric(
            "Available Docks",
            int(df['num_docks_available'].sum())
        )
