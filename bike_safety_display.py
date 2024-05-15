import geopandas as gpd
import folium

# Load the GeoJSON files for safety clusters
most_safe_clusters = gpd.read_file("most_safe_clusters.geojson")
least_safe_clusters = gpd.read_file("least_safe_clusters.geojson")

# Initialize the map at a given location
m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)  # Centered around New York City

# Add most safe clusters
folium.GeoJson(
    most_safe_clusters,
    style_function=lambda feature: {
        'color': 'green',
        'weight': 2,
    },
    name='Most Safe Clusters'
).add_to(m)

# Add least safe clusters
folium.GeoJson(
    least_safe_clusters,
    style_function=lambda feature: {
        'color': 'red',
        'weight': 2,
    },
    name='Least Safe Clusters'
).add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Save the map to an HTML file
m.save("../Mapped Results/safety_clusters_map.html")

# For Jupyter Notebooks, we can display the map inline
m
