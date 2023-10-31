#data_sync.py
# this function will synchronize data from the kpimon xApp
#data_sync.py
from influxdb import DataFrameClient
import logging

class DATABASE(object):
    def __init__(self, dbname, host='localhost', port='8086'):
        self.dbname = dbname  # Define the database name as an instance variable
        self.client = DataFrameClient(host, port, dbname)

def sync_kpimon_data():
    print("sync_kpimon_data endpoint called")
    try:
        # Specify your InfluxDB settings
        dbname = 'kpimon'  # Connect to the 'kpimon' database
        host = 'ricplt-influxdb.ricplt.svc.cluster.local'  # Updated to use the full DNS name within the Kubernetes cluster
        port = '8086'

        # Create an instance of the DATABASE class
        db = DATABASE(dbname, host, port)

        # Log a message
        logging.info(f"Connected to the '{dbname}' database in InfluxDB at {host}:{port}")
    except Exception as e:
        logging.error(f"Error connecting to the '{dbname}' database in InfluxDB: {str(e)}")
