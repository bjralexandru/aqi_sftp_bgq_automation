import os
import datetime
import shutil

''' Get current time to use for folder and file's new name '''
# %H = hour using 24h clock, %d = day of month, %B = full month name, %Y = year including century (eg. 2022 instead of just 22)
now            = datetime.datetime.now()
time_component = now.strftime('Hour-%H %d-%B-%Y')

''' Stored all paths in a separate file '''
credentials = '/Users/alexandrubujor/Public/Bujor/AQI-Project/credentials.txt'

with open(credentials, "r") as f:
            for line in f:
              contents = line.strip().split(",")

uploaded_file = str(contents[3])
archive_path = str(contents[4])

new_file_name = "aqi-data for "+time_component

# new code snippet

folder_name = now.strftime('%d-%B-%Y')


# Create folder for each new day for easier acces.

def make_new_folder(archive_path,folder_name):
    # %d = day of month, %B = full month name, %Y = year including century (eg. 2022 instead of just 22)
    folder_name = now.strftime('%d-%B-%Y')

    if not os.path.exists(f'{archive_path}/{folder_name}'):
        os.makedirs(f'{archive_path}/{folder_name}')
        print(f'Successfully made a folder for {folder_name}')
    else:
        print('Folder already in place!')
        pass

make_new_folder(archive_path,folder_name)

''' The shutil.move() function takes 2 arguments: the initial file's path, 
    and the final path, where if a new file name is given, it also renames it for you.'''

full_archive_path = f"{archive_path}/{folder_name}/{new_file_name}"

# Function for moving and renaming initial file to archive.
def move_to_archive(uploaded_file,full_archive_path):
    if os.path.exists(uploaded_file):
    	shutil.move(uploaded_file, full_archive_path)
    	print("File was archived successfully!")
    else:
    	print("Could not find file inside directory!")

move_to_archive(uploaded_file,full_archive_path)