import pandas as pd 
import pandas_gbq
from google.oauth2 import service_account
import os 


# Create Google credentials from service account json file
service_account_json = "/path/toJSON/key"
 
credentials = service_account.Credentials.from_service_account_file(service_account_json,)

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
