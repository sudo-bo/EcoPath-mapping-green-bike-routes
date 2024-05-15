import pandas as pd

try:
    columns_to_keep = [
        'CRASH DATE', 'CRASH TIME', 'LATITUDE', 'LONGITUDE', 'NUMBER OF PERSONS INJURED',
        'NUMBER OF PERSONS KILLED', 'NUMBER OF PEDESTRIANS INJURED', 'NUMBER OF PEDESTRIANS KILLED',
        'NUMBER OF CYCLIST INJURED', 'NUMBER OF CYCLIST KILLED'
    ]
    collisions = pd.read_csv(
        '../Motor_Vehicle_Collisions.csv',
        usecols=columns_to_keep,
        parse_dates=['CRASH DATE'],
        on_bad_lines='skip'
    )
    
    # Filling in NaN values with 0 before conversion to int16
    int_columns = [
        'NUMBER OF PERSONS INJURED', 'NUMBER OF PERSONS KILLED',
        'NUMBER OF PEDESTRIANS INJURED', 'NUMBER OF PEDESTRIANS KILLED',
        'NUMBER OF CYCLIST INJURED', 'NUMBER OF CYCLIST KILLED'
    ]
    collisions[int_columns] = collisions[int_columns].fillna(0).astype('int16')

    # Standardizing CRASH TIME format to HH:MM:SS
    collisions['CRASH TIME'] = collisions['CRASH TIME'].apply(
        lambda x: x if len(x.split(':')) == 3 else (x + ':00' if ':' in x else x + ':00:00')
    )

    # Combining 'CRASH DATE' and 'CRASH TIME' into a single datetime column
    collisions['CRASH DATETIME'] = pd.to_datetime(collisions['CRASH DATE'].dt.strftime('%Y-%m-%d') + ' ' + collisions['CRASH TIME'],
                                                  format='%Y-%m-%d %H:%M:%S', errors='coerce')

    # Dropping rows with missing essential coordinates or datetime
    collisions.dropna(subset=['LATITUDE', 'LONGITUDE', 'CRASH DATETIME'], inplace=True)


    # New order with 'CRASH DATETIME' as the third column
    new_columns = [
        'CRASH DATE', 'CRASH TIME', 'CRASH DATETIME', 'LATITUDE', 'LONGITUDE', 
        'NUMBER OF PERSONS INJURED', 'NUMBER OF PERSONS KILLED', 
        'NUMBER OF PEDESTRIANS INJURED', 'NUMBER OF PEDESTRIANS KILLED', 
        'NUMBER OF CYCLIST INJURED', 'NUMBER OF CYCLIST KILLED'
    ]
    
    collisions = collisions[new_columns]
    collisions.to_csv('cleaned_motor_vehicle_collisions.csv', index=False)
    
    print("\nCollisions Data:")
    print(collisions.info())


except Exception as e:
    print("An error occurred:", e)

