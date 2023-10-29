#data_sync.py
# this function will synchronize data from the kpimon xApp to ts-xapp InfluxDB
from influxdb import DataFrameClient
import pandas as pd
import logging

class DATABASE(object):
    def __init__(self, dbname, host='localhost', port='8086'):
        self.data = None
        self.client = DataFrameClient(host, port, dbname)

    def create_database(self):
        self.client.create_database(self.dbname)

    def read_data(self, meas, limit=1):
        self.client.switch_database('kpimon')
        result = self.client.query('select * from ' + meas + ' limit ' + str(limit))
        if len(result[meas]) != 0:
            self.data = result[meas]
        else:
            raise Exception('Data not found for ' + meas + ' vnf')

    def write_data(self, df, meas='actions'):
        self.client.write_points(df, meas)

def sync_kpimon_data():
    try:
        # Specify your InfluxDB settings
        dbname = 'ts-xapp_influxdb'  # Replace with your desired database name
        host = 'influxdb-host'  # Replace with your InfluxDB host
        port = '8086'

        # Create an instance of the DATABASE class
        db = DATABASE(dbname, host, port)

        # Create the database if it doesn't exist
        db.create_database()

        # Read data from kpimon xApp
        db.read_data("ricIndication_UeMetrics")
        ue_data_kpimon = db.data
        
        if not ue_data_kpimon.empty:
            # Write the data to your InfluxDB
            db.write_data(ue_data_kpimon, 'my_measurement')
        else:
            logging.info("No data received from KPImon. No data will be written to InfluxDB.")

        logging.info("Data synchronization with kpimon successful")
    except Exception as e:
        logging.error(f"Error syncing data with kpimon: {str(e)}")

