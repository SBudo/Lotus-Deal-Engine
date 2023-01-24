#!/usr/bin/python3

import pyodbc
import configparser
import time
from datetime import datetime
import requests
import json
import os
import subprocess



def convert_array_to_hash(arr, key_member):
    # Instantiate the hashtable
    hsh = {}

    if arr is not None:
        # Pass the array into the hashtable
        for obj in arr:
            print(obj[key_member])
            key=str(obj[key_member])
            hsh[key] = obj['Message']

    # return the new hashtable
    return hsh


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
        dealsFromBoost = json.loads(requests.post(config["boost"]["boostURL"], json={'query': "query{ deals(limit: 10000){ deals{ ID Message } } }"}).text)
        query = "SELECT * FROM FilecoinDeals WHERE DealStatus<>'Sealer: Proving' AND DealStatus not like 'Error%' and DealId is not null"
        cursor.execute(query)
        dealsfromDB=''
        dealsFromDB = cursor.fetchall()

        dealsFromBoostHash={}

        for obj in dealsFromBoost['data']['deals']['deals']:
            key=str(obj["ID"])
            dealsFromBoostHash[key] = obj['Message']


        for deal in dealsFromDB:
            message = dealsFromBoostHash[deal.DealId]
            message = message.replace("'"," ")

            msg = dealsFromBoostHash[deal.DealId]

            if message != deal.DealStatus:
                print(datetime.now(),"- Updating deal:",deal.DealId,"- Set Status to:",message)
                update_query = "UPDATE FilecoinDeals SET DealStatus='" + message + "' WHERE DealId='"+ deal.DealId +"'"
                cursor.execute(update_query)
                cnxn.commit()

        print(datetime.now(),"- Sleeping for",config["deals"]["waitEndLoop"],"secs")
        time.sleep(int(config["deals"]["waitEndLoop"]))

        config = configparser.ConfigParser()
        configFilePath = r'dealEngine.conf'
        config.read(configFilePath)

except pyodbc.Error as e:
    print(datetime.now(),"- Exception Error!")
    print(datetime.now(),e)
