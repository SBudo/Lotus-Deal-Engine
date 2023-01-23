#!/usr/bin/python3

import pyodbc
import configparser
import time
from datetime import datetime
import requests
import json
import os
import subprocess

print(datetime.now(),"- Starting download process")

print(datetime.now(),"- Reading configuration file")
# read the config file
config = configparser.ConfigParser()
configFilePath = r'dealEngine.conf'
config.read(configFilePath)


try:
    # Connect to the SQL database
    print(datetime.now(),"- Connecting to SQL database")
    cnxn = pyodbc.connect('DRIVER='+config["sql"]["driver"]+';SERVER=tcp:'+config["sql"]["server"]+';PORT=1433;DATABASE='+config["sql"]["database"]+';UID='+config["sql"]["username"]+';PWD='+config["sql"]["password"])
    cursor = cnxn.cursor()
    while 1:
        print(datetime.now(),"- Querying the database for a file to download")
        results = cursor.execute("SELECT TOP 1 * FROM FilecoinDeals WHERE DownloadStatus='NotStarted' or DownloadStatus='InProgress'")
        if results.arraysize == 1:
            row = cursor.fetchone()
            update_query = "UPDATE FilecoinDeals SET DownloadStatus='Completed' WHERE Filename='" + row.Filename + "' AND DownloadPath='" + row.DownloadPath + "'"
            cursor.execute(update_query)
            cnxn.commit()
            if os.path.exists(row.DownloadPath+row.Filename) == False or os.path.exists(row.DownloadPath+row.Filename+".aria2") == True:
                print(datetime.now(),"- Downloading file:",row.DownloadURL+row.Filename)
                subprocess.Popen(["aria2c", "-x", config["aria2c"]["serverConnections"], "-s", config["aria2c"]["fileSplit"], "-c", "-d", row.DownloadPath, row.DownloadURL+row.Filename]).wait()
                if os.path.exists(row.DownloadPath+row.Filename) == True:
                    print(datetime.now(),"- Download completed")
                    update_query = "UPDATE FilecoinDeals SET DownloadStatus='Completed' WHERE Filename='" + row.Filename + "' AND DownloadPath='" + row.DownloadPath + "'"
                else:
                    print(datetime.now(),"- Error during the download")
                    update_query = "UPDATE FilecoinDeals SET DownloadStatus='Error - file does not exist' WHERE Filename='" + row.Filename + "' AND DownloadPath='" + row.DownloadPath + "'"
            else:
                #file does exists
                update_query = "UPDATE FilecoinDeals SET DownloadStatus='Completed' WHERE Filename='" + row.Filename + "' AND DownloadPath='" + row.DownloadPath + "'"
                print(datetime.now(),"- File to download already exist in the folder")
            cursor.execute(update_query)
            cnxn.commit()
        else:
            print(datetime.now(),"- No files to download")
        
        print(datetime.now(),"- Sleeping for",config["deals"]["waitEndLoop"],"secs")
        time.sleep(config["deals"]["waitEndLoop"])

except pyodbc.Error as e:
    print(datetime.now(),"- Exception Error!")
    print(datetime.now(),e)