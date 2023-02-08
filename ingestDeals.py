#!/usr/bin/python3

import pyodbc
import configparser
import time
from datetime import datetime
import requests
import json
import os
import subprocess

print (datetime.now(),"- Starting...")


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
        print (datetime.now(),"- Getting the deals list from Boost")
        deals = json.loads(requests.post(config["lotus"]["boostURL"], json={'query': "query{ deals(limit: 3000){ deals{ ID Message } } }"}).text)

        totalReadyToPublish = 0
        totalPreCommit1 = 0
        totalAddingToSector = 0
        totalAwaitingPublish = 0
        totalAnnouncing = 0

        for x in deals["data"]["deals"]["deals"]:
            if x['Message'] == 'Ready to Publish':
                totalReadyToPublish = totalReadyToPublish + 1
            if x['Message'] == 'Sealer: PreCommit1':
                totalPreCommit1 = totalPreCommit1 + 1
            if x['Message'] == 'Adding To Sector':
                totalAddingToSector = totalAddingToSector + 1
            if x['Message'] == 'Awaiting Publish Confirmation':
                totalAwaitingPublish = totalAwaitingPublish + 1
            if x['Message'] == 'Announcing':
                totalAnnouncing = totalAnnouncing + 1
                        

        print (datetime.now(),"- Total deals Ready To Publish (RTP):",totalReadyToPublish)

        if totalReadyToPublish < int(config["deals"]["readyToPublishThreshold"]):
            print (datetime.now(),"- Number of deals Ready To Publish is lower than the threshold. Current RTP deals:",totalReadyToPublish,"- Threshold:",config["deals"]["readyToPublishThreshold"])
            query = "SELECT TOP 1 * from FilecoinDeals WHERE MinerID='" + config['lotus']['minerId'] + "' and DealStatus='Awaiting Offline Data Import' and DealId is not null and DownloadStatus='Completed' and DatasetName='" + config['deals']['currentDatasetName'] + "' ORDER BY Id"
            cursor.execute(query)
            dealRow = cursor.fetchone()

            if len(dealRow) == 0:
                print (datetime.now(),"- No deals found in primary Dataset. Looking in Secondary Dataset")
                query = "SELECT TOP 1 * from FilecoinDeals WHERE MinerID='" + config['lotus']['minerId'] + "' and DealStatus='Awaiting Offline Data Import' and DealId is not null and DownloadStatus='Completed' and DatasetName='" + config['deals']['secondaryDatasetName'] + "' ORDER BY Id"
                cursor.execute(query)
                dealRow = cursor.fetchone()

            if len(dealRow) > 0:
                print (datetime.now(),"- Found a deal to import:",dealRow.DealId)
                fileToImport = dealRow.ImportPath + dealRow.Filename
                if os.path.exists(fileToImport) == True:
                    importCMD = "boostd import-data " + dealRow.DealId + " " + fileToImport
                    print (datetime.now(),"- Starting the import. Deal Id:",dealRow.DealId,", File:",fileToImport)
                    subprocess.Popen(["boostd", "import-data", dealRow.DealId,fileToImport]).wait()
                    queryCommP = "SELECT TOP 1 * from FilecoinDeals WHERE MinerID='" + config['lotus']['minerId'] + "' and DealId='" + dealRow.DealId + "'"
                    cursor.execute(queryCommP)
                    commPResult = cursor.fetchone()
                    while commPResult.DealStatus == "Awaiting Offline Data Import":
                        print (datetime.now(),"- Waiting for CommP to finish. Current deal status:",commPResult.DealStatus)
                        time.sleep(int(config["deals"]["waitCommP"]))
                        cursor.execute(queryCommP)
                        commPResult = cursor.fetchone()
                    if commPResult.DealStatus == "Ready To Publish":
                        print (datetime.now(),"- CommP successful")
                    else:
                        print (datetime.now(),"- Error during CommP")
                        #To do: add alert to Slack
                else:
                    print (datetime.now(),"- File to import not found! ",fileToImport)
                    downloadQuery = "UPDATE FilecoinDeals SET DownloadStatus='NotStarted' WHERE MinerID='" + config['lotus']['minerId'] + "' and DealID='" + dealRow.DealId + "' AND filename='" + dealRow.Filename + "'"
                    cursor.execute(downloadQuery)
                    cnxn.commit()
            else:
                if totalReadyToPublish > 0:
                    totalJobs = totalPreCommit1 + totalAddingToSector + totalAwaitingPublish + totalAnnouncing
                    if totalJobs < config['deals']['numberOfJobsThreshold']:
                        print (datetime.now(),"- Triggering Publish message. Number of jobs lower or equal than threshold. Current Jobs:",totalJobs,", threshold configured:",config['deals']['numberOfJobsThreshold'])
                        requests.post(config["lotus"]["boostURL"], json={'query': "mutation { dealPublishNow }"})
                    else:
                        print (datetime.now(),"- Too many jobs in the queue, waiting! Current Jobs:",totalJobs,", threshold configured:",config['deals']['numberOfJobsThreshold'])
        else:
            totalJobs = totalPreCommit1 + totalAddingToSector + totalAwaitingPublish + totalAnnouncing
            if totalJobs < config['deals']['numberOfJobsThreshold']:
                print (datetime.now(),"- Triggering Publish message. Number of jobs lower or equal than threshold. Current Jobs:",totalJobs,", threshold configured:",config['deals']['numberOfJobsThreshold'])
                requests.post(config["lotus"]["boostURL"], json={'query': "mutation { dealPublishNow }"})
            else:
                print (datetime.now(),"- Too many jobs in the queue, waiting! Current Jobs:",totalJobs,", threshold configured:",config['deals']['numberOfJobsThreshold'])

        print(datetime.now(),"- Sleeping for",config["deals"]["waitEndLoop"],"secs")
        time.sleep(int(config["deals"]["waitEndLoop"]))

        config = configparser.ConfigParser()
        configFilePath = r'dealEngine.conf'
        config.read(configFilePath)

except pyodbc.Error as e:
    print(datetime.now(),"- Exception Error!")
    print(datetime.now(),e)
