import pandas as pd
import matplotlib.pyplot as plt

def load_traffic_data(file_path):
    traffic_data = pd.read_csv(file_path)
    return traffic_data

def process_traffic_data(traffic_data):
    # Filtering data from 2015 onwards
    traffic_data['Last Day of Count'] = pd.to_datetime(traffic_data['Last Day of Count'])
    traffic_data_filtered = traffic_data[traffic_data['Last Day of Count'].dt.year >= 2015]

    # Aggregating traffic volume by time of day
    time_columns = [col for col in traffic_data_filtered.columns if 'sum' in col]
    traffic_sums = traffic_data_filtered[time_columns].sum()

    return traffic_sums

def plot_traffic_data(traffic_sums):
    # Plotting traffic volume by time of day
    plt.figure(figsize=(12, 6))
    traffic_sums.index = [col.replace('sum', '').strip() for col in traffic_sums.index]
    traffic_sums.plot(kind='bar')
    plt.title('Traffic Volume by Time of Day (2015 to 2020)')
    plt.xlabel('Time of Day')
    plt.ylabel('Total Traffic Volume')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def load_collision_data(file_path):
    collision_data = pd.read_csv(file_path)
    return collision_data

def process_collision_data(collision_data):
    # Filtering data from 2015 onwards
    collision_data['CRASH DATE'] = pd.to_datetime(collision_data['CRASH DATE'])
    collision_data_filtered = collision_data[collision_data['CRASH DATE'].dt.year >= 2015]

    # Extracting hour from CRASH TIME
    collision_data_filtered['HOUR'] = pd.to_datetime(collision_data_filtered['CRASH TIME'], format='%H:%M:%S').dt.hour

    # Aggregatting crashes by time of day
    hourly_crashes = collision_data_filtered['HOUR'].value_counts().sort_index()

    return hourly_crashes

def plot_collision_data(hourly_crashes):
    # Plotting number of crashes by time of day
    plt.figure(figsize=(12, 6))
    hourly_crashes.index = [f'{hour % 12 if hour % 12 != 0 else 12} {"AM" if hour < 12 else "PM"}' for hour in hourly_crashes.index]
    hourly_crashes.plot(kind='bar')
    plt.title('Number of Crashes by Time of Day (2015 to 2024)')
    plt.xlabel('Time of Day')
    plt.ylabel('Number of Crashes')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main():
    # Traffic Volume Analysis
    print("Loading and processing traffic volume data...")
    traffic_data = load_traffic_data('aggregated_traffic_volume_counts.csv')
    traffic_sums = process_traffic_data(traffic_data)
    print("Plotting traffic volume data...")
    plot_traffic_data(traffic_sums)

    # Collision Data Analysis
    print("Loading and processing collision data...")
    collision_data = load_collision_data('cleaned_motor_vehicle_collisions.csv')
    hourly_crashes = process_collision_data(collision_data)
    print("Plotting collision data...")
    plot_collision_data(hourly_crashes)

if __name__ == "__main__":
    main()
