from streamlit_folium import st_folium
import folium

with main_container:

    # =========================================
    # LOAD DATA
    # =========================================
    df = load_ecobici_data()

    # =========================================
    # KPIs
    # =========================================
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

    # =========================================
    # TABLE + MAP LAYOUT
    # =========================================
    left_col, right_col = st.columns([1.2, 1])

    # -----------------------------------------
    # LEFT SIDE -> TABLE
    # -----------------------------------------
    with left_col:

        st.subheader("Ecobici Stations")

        st.dataframe(
            df[[
                'name',
                'capacity',
                'num_bikes_available',
                'num_docks_available'
            ]],
            use_container_width=True
        )

    # -----------------------------------------
    # RIGHT SIDE -> MAP
    # -----------------------------------------
    with right_col:

        st.subheader("Stations Map")

        # Center map
        centroide_lat = df['lat'].mean()
        centroide_lon = df['lon'].mean()

        # Create map
        mapa = folium.Map(
            location=[centroide_lat, centroide_lon],
            zoom_start=12
        )

        # Add markers
        for _, row in df.iterrows():

            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=row['name']
            ).add_to(mapa)

        # Render map in Streamlit
        st_folium(
            mapa,
            width=700,
            height=500
        )
