#data_sync.py
# this function will synchronize data from the kpimon xApp to ts-xapp InfluxDB
from influxdb import DataFrameClient
import pandas as pd
import logging

class DATABASE(object):
    def __init__(self, dbname, host='localhost', port='8087'):
        self.dbname = dbname  # Define the database name as an instance variable
        self.data = None
        self.client = DataFrameClient(host, port, dbname)
    
    def create_database(self):
        # Check if the database exists before trying to create it
        if not {'name': self.dbname} in self.client.get_list_database():
            self.client.create_database(self.dbname)
            logging.info(f"Database {self.dbname} created.")
        else:
            logging.info(f"Database {self.dbname} already exists.")
    
    def read_data(self, meas, limit=1):
        self.client.switch_database('kpimon')
        query = f'SELECT * FROM {meas} LIMIT {limit}'
        result = self.client.query(query)
        if meas in result and not result[meas].empty:
            self.data = result[meas]
        else:
            logging.warning(f'Data not found for {meas}. No data will be synchronized.')
            self.data = pd.DataFrame()  # Return an empty DataFrame

    def write_data(self, df, meas='actions'):
        if not df.empty:
            self.client.switch_database(self.dbname)  # Ensure you are writing to the correct database
            self.client.write_points(df, meas)
            logging.info(f"Data written to measurement {meas} in database {self.dbname}.")
        else:
            logging.info("No data to write.")


def sync_kpimon_data():
    try:
        # Specify your InfluxDB settings
        dbname = 'ts-xapp_influxdb'  # Replace with your desired database name
        host = 'influxdb-host'  # Replace with your InfluxDB host
        port = '8087'

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

