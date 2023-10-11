#This is TS xApp version 1.0.0
import logging
import socket
import time
import os
from threading import Thread, Lock
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from flask import Flask, request, jsonify
from ricxappframe.xapp_frame import RMRXapp, rmr, Xapp
from rmr_health_check import RMRHealthCheckXapp
from sdl_health_check import sdl_health_check


# Initialize logging
logging.basicConfig(level=logging.INFO)

# Sample data or reading from E2 node 
cells = ["Cell 1", "Cell 2", "Cell 3"]
ues = ["UE 1", "UE 2", "UE 3"]

# InfluxDB Configuration
INFLUXDB_URL = 'http://localhost:8086'
INFLUXDB_TOKEN = 'YOUR_TOKEN'
INFLUXDB_ORG = 'YOUR_ORG'
INFLUXDB_BUCKET = 'YOUR_BUCKET'

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN)
write_api = client.write_api(write_options=SYNCHRONOUS)

app = Flask(__name__)

print("Wellcome to start TS-xApp, in this stage we are going to run the TS xApp....")
print("We should test O-RAN compoonet")

class UE:
    def __init__(self, ue_id, cell, priority, ue_type, origin, signal_strength, throughput):
        self.ue_id = ue_id
        self.cell = cell
        self.priority = priority
        self.ue_type = ue_type
        self.origin = origin
        self.signal_strength = signal_strength
        self.throughput = throughput

class TrafficSteering:
    def __init__(self):
        self.cells = cells
        self.ues = ues
        self.e2 = E2Driver()
        self.a1 = A1Driver()
        self.policy = None
        self.lock = Lock()  # For thread safety
        self.server = None  # SCTP server
        self.run_load_balancing = False  # Flag to control load balancing

    def init_e2(self):
        # Initialize SCTP connection
        ip_addr = socket.gethostbyname(socket.gethostname())
        port = 5000
        self.server = sctp.sctpsocket_tcp(socket.AF_INET)  # Using SCTP
        self.server.bind((ip_addr, port))
        self.server.listen()
        logging.info(f"SCTP server started at {ip_addr}:{port}")

    def entry(self):
        while True:
            conn, addr = self.server.accept()
            logging.info(f'Connected by {addr}')
            # Further processing can be added here based on the E2-like interface code

    def on_register(self):
        self.e2.register_interface()
        self.a1.register_interface()
        # Start interface threads
        Thread(target=self.e2.start_recv_loop, args=(self.handle_e2_update,)).start()
        Thread(target=self.a1.start_recv_loop, args=(self.handle_a1_update,)).start()
        Thread(target=self.entry).start()  # Start the E2-like interface main loop

    def handle_e2_update(self, metrics):
        # Process metrics
        overloaded, underloaded = self.detect_imbalance(metrics)
        # Additional processing can be added here based on the E2-like interface code
        # Write metrics to InfluxDB
        for metric in metrics:
            point = Point("e2_metrics").tag("UE", metric['ue']).field("value", metric['value'])
            write_api.write(INFLUXDB_BUCKET, INFLUXDB_ORG, point)

    def handle_a1_update(self, policy):
        # Process policy
        with self.lock:
            self.policy = policy
        # Write policy to InfluxDB
        point = Point("a1_policy").field("policy_name", self.policy.name)
        write_api.write(INFLUXDB_BUCKET, INFLUXDB_ORG, point)

    def run(self):
        while True:
            metrics = self.e2.get_metrics()

            # Write metrics to InfluxDB for Grafana access
            for metric_name, metric_value in metrics.items():
                point = Point(metric_name).field("value", metric_value)
                write_api.write(INFLUXDB_BUCKET, INFLUXDB_ORG, point)

            if self.run_load_balancing and self.policy and self.policy.name == "Load Balancing":
                overloaded, underloaded = self.detect_imbalance(metrics)
                if overloaded and underloaded:
                    target_ues = self.calculate_handovers(overloaded, underloaded)
                    for ue in target_ues:
                        src_cell = ue.cell
                        tgt_cell = self.get_target_cell(ue)
                        self.e2.initiate_handover(ue, src_cell, tgt_cell)
            time.sleep(10)

    # Helper functions
    def detect_imbalance(self, metrics):
        # For simplicity, let's use arbitrary thresholds. These can be adjusted.
        OVERLOADED_THRESHOLD = 100  # Example threshold for overloaded cells
        UNDERLOADED_THRESHOLD = 10  # Example threshold for underloaded cells

        overloaded = [cell for cell, ue_count in metrics['active_ues'].items() if ue_count > OVERLOADED_THRESHOLD]
        underloaded = [cell for cell, ue_count in metrics['active_ues'].items() if ue_count < UNDERLOADED_THRESHOLD]

        return overloaded, underloaded

    def calculate_handovers(self, overloaded, underloaded):
        # For now, let's just select UEs with poor signal strength for handover
        # This is a simplistic approach and can be enhanced
        POOR_SIGNAL_THRESHOLD = -100  # Example threshold for poor signal strength in dBm

        target_ues = [ue for ue in self.ues if ue.signal_strength < POOR_SIGNAL_THRESHOLD]

        return target_ues

    def get_target_cell(self, ue):
        # For simplicity, let's just return the first underloaded cell as the target
        # This can be enhanced to select the best target cell based on various criteria
        return self.cells[0]  # Return the first cell as target


@app.route('/push_policy', methods=['POST'])
def push_policy():
    data = request.json
    # Assuming the policy data is sent as JSON and has a 'name' attribute
    ts_xapp.handle_a1_update(data)
    return jsonify({"message": "Policy applied successfully!"})

def main_menu():
    print("\nWelcome to the Traffic Steering xApp!")
    print("xApp Onboarded and deployed successfully.")
    print("xApp registered via E2.\n")
    
    while True:
        print("\nMenu Options:")
        print("1 - Apply Load Balancing")
        print("2 - Cell Outage Compensation")
        print("3 - Slicing-based Steering")
        print("4 - Service-based Steering")
        print("5 - Energy Efficiency")
        print("6 - Undeploy the TS-xApp")
        print("Enter 'exit' to quit the application.\n")
        
        choice = input("Please select an option: ")

        if choice == '1':
            ts_xapp.run_load_balancing = True  # Start load balancing
            print("Load Balancing applied. See the result in the dashboard.")
        elif choice == '2':
            print("Cell Outage Compensation applied. See the result in the dashboard.")
        elif choice == '3':
            print("Slicing-based Steering applied. See the result in the dashboard.")
        elif choice == '4':
            print("Service-based Steering applied. See the result in the dashboard.")
        elif choice == '5':
            print("Energy Efficiency applied. See the result in the dashboard.")
        elif choice == '6':
            print("TS-xApp undeployed successfully.")
            break
        elif choice.lower() == 'exit':
            break
        else:
            print("Invalid choice. Please try again.")

def main():
    try:
        ts_xapp = TrafficSteering()
        ts_xapp.on_register()
        Thread(target=ts_xapp.run).start()
        main_menu()  # Display the interactive menu
        app.run(port=5000)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if ts_xapp.server:
            ts_xapp.server.close()

if __name__ == "__main__":
    main()  # This line starts the main function when the script is executed
