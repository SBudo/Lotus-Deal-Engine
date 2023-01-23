# Lotus-Deal-Engine

!!! Work in progress !!!

Deal engine for the lotus and boost implementation of the filecoin chain.
The purpose of the engine is to manage the download, ingestion and file clean up of offline deals made through Boost.
The engine has been written in Python scripts with a SQL database backend

There are four scripts running on a loop (along with a configuration file):
- ingestDeals.py: to import and publish offline deals
- updateDealsStatus.py: to update the SQL database based on the deal status in boost
- downloadFiles.py: to donwload missing files from the deal provider
- cleanupFiles.py: to clean up existing files after the deal has been sealed

## Installation
The scripts have been tested on Ubuntu 20.04.
### prerequisites
Install python3 <br>
` sudo apt-get update ` <br>
` sudo apt-get install python3.8 ` <br><br>
Install the SQL ODBC Connector <br>
``` sudo su
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list

exit
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18 ``` <br>


## Usage
