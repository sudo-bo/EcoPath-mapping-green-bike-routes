import pandas as pd

try:
    traffic_counts = pd.read_csv('../Traffic_Volume_Counts.csv')
    traffic_counts.drop(['ID', 'SegmentID', 'Direction'], axis=1, inplace=True)

    traffic_counts['Date'] = pd.to_datetime(traffic_counts['Date'])

    # Sorting data for sequential processing
    traffic_counts.sort_values(by=['Roadway Name', 'From', 'To', 'Date'], inplace=True)

    hour_columns = [
        '12:00-1:00 AM', '1:00-2:00AM', '2:00-3:00AM', '3:00-4:00AM',
        '4:00-5:00AM', '5:00-6:00AM', '6:00-7:00AM', '7:00-8:00AM',
        '8:00-9:00AM', '9:00-10:00AM', '10:00-11:00AM', '11:00-12:00PM',
        '12:00-1:00PM', '1:00-2:00PM', '2:00-3:00PM', '3:00-4:00PM',
        '4:00-5:00PM', '5:00-6:00PM', '6:00-7:00PM', '7:00-8:00PM',
        '8:00-9:00PM', '9:00-10:00PM', '10:00-11:00PM', '11:00-12:00AM'
    ]

    # Grouping by 'Roadway Name', 'From', and 'To' and setting up aggregation functions
    aggregation_functions = {hour: 'sum' for hour in hour_columns}
    aggregation_functions['Date'] = ['count', 'max']
    
    result = traffic_counts.groupby(['Roadway Name', 'From', 'To']).agg(aggregation_functions).reset_index()

    # Flattening the leftover MultiIndexes in columns
    result.columns = [' '.join(col).strip() for col in result.columns.values]

    result.rename(columns={
        'Date count': 'Number of Days Measured',
        'Date max': 'Last Day of Count'
    }, inplace=True)

    result.to_csv('../aggregated_traffic_volume_counts.csv', index=False)

    print("\nTraffic Aggregation Data:")
    print(result.info())

except Exception as e:
    print("An error occurred:", e)


