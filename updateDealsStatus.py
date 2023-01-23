#!/usr/bin/python3

import pyodbc
import configparser
import time
from datetime import datetime
import requests
import json
import os
import subprocess


print(datetime.now(),"- Starting update deal status process")

print(datetime.now(),"- Reading configuration file")
# read the config file
config = configparser.ConfigParser()
configFilePath = r'dealEngine.conf'
config.read(configFilePath)
