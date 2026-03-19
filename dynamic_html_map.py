import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster


def dynamic_html_map(my_locations_file, reference_column, output_file="tmp/map.html"):
    df = pd.read_csv(my_locations_file)

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()
    reference_column = reference_column.strip().lower()

    # Validate required columns
    required_columns = {"latitude", "longitude", reference_column}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    # Convert coordinates
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    # Remove rows with missing coordinates
    df_clean = df.dropna(subset=["latitude", "longitude"]).copy()

    if df_clean.empty:
        raise ValueError("No valid rows with latitude and longitude were found.")

    def format_lat(lat):
        return f"{abs(lat):.3f}°{'N' if lat >= 0 else 'S'}"

    def format_lon(lon):
        return f"{abs(lon):.3f}°{'E' if lon >= 0 else 'W'}"

    # Initialize map
    m = folium.Map(
        location=[0, 0],
        # location=[df_clean["latitude"].mean(), df_clean["longitude"].mean()],
        zoom_start=2,
        tiles="CartoDB positron",
        control_scale=True,
    )

    # Base layers
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri Satellite",
        name="Esri Satellite",
        overlay=False,
        control=True,
    ).add_to(m)
    folium.TileLayer("CartoDB positron", name="CartoDB Positron").add_to(m)

    marker_cluster = MarkerCluster(name="Locations").add_to(m)

    for _, row in df_clean.iterrows():
        tooltip = (
            f"<b>ID:</b> {row[reference_column]}<br>"
            f"<b>Coordinates:</b> {format_lat(row['latitude'])}, {format_lon(row['longitude'])}"
        )
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            tooltip=folium.Tooltip(tooltip, sticky=True),
        ).add_to(marker_cluster)

    folium.LayerControl().add_to(m)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    m.save(output_file)
    return m

    