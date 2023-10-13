# Traffic Steering (TS) xApp

The Traffic Steering (TS) xApp is a specialized tool designed for the [OAIC O-RAN testbed](https://www.openaicellular.org/). Its primary purpose is to efficiently manage and optimize traffic flow within cellular networks. By utilizing real-time metrics and adhering to dynamic policies, this xApp ensures optimal network performance by making informed decisions about user equipment (UE) handovers between cells. 
This xApp can be onboarded through the xApp Onboarder.

## 🌟 Key Features

- **Interface Integration**: 
  - E2 Interface  interactions for direct RAN communication and real-time metric acquisition.
- **Health check operations**: 
  - RMR and SDL Health check.
- **KPIMON xApp integration**:
-  KPIMON xApp is in charge of collecting RAN metrics and writing to InfluxDB.
- **Dynamic Policy Management**:
-  Adapts traffic steering policies in response to real-time updates from the A1 interface.
- **Load Balancing**:
-  Identifies overloaded cells and redistributes UEs to achieve balanced load across cells.
- **UE Profiling**:
-  Provides detailed profiling for each UE, capturing attributes such as ID, cell, priority, type, origin, signal strength, and throughput.
- **InfluxDB Integration**:
-  Logs metrics and policies in InfluxDB, paving the way for historical data analysis and visualization using tools like Grafana.
- **Flask API Support**:
-  Allows external xApps to dynamically push or modify policies, with support for ML/RL/DRL plugins.
- **Scalability**: Built to accommodate a growing number of UEs and cells, ensuring consistent efficiency.
- **Modular Design**:
-  Prepared for effortless integration of future features.

## 🛠 Prerequisites

- Ensure [OAIC and SRSRAN](https://openaicellular.github.io/oaic/) are installed.
- Set up multiple UEs and initiate network traffic flow.
- Running KPImon xApp

## 🚀 Getting Started
Start with root permission and:

1. Execute the RIC installation:
   ```bash
   ./ricinstallation.sh
2. Start SRSRAN:
   ```bash
   ./srsrandeploy.sh
3. Execute KPImon-xApp:
   ```bash
   ./kpimon.sh
4. Go to TS-xApp folder and :
   ```bash
   ./ts-xapp.sh

## 🤝 Contributing
We welcome your contributions to enhance this xApp! Feel free to fork the repository and submit a pull request with your improvements.
