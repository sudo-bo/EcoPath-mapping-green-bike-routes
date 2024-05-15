import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.ops import unary_union
from shapely.geometry import Point, LineString, MultiLineString, GeometryCollection
from sklearn.cluster import KMeans
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def load_data(bike_path_file, crash_data_file):
    # Load the bike paths and crash data GeoJSON files
    bike_paths = gpd.read_file(bike_path_file)
    crashes = pd.read_csv(crash_data_file, parse_dates=['CRASH DATETIME'])
    return bike_paths, crashes

def cluster_bike_paths(bike_paths, n_clusters=50):
    # Extract centroids for clustering
    centroids = np.array([geom.centroid.coords[0] for geom in bike_paths.geometry])
    
    # Perform KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(centroids)
    bike_paths['cluster'] = kmeans.labels_
    
    return bike_paths

def combine_bike_paths(bike_paths):
    combined_bike_paths = []
    
    # Combine bike paths within each cluster
    for cluster in bike_paths['cluster'].unique():
        cluster_paths = bike_paths[bike_paths['cluster'] == cluster]
        combined_cluster_path = unary_union(cluster_paths.geometry)
        
        if isinstance(combined_cluster_path, (LineString, MultiLineString)):
            combined_bike_paths.append(combined_cluster_path)
        elif isinstance(combined_cluster_path, GeometryCollection):
            for geom in combined_cluster_path:
                if isinstance(geom, (LineString, MultiLineString)):
                    combined_bike_paths.append(geom)
        else:
            print(f"Unhandled geometry type: {type(combined_cluster_path)}")
    
    print(f"Number of combined bike path segments: {len(combined_bike_paths)}")
    return gpd.GeoDataFrame(geometry=combined_bike_paths, crs=bike_paths.crs)

def create_crash_points(crashes):
    # Create GeoDataFrame from crash data
    geometry = [Point(xy) for xy in zip(crashes['LONGITUDE'], crashes['LATITUDE'])]
    crashes_gdf = gpd.GeoDataFrame(crashes, geometry=geometry, crs='EPSG:4326')
    return crashes_gdf

def calculate_safety_scores(crashes):
    # Calculate safety scores based on the weighted sum
    crashes['safety_score'] = (
        10 * crashes['NUMBER OF PERSONS KILLED'] +
        8 * crashes['NUMBER OF CYCLIST KILLED'] +
        8 * crashes['NUMBER OF PEDESTRIANS KILLED'] +
        2 * crashes['NUMBER OF PERSONS INJURED'] +
        3 * crashes['NUMBER OF CYCLIST INJURED'] +
        3 * crashes['NUMBER OF PEDESTRIANS INJURED']
    )
    return crashes

def map_crashes_to_bike_paths(bike_paths, crashes, buffer_radius=50):
    # Ensure both bike paths and crashes are in a projected CRS suitable for buffering and spatial operations
    print("Reprojecting bike paths and crashes to a projected CRS for buffering and spatial operations...")
    projected_crs = 'EPSG:2263'
    bike_paths = bike_paths.to_crs(projected_crs)
    crashes = crashes.to_crs(projected_crs)
    
    # Create buffers around bike paths
    print(f"Creating buffers around bike paths with a radius of {buffer_radius} meters...")
    bike_paths['buffer'] = bike_paths.geometry.buffer(buffer_radius)
    
    # Perform spatial join to map crashes to nearby bike paths
    print("Performing spatial join to count crashes within buffers...")
    crashes_in_buffers = gpd.sjoin(crashes, bike_paths.set_geometry('buffer'), how='inner', predicate='within')
    
    # Aggregate safety scores by bike path
    print("Aggregating safety scores by bike path...")
    bike_paths['safety_score'] = crashes_in_buffers.groupby(crashes_in_buffers.index)['safety_score'].sum().reindex(bike_paths.index, fill_value=0)
    
    # Drop the buffer column to avoid issues with multiple geometry columns
    bike_paths = bike_paths.drop(columns='buffer')
    
    return bike_paths.to_crs('EPSG:4326')  # Reproject back to the original CRS

def normalize_scores(bike_paths):
    # Normalize the safety scores for better visualization
    scaler = MinMaxScaler()
    bike_paths['normalized_safety_score'] = scaler.fit_transform(bike_paths[['safety_score']])
    return bike_paths

def get_safe_and_unsafe_clusters(bike_paths, n_clusters=5):
    # Sort by safety score to find the safest and least safe clusters
    sorted_bike_paths = bike_paths.sort_values(by='normalized_safety_score')
    
    safest_clusters = sorted_bike_paths.head(n_clusters)
    least_safe_clusters = sorted_bike_paths.tail(n_clusters)
    
    return safest_clusters, least_safe_clusters

def output_cluster_info(clusters, filename):
    # Output the cluster information for Google Maps
    clusters.to_file(filename, driver='GeoJSON')

def plot_safety_results(bike_paths, safest_clusters, least_safe_clusters):
    fig, ax = plt.subplots(figsize=(10, 10))
    
    vmin = bike_paths['normalized_safety_score'].min()
    vmax = bike_paths['normalized_safety_score'].max()
    
    bike_paths.plot(ax=ax, column='normalized_safety_score', cmap='RdYlGn_r', linewidth=2, legend=True, vmin=vmin, vmax=vmax, alpha=0.5)
    safest_clusters.plot(ax=ax, color='green', linewidth=2, label='Safest Clusters')
    least_safe_clusters.plot(ax=ax, color='red', linewidth=2, label='Least Safe Clusters')
    
    plt.legend()
    plt.title('Bike Paths with Normalized Safety Scores')
    plt.show()

def main():
    try:
        # Load the processed data
        print("Loading data...")
        bike_paths, crashes = load_data('processed_bike_paths.geojson', 'cleaned_motor_vehicle_collisions.csv')

        # Cluster the bike path segments
        print("Clustering bike paths...")
        bike_paths = cluster_bike_paths(bike_paths, n_clusters=200)

        # Combine bike path segments within each cluster
        print("Combining bike paths...")
        combined_bike_paths = combine_bike_paths(bike_paths)

        # Create crash points
        print("Creating crash points...")
        crashes_gdf = create_crash_points(crashes)

        # Calculate safety scores
        print("Calculating safety scores...")
        crashes_with_scores = calculate_safety_scores(crashes_gdf)

        # Map crashes to bike paths
        print("Mapping crashes to bike paths...")
        bike_paths_with_scores = map_crashes_to_bike_paths(combined_bike_paths, crashes_with_scores)

        # Normalize safety scores
        print("Normalizing safety scores...")
        bike_paths_normalized = normalize_scores(bike_paths_with_scores)

        # Get the safest and least safe clusters
        print("Identifying safest and least safe clusters...")
        safest_clusters, least_safe_clusters = get_safe_and_unsafe_clusters(bike_paths_normalized)

        # Output the cluster information for Google Maps
        print("Outputting cluster information for Google Maps...")
        output_cluster_info(safest_clusters, './Bike Lane groupings/most_safe_clusters.geojson')
        output_cluster_info(least_safe_clusters, './Bike Lane groupings/least_safe_clusters.geojson')

        # Plot the results
        print("Plotting results...")
        plot_safety_results(bike_paths_normalized, safest_clusters, least_safe_clusters)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
