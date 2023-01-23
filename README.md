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
The scripts have been tested on Ubuntu 20.04.<br>
The installation steps below have to be done on all servers where the scripts will be running.<br>
You can run the scripts on separate servers or one server, but it is recommended to run the "ingestDeals.py" on the boost node<br>

Install python3:<br>

```
sudo apt-get update
sudo apt-get install python3.8 
```
<br>
Install the SQL ODBC Connector:<br>

```
sudo su
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list

exit
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18 
```
<br>
Install python modules (pyodbc and requests):<br>

``` 
pip install pyodbc
pip install requests
```
<br>
Install aria2c only on the server where the download script will be running:<br>

```
sudo apt install aria2
```
<br>

Clone the repo: <br>
```
git clone https://github.com/SBudo/Lotus-Deal-Engine
```

## Usage
