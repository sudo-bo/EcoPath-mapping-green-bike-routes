import geopandas as gpd

try:
    # Load the GeoJSON file into a GeoDataFrame
    bike_paths = gpd.read_file('../NYC Bike Routes.geojson')

    # Selecting the necessary columns and renaming them for clarity
    bike_paths = bike_paths[['fromstreet', 'tostreet', 'street', 'lanecount', 'facilitycl', 'geometry']]

    bike_paths.rename(columns={
        'fromstreet': 'From Street',
        'tostreet': 'To Street',
        'street': 'Street Name',
        'lanecount': 'Lane Count',
        'facilitycl': 'Facility Class'
    }, inplace=True)

    bike_paths.to_file("../processed_bike_paths.geojson", driver='GeoJSON')

    print("\nBike Routes Data:")
    print(bike_paths.info())

except Exception as e:
    print(f"An error occurred: {e}")

