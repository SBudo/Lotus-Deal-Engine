# Lotus-Deal-Engine
Deal engine for the lotus and boost implementation of the filecoin chain.
The purpose of the engine is to manage the download, ingestion and file clean up of offline deals made through Boost.
The engine has been written in Python scripts with a SQL database backend

There are four scripts running on a loop (along with a configuration file):
- Ingest-Deals.py: to import and publish offline deals
- Update-DealsStatus.py: to update the SQL database based on the deal status in boost
- Download-Files.py: to donwload missing files from the deal provider
- Cleanup-Files.py: to clean up existing files after the deal has been sealed

## Installation

## Usage
