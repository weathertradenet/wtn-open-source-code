

##  /tmp/scenario_analysis_asset_level.csv
##  reference_column = "id"


def dynamic_html_map(file_name, ):

    df = pd.read_csv(file_name)  # Replace with your actual filename
    df.columns = df.columns.str.strip().str.lower()
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df.columns = df.columns.str.strip()

# Remove rows with missing coordinates
    df_clean = df.dropna(subset=['latitude', 'longitude'])
    
    # Helper functions for coordinate formatting
    def format_lat(lat):
        return f"{abs(lat):.3f}°{'N' if lat >= 0 else 'S'}"
    
    def format_lon(lon):
        return f"{abs(lon):.3f}°{'E' if lon >= 0 else 'W'}"
        
    # Initialize base map
    m = folium.Map(location=[df["latitude"].mean(), df["longitude"].mean()], zoom_start=5, tiles="CartoDB positron", control_scale=True)
    
    # Add base tile layers     
    folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr='Esri Satellite',
        name='Esri Satellite',
        overlay=False,
        control=True
    ).add_to(m)
    folium.TileLayer('CartoDB positron', name='CartoDB Positron').add_to(m)   
    
    # Marker cluster layer
    marker_cluster = MarkerCluster(name="Locations").add_to(m)
    
    
    # Loop through data and add formatted tooltips
    for _, row in df.iterrows():
        tooltip = (
            f"<b>ID:</b> {row[reference_column]}<br>"
            f"<b>nature of the site:</b> {row[col2]}<br>"
            f"<b>key:</b> {row[col3]}<br>"
            f"<b>country:</b> {row[col4]}<br>"
            f"<b>occupier:</b> {row[col5]}<br>"
            f"<b>Coordinates:</b> {format_lat(row['latitude'])}, {format_lon(row['longitude'])}"
        )
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            tooltip=folium.Tooltip(tooltip, sticky=True)
        ).add_to(marker_cluster)

    
    folium.LayerControl().add_to(m)
    
    # Save to HTML
    # m.save("tmp/map.html")
    