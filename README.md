# Traffic Steering (TS) xApp

The Traffic Steering (TS) xApp is a robust tool developed specifically for the [OAIC O-RAN testbed](https://www.openaicellular.org/). It's designed to efficiently manage and optimize traffic flow within cellular networks. By leveraging real-time metrics and adhering to dynamic policies, this xApp facilitates informed decisions regarding user equipment (UE) handovers between cells, ensuring peak network performance.

## 🌟 Key Features

- **Interface Integration**: Seamless integration with both E2 and A1 interfaces for direct communication with the RAN and real-time metric acquisition.
  
- **Dynamic Policy Management**: Ability to adaptively update traffic steering policies based on real-time updates from the A1 interface.
  
- **Load Balancing**: Proactively detects overloaded cells and initiates handovers, redistributing UEs to ensure balanced load distribution across cells.
  
- **UE Profiling**: Comprehensive profiling for each UE, detailing attributes like ID, hosting cell, priority, type, origin, signal strength, and throughput.
  
- **InfluxDB Integration**: Efficiently logs metrics and policies in InfluxDB, setting the stage for in-depth historical data analysis and visualization tools like Grafana.
  
- **Flask API Support**: Facilitates external xApps to dynamically push or modify policies.
  
- **Scalability**: Architecturally designed to accommodate a growing number of UEs and cells, ensuring sustained efficiency as the network scales.
  
- **Modular Design**: Built with future expansion in mind, allowing for effortless integration of upcoming features.

## 🛠 Prerequisites

- Ensure [OAIC and SRSRAN](https://openaicellular.github.io/oaic/) are installed.
- Set up multiple UEs and initiate traffic flow within the network.

## 🚀 Getting Started

1. **Clone the Repository**:
https://github.com/natanzi/TS-xApp
2. Run the xApp on by:
   python TS_xApp.py
3. **Monitor**: Keep an eye on the logs to gain insights into the xApp's operations and decision-making processes.

## 🤝 Contributing

Your contributions can make this xApp even better! Feel free to fork the repository and submit a pull request with your enhancements.
ges.

