import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.ops import unary_union
from shapely.geometry import LineString, MultiLineString, GeometryCollection
from sklearn.cluster import KMeans
import numpy as np
from matplotlib.colors import TwoSlopeNorm

def load_data(bike_path_file, tree_data_file):
    # Load the bike paths and tree data GeoJSON files
    bike_paths = gpd.read_file(bike_path_file)
    trees = gpd.read_file(tree_data_file)
    return bike_paths, trees

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

def create_buffers(bike_paths, buffer_radius=100):
    # Ensure bike paths are in a projected CRS suitable for buffering
    print("Reprojecting bike paths to a projected CRS for buffering...")
    bike_paths = bike_paths.to_crs(epsg=2263)
    
    # Create a buffer around the combined bike path segments
    print(f"Creating buffers around bike paths with a radius of {buffer_radius} meters...")
    bike_paths['buffer'] = bike_paths.geometry.buffer(buffer_radius)
    
    return bike_paths

def count_trees_in_buffers(bike_paths, trees):
    # Ensure the trees are in the same CRS as the buffered bike paths
    print("Ensuring the trees and bike paths have the same CRS...")
    trees = trees.to_crs(bike_paths.crs)
    
    # Perform a spatial join to count the number of trees within each buffer
    print("Performing spatial join to count trees within buffers...")
    tree_counts = gpd.sjoin(trees, bike_paths.set_geometry('buffer'), how='inner', predicate='within')
    
    # Count the number of trees in each bike path buffer
    print("Counting the number of trees in each buffer...")
    tree_density = tree_counts.groupby(tree_counts.index).size()
    
    # Debugging: Print tree density values
    print(tree_density)
    
    # Assign the tree density to the bike paths GeoDataFrame
    print("Assigning tree density to bike paths...")
    bike_paths['tree_density'] = bike_paths.index.map(tree_density).fillna(0)
    
    # Debugging: Check if tree density values are correctly assigned
    print(bike_paths['tree_density'].describe())
    
    return bike_paths

def plot_results(bike_paths, most_green_clusters, least_green_clusters):
    print("Plotting results...")
    # Plot the results with a gradient based on tree density
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Normalize tree density values for better color differentiation
    vmin = bike_paths['tree_density'].min()
    vcenter = bike_paths['tree_density'].mean()
    vmax = bike_paths['tree_density'].max()

    print("vmin:", vmin)
    print("vcenter:", vcenter)
    print("vmax:", vmax)
    
    # Ensure vmin, vcenter, and vmax are in ascending order
    if vmin > vcenter:
        vcenter = vmin + (vmax - vmin) / 2
    
    norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    
    # Plot bike paths with a gradient color based on tree density
    bike_paths.plot(ax=ax, column='tree_density', cmap='RdYlGn', linewidth=2, legend=True, norm=norm)
    
    # Highlight the most green clusters in green
    most_green_clusters.plot(ax=ax, color='green', linewidth=2, label='Most Green Clusters')
    
    # Highlight the least green clusters in red
    least_green_clusters.plot(ax=ax, color='red', linewidth=2, label='Least Green Clusters')
    
    # Create a single legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels)
    
    plt.title('Bike Paths with Normalized Tree Density')
    plt.show()

def output_cluster_info(bike_paths):
    print("Outputting cluster information for Google Maps...")

    # Sort bike paths by tree density
    sorted_bike_paths = bike_paths.sort_values(by='tree_density', ascending=False)
    
    # Get the five most and least green clusters
    most_green_clusters = sorted_bike_paths.head(5)
    least_green_clusters = sorted_bike_paths.tail(5)
    
    # Drop additional geometry columns before outputting to GeoJSON
    most_green_clusters = most_green_clusters.drop(columns=['buffer'])
    least_green_clusters = least_green_clusters.drop(columns=['buffer'])
    
    # Output the results
    most_green_clusters.to_file("./Bike Lane groupings/most_green_clusters.geojson", driver='GeoJSON')
    least_green_clusters.to_file("./Bike Lane groupings/least_green_clusters.geojson", driver='GeoJSON')
    
    print("Most green clusters and least green clusters have been outputted to GeoJSON files.")
    
    return most_green_clusters, least_green_clusters

def main():
    try:
        # Load the processed data
        print("Loading data...")
        bike_paths, trees = load_data('processed_bike_paths.geojson', 'processed_tree_data.geojson')

        # Cluster the bike path segments
        print("Clustering bike paths...")
        bike_paths = cluster_bike_paths(bike_paths, n_clusters=100)

        # Combine bike path segments within each cluster
        print("Combining bike paths...")
        combined_bike_paths = combine_bike_paths(bike_paths)

        # Create buffers around the combined bike paths
        print("Creating buffers...")
        buffered_bike_paths = create_buffers(combined_bike_paths)

        # Count trees within the buffers
        print("Counting trees within buffers...")
        bike_paths_with_density = count_trees_in_buffers(buffered_bike_paths, trees)

        # Reproject buffered bike paths back to the original CRS
        bike_paths_with_density = bike_paths_with_density.to_crs(epsg=4326)

        # Output the most and least green clusters
        most_green_clusters, least_green_clusters = output_cluster_info(bike_paths_with_density)

        # Plot the results
        print("Plotting results...")
        plot_results(bike_paths_with_density, most_green_clusters, least_green_clusters)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
