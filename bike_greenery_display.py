import geopandas as gpd
import folium

# Load the GeoJSON files
most_green_clusters = gpd.read_file("most_green_clusters.geojson")
least_green_clusters = gpd.read_file("least_green_clusters.geojson")

# Initialize the map at a given location
m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)  # Centered around New York City

# Add most green clusters
folium.GeoJson(
    most_green_clusters,
    style_function=lambda feature: {
        'color': 'green',
        'weight': 2,
    },
    name='Most Green Clusters'
).add_to(m)

# Add least green clusters
folium.GeoJson(
    least_green_clusters,
    style_function=lambda feature: {
        'color': 'red',
        'weight': 2,
    },
    name='Least Green Clusters'
).add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Save the map to an HTML file
m.save("../Mapped Results/bike_clusters_map.html")

# For Jupyter Notebooks, we can display the map inline
m
