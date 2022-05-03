import os
import datetime
import pandas as pd 



def main(): 

    # Retrieve data from website through their API
    # See details of API at:- https://aqicn.org/api/
    base_url = "https://api.waqi.info"
    api_key = "~path/"
    final_csv_path = "~path/aqi.csv"
    # Saved token to a file
    with open(api_key) as f:
            contents = f.readlines()
            key = contents[0]
    # Set the perimeter for the desired city/location
    # Can do that going to https://bboxfinder.com/ and use the rectangle tool
    # For ease of access, the latlngbox variable for your particular project can be copy-pasted from
    #   the https:/bboxfinder.com/#_____ link where, "_____" is in written in the right order 
    latlngbox = "44.297690,25.860967,44.574211,26.286687" # For Bucharest
    trail_url=f"/map/bounds/?latlng={latlngbox}&token={key}" 
    my_data = pd.read_json(base_url + trail_url) # Join parts of URL
    print('Raw data loaded successfully into ->', my_data.columns) #JSON contains 2 columns: ‘status’ and ‘data’
    
    
    # Loop JSON file to create DataFrame from the 'data' column
    all_rows = []
    for each_row in my_data['data']:
        all_rows.append([each_row['station']['name'],
        each_row['lat'],
        each_row['lon'],
        each_row['aqi']])
    
    # Append isolated rows to manually named columns
    df = pd.DataFrame(all_rows, columns=['station_name', 'lat', 'lon', 'aqi'])
    
    # Clean the DataFrame
    df['aqi'] = pd.to_numeric(df.aqi, errors='coerce') # Invalid parsing to NaN
    # Remove NaN (Not a Number) entries in col
    df1 = df.dropna(subset = ['aqi'])
    # Add current date-time column 
    now = datetime.datetime.now()
    df1["date"] = now

    # Write dataframe to csv
    
    try:
        if os.path.exists(final_csv_path):
            os.remove(final_csv_path)
            print("Previously stored file removed!")
            df1.to_csv(final_csv_path)
            print('Data was cleaned and successfully saved!')
        else:
            print("No previously stored data found. Saving data ...")
            df1.to_csv(final_csv_path)
            print('Data was cleaned and successfully saved!')
    except:
        print('Error while processing data!')


if __name__ == '__main__':
    main() 




