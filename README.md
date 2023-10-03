# Traffic Steering (TS) xApp

The Traffic Steering (TS) xApp is designed to manage and optimize traffic flow within a cellular network. By analyzing metrics and adhering to specified policies, the xApp can make decisions on user equipment (UE) handovers between cells to ensure optimal network performance.

## Key Features

- **Interface Integration**: The xApp integrates with both E2 and A1 interfaces, allowing it to communicate directly with the RAN and gather essential metrics.
- **Dynamic Policy Handling**: The xApp can dynamically update its traffic steering policy based on updates received from the A1 interface.
- **Load Balancing**: One of the primary features is the ability to balance the load across cells. If a cell is detected as overloaded, the xApp can initiate handovers to redistribute UEs to underloaded cells.
- **Modular Design**: The xApp is designed with modularity in mind, allowing for easy expansion and integration of additional features in the future.
- **Supports external xApps to push policies via a Flask API.
- **UE Profiling: Assigns each UE a profile detailing its ID, hosting cell, priority, type, origin, signal strength, and throughput.
- **InfluxDB Integration: Stores metrics and policies in InfluxDB for historical data analysis and visualization (like Grafana).
- **Scalability: Designed to handle a growing number of UEs and cells, ensuring the xApp remains efficient as the network expands.

### Prerequisites
- Install OAIC, SRSRAN
- Add multiple UE and push traffic on the network

### Running the xApp

1. Clone the repository:
https://github.com/natanzi/TS-xApp
2. Run the xApp on by:
   python TS_xApp.py
3. Monitor the logs to observe the xApp's operations and decisions.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

