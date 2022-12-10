<h1> Using Cron Jobs and Bigquery </h1>

[![Using - MacOS](https://img.shields.io/badge/Using-MacOS-white?style=for-the-badge&logo=Apple&logoColor=black)](https://) [![Using - Windows](https://img.shields.io/badge/Using-Windows-lightblue?style=for-the-badge&logo=Windows&logoColor=black)](https://)

# 🏃 TL;DR:

- Retrieved data from https://aqicn.org/ through their API.
- Built Data Frame from the JSON file and added timestamp column after extraction.
- Built a server using OpenSSH, on a separate machine running Windows and configured SFTP for the data.
- Wrote a script on the Windows Server Machine to upload incoming data to a BigQuery hosted table.
- Automated the data retrieval through CronJobs on the data landing machine and also the SFTP to the Windows Server (with a delay)
- The ETL is running in batch once every hour. Also, once transfered the .csv file is deleted from the landing folder and moved to a separate location (backup).
- On the server side, using 'Windows Scheduler' - automated a script to check once every hour if there is any incoming data and upload it to the BigQuery table. 

# 🔭 Project's scope
According to a Forbes article from 2020, _"in the list of countries from worst to best, Poland and Italy are number 53 and 59 respectively."_, whereas _"Romania is number 54"_. This situation is especially concerning to me, because the measurements are for the city of Bucharest in wich I currently live in. 

Therefore, when I was looking for a suitable project to develop ETL skills upon, it came natural to me to try and build my own database for historic air quality data for my city. (Wich will not be redistributed as it goes against the API's ToS, hence for historical data go check https://aqicn.org/data-platform.)

I think it would also be useful to bind a Twitter Bot to this database, which would tweet each time a sensor exceeds a particular value. Issues may occur on the Google Cloud side, because I have to do better research as not to accidentally trigger costs on the platform, but also further check not to go against any 'Terms of Service' with https://aqicn.org. 

# 📦 AQI data retrieval through the API

In order to get access to the air-quality index, the https://aqicn.org platform gives access to anyone interested, through their API. All you have to do is to sign up for your own token at https://aqicn.org/data-platform/token/.

In order to use this token to retrieve AQI data, you'll have to access the JSON file containing it. You'll first have to get the geolocation coordinates for your area of interest. I did it using http://bboxfinder.com as shown below:

<img src="https://user-images.githubusercontent.com/44103446/206877812-0114cd51-8845-4ed5-8838-e72d63315f11.png" width=800 height=450 />



You then copy the perimeter as it is from the URL and take it to this next address, replacing the {variables} with the right values:

##### https://api.waqi.info/map/bounds/?latlng={latlngbox}&token={api_token}

<img src="https://user-images.githubusercontent.com/44103446/206877881-10afa459-6aa0-4b60-a9fe-8557e5a5fd7e.png" width=800 height=450 />



As shown above, there are 4 stations available for the selected perimeter. Next we'll write a python script to extract this data and also parse it to a pandas dataframe.

# 🐍 Python DataFrame from the AQI JSON data


```python
import os
import datetime
import pandas as pd 

def main(): 

    # Retrieve data from website through their API
    base_url = "https://api.waqi.info"
    api_key = "~path/to/TokenFile"
    final_csv_path = "~path/to/SaveCSV"
   
    # Saved token to a file
    with open(api_key) as f:
            contents = f.readlines()
            key = contents[0]
            
    # Set the perimeter for the desired city/location
    latlngbox = "44.297690,25.860967,44.574211,26.286687" # For Bucharest
    trail_url=f"/map/bounds/?latlng={latlngbox}&token={key}" 
    my_data = pd.read_json(base_url + trail_url) # Join parts of URL
    print('Raw data loaded successfully into ->', my_data.columns) #JSON contains 2 columns: ‘status’ and ‘data’
```
##### The above section of the code is intended to take the entire JSON file and parse it to a dataframe. It contains 2 columns 'status' and 'data'. We are interested in the information stored in the data column, which needs further cleaning and transformations.


```python
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
    aqi_dataframe = df.dropna(subset = ['aqi'])
```
##### In the code snippet above we looped through the JSON data column row by row and split them in 4 separate columns 'station_name', 'lat', 'lon' and 'aqi'. Next we made sure that every value is set to numeric and also that there are no 'NaN' values left behind.


```python
# Add current date-time column 
    now = datetime.datetime.now()
    aqi_dataframe["date"] = now
```
##### Also, in order to build a table with historical data we need a timestamp for the extraction, so using the code snippet above we introduced another column with the datetime information.

##### Next we'll check if at the indicated path we have a previously stored file and delete it and save the new data instead.

```python
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
```


# 🔐 Create server for SFTP


##### On a separate windows running machine, I've used OpenSSH to host a server to which we'll send the retrieved AQI data. The process I followed was perfectly explained elsewhere: [Veronica Explains's video](https://www.youtube.com/watch?v=3FKsdbjzBcc&t=974s) and also [SavvyNik's Video](https://www.youtube.com/watch?v=HCmEB5qtkSY) - I'd like to take this opportunity to thank these creators for their wonderful explanations.

##### The following is a Firewall rule that I've created to allow the SFTP take place:
<img src="https://user-images.githubusercontent.com/44103446/206878004-2c9c04ce-51e8-4dfe-b95f-f332134146a1.png" width=800 height=400 />




##### By modifying the \~\ssh\sshd_config file I've set a certain folder for data to land in when the SFTP takes place.

# 🤖 Python Script for automatic SFTP 

##### The following is a script intended to transfer the .csv file once created, through SFTP to the remote server and then it will move the file to another location for backup.


```python
import pysftp
import os

def main():

    # Keep this file safe! 
    credentials = '/Users/alexandrubujor/Public/Bujor/AQI-Project/credentials.txt'
    
    # Load credentials from safe file.
    
    with open(credentials, "r") as f:
            for line in f:
              contents = line.strip().split(",")
            
    host = str(contents[x])
    user = str(contents[y])
    pswd = str(contents[z])
    file_to_upload = str(contents[w])
```

##### This is not a secure enough way of transfering files, but it's the one that worked and I settled with it for this project. (I tried to use the encryption keys, but failed to make them work so went back to user and pswd. Will definetly look into it after I finish documenting this.)


```python
  # Establish sftp connection with remote server and push collected data.
    
    with pysftp.Connection(host, username = user, password = pswd) as sftp:
        try:
            if os.path.exists(file_to_upload):
                sftp.put(file_to_upload, preserve_mtime=True)
                print('File uploaded successfully!')
            else:
                print('No file in specified directory!')
        except:
            print('Transfer error encountered!')    

```
### So far we have a script which retrieves data from the website and saves it in a .csv file. Also, we have a server to which we'll send the file and a script that we'll use to automate the SFTP.


# ☁️ BigQuery table and connection:


##### For this project I've used the free SandBox Version of BigQuery. The following are screenshots from within the platform for the steps taken to configure the table which will store the historical AQI data.

<img src="https://user-images.githubusercontent.com/44103446/206878052-b3fa1734-5e06-492b-aebc-2e9b092f59cc.png" width=200 height=400 />  <img src="https://user-images.githubusercontent.com/44103446/206878072-6b5ec9cd-b313-4818-a001-462a351d0401.png" width=200 height=400 />


##### Now that we have the table with the right columns and data types, we'll write a script to upload the .csv contents to the BigQuery table.
<img src="https://user-images.githubusercontent.com/44103446/206878266-665fde05-9e28-4082-ae38-d9efcc5aa906.png" width=800 height=400 />


##### First wel'll import the needed libraries and also create a 'credentials' variable needed for authentication and gaining writing rights on our BigQuery platform.


```python
import pandas as pd 
import pandas_gbq
from google.oauth2 import service_account
import os 


# Create Google credentials from service account json file
service_account_json = "~/path/to/JSON-File"
 
credentials = service_account.Credentials.from_service_account_file(service_account_json,)
```


##### We'll create a dataframe with the data we want to push and variables for the project and dataset ID for easy code reuse in case of changing projects.


```python
# Load data we need to push in a temporary dataFrame
csv_path = r"C:\Incoming\aqi.csv"
temp_data = pd.read_csv(csv_path, index_col = 0)

# Project and dataset ID: 
bgq_project = "bucharest_air_quality"
bgq_dataset = "air_quality"
```


##### And finally a function for pushing the data to the database.


```python
def push_to_DB(path_to_file):
    try:
        if os.path.exists(path_to_file):
            temp_data.to_gbq(f"{bgq_project}.{bgq_dataset}",if_exists = "append",credentials=credentials)
            print("Contents successfully uploaded to database!")
            os.remove(path_to_file)
            print("Previously stored file removed! For historical data check with archive.")
        else:
            print("No previously stored data found. Nothing to upload!")
    except:
        print('Error while transferring data to database!')
    
push_to_DB(csv_path)
```


# ⏲️ CronJobs and Windows Scheduler: 


##### The steps in which our scripts will run are:

##### 1. Retrieve data from the website once every hour and save it in a .csv file to a specified location.





##### 2. SFTP the .csv file to the Windows Server each hour with a delay to allow data to be written in case of a big load.





##### 3. With an extra delay, check if there is a file in our initial landing path and move it to a separate location for back-up. Furthermore, rename the file and also create a dedicated folder for each day for easy acces. This is done by using the following script: 


```python
import os
import datetime
import shutil

''' Store all paths in a separate file '''
credentials = '~/your/Path'

with open(credentials, "r") as f:
            for line in f:
              contents = line.strip().split(",")

path_file_to_move = str(contents[3])
where_to_move = str(contents[4])

```

##### Create variables with time components for both folder's and file's new name


```python
''' Get current time to use for folder and file's new name '''
# %H = hour using 24h clock, %d = day of month, %B = full month name, %Y = year including century (eg. 2022 instead of just 22)

now            = datetime.datetime.now()
time_component = now.strftime('Hour-%H %d-%B-%Y')
new_file_name = "aqi-data for "+time_component

```


##### And also functions for creating the folder and moving the data for easy code modification when changing projects.


```python
# Create folder for each new day for easier acces.

def make_new_folder(where_to_move,folder_name):
    # %d = day of month, %B = full month name, %Y = year including century (eg. 2022 instead of just 22)
    folder_name = now.strftime('%d-%B-%Y')

    if not os.path.exists(f'{where_to_move}/{folder_name}'):
        os.makedirs(f'{where_to_move}/{folder_name}')
        print(f'Successfully made a folder for {folder_name}')
    else:
        print('Folder already in place!')
        pass

make_new_folder(where_to_move,folder_name)

''' The shutil.move() function takes 2 arguments: the initial file's path, 
    and the final path, where if a new file name is given, it also renames it for you.'''

full_archive_path = f"{where_to_move}/{folder_name}/{new_file_name}"

# Function for moving and renaming initial file to archive.
def move_to_archive(path_file_to_move,full_archive_path):
    if os.path.exists(path_file_to_move):
    	shutil.move(path_file_to_move, full_archive_path)
    	print("File was archived successfully!")
    else:
    	print("Could not find file inside directory!")

move_to_archive(path_file_to_move,full_archive_path)
```

<img src="https://user-images.githubusercontent.com/44103446/206878312-1df25d1d-2789-492f-92ef-bc24e787fed1.png" width=800 height=200 />
    <figcaption>As shown, every script runs with a 5 minute delay after the other to allow a larger file to download/upload.</figcaption>




##### 4. On the server side, we'll use 'Task Scheduler' for automating the uploading process with the upload script shown above. It also has a delay, bigger then the moving-renaming script. 

##### Wrote a script and saved it as a .bat file to run in 'Task Scheduler' containing the Python Path and also the BigQuery Script Path.

```bash
"~path\anaconda3\python.exe" "~path\bigquery_aqi_loader.py"
```


<img src="https://user-images.githubusercontent.com/44103446/206878355-be52ac17-e2fe-4da1-85ca-1ab61e975714.png" width=1000 height=500 />


# 👨‍💻 The end result in the BigQuery Database looks like this:

<img src="https://user-images.githubusercontent.com/44103446/206878383-5c495812-27f4-4637-b2ff-9879af617fa4.png" width=1000 height=500 />



# ✋ Limitations:

* Through the API, I only get access to 4 stations, but there are [many more](https://aqicn.org/station/romania/sector-1/strada-general-henri-mathias-berthelot) on the official website for the city of Bucharest. 
* SFTP should work using encrypted keys and not username/password.
* The chosen delay time is enough for now, because the load it's also small. However, given the process takes places on my physical machines the computing power for larger files/tables might not be enough to deliver them in time.
* Code works fine for small files/tables but might be slow for larger ones, although it relies on well established libraries.
* Didn't write tests for the code so there might be several ways it can break. Next thing on my learning journey is TDD so I'll use this code for my practical work.
* #### This is all I could come with for now.

# ✨ Thank your very much for your attention!   ✨


#####  As always I'm looking forward for your comments and suggestions! ✌️
