#!/usr/bin/python3

import pyodbc
import configparser
import time
from datetime import datetime
import os
import subprocess


print(datetime.now(),"- Starting update deal status process")

print(datetime.now(),"- Reading configuration file")
# read the config file
config = configparser.ConfigParser()
configFilePath = r'dealEngine.conf'
config.read(configFilePath)

try:
    print(datetime.now(),"- Connecting to SQL database")
    cnxn = pyodbc.connect('DRIVER='+config["sql"]["driver"]+';SERVER=tcp:'+config["sql"]["server"]+';PORT=1433;DATABASE='+config["sql"]["database"]+';UID='+config["sql"]["username"]+';PWD='+config["sql"]["password"])
    cursor = cnxn.cursor()
    while 1:
        query = "SELECT TOP 1 * FROM FilecoinDeals WHERE DownloadStatus='Completed' and DealStatus='Sealer: Proving'"
        cursor.execute(query)
        file = cursor.fetchone()

        if file:
            cmd = "rm " + file.DownloadPath + file.Filename
            print(datetime.now().strftime("%d-%m-%Y %H:%M:%S"), "- Removing: ", cmd)
            os.system(cmd)
            update_query = "UPDATE FilecoinDeals SET DownloadStatus='FileRemoved' WHERE DealId='" + file.DealId + "' and Filename='" + file.Filename + "'"
            cursor.execute(update_query)
            cnxn.commit()

            print(datetime.now().strftime("%d-%m-%Y %H:%M:%S"), "- Updating database for deal: ", file.DealId)
        else:
            print(datetime.now().strftime("%d-%m-%Y %H:%M:%S"), "- No files to clean up")

        print(datetime.now(),"- Sleeping for",config["deals"]["waitEndLoop"],"secs")
        time.sleep(int(config["deals"]["waitEndLoop"]))

        config = configparser.ConfigParser()
        configFilePath = r'dealEngine.conf'
        config.read(configFilePath)

except pyodbc.Error as e:
    print(datetime.now(),"- Exception Error!")
    print(datetime.now(),e)