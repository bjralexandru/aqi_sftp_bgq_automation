import pysftp
import os

def main():

    # Keep this file safe! 
    credentials = '~path/credentials.txt'
    
    # Load credentials from safe file.
    
    with open(credentials, "r") as f:
            for line in f:
              contents = line.strip().split(",")
            
    host = str(contents[0])
    user = str(contents[1])
    pswd = str(contents[2])
    file_to_upload = str(contents[3])

    
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


if __name__ == '__main__':
    main()
