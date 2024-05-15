import geopandas as gpd
import pandas as pd  # Ensure pandas is imported

try:
    # Load the GeoJSON file into a GeoDataFrame
    trees = gpd.read_file('../Tree Data.geojson')

    # Ensure that 'tree_dbh' is a numeric field and filter rows where 'tree_dbh' is not available
    trees['tree_dbh'] = pd.to_numeric(trees['tree_dbh'], errors='coerce')
    trees.dropna(subset=['tree_dbh', 'geometry'], inplace=True)

    # Extracting latitude and longitude if not directly available as columns
    if 'latitude' not in trees.columns or 'longitude' not in trees.columns:
        trees['latitude'] = trees.geometry.y
        trees['longitude'] = trees.geometry.x

    trees = trees[['latitude', 'longitude', 'tree_dbh', 'geometry']]
    trees.rename(columns={'tree_dbh': 'Tree Diameter at Breast Height (cm)'}, inplace=True)

    trees.to_file("../processed_tree_data.geojson", driver='GeoJSON')

    print("Tree Data Overview:")
    print(trees.info())
    
except Exception as e:
    print(f"An error occurred: {e}")
