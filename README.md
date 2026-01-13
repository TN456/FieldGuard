# FieldGuard - Livestock Health Monitoring System

FieldGuard is a multi-phase, event-driven project that simulates livestock health data, streams it through Apache Kafka, and processes it for anomaly detection.

**Phases 1, 2 & 3 are complete:** The project currently provisions a full data infrastructure via Docker, runs a realistic Python-based simulator, and utilizes **Unsupervised Machine Learning** to detect health anomalies in real-time without hardcoded rules.

## Project Goals

- **Realistic Simulation:** Move beyond random number generation by using state machines to simulate biological health events (Healthy -> Incubating -> Fever -> Recovery).
- **Event-Driven Architecture:** Utilize Apache Kafka as the central nervous system for data streaming.
- **Intelligent Analysis:** Use **Isolation Forest** algorithms to learn "normal" herd behavior and automatically flag deviations (sickness/distress).
- **Hybrid Storage:** Store data in **MongoDB** (document store for alerts/logs) and **MySQL** (relational data for farm management).

---

## Architecture & Phases

### Phase 1 - Infrastructure (Docker)
Infrastructure is managed via `docker-compose.yml` on Windows/Linux:
- **Zookeeper:** Manages Kafka broker metadata.
- **Kafka:** Handles the `animal-health-stream` topic. Configured with dual listeners (Internal for Docker, External for Host).
- **MongoDB:** NoSQL storage for incoming health alerts.
- **MySQL:** Relational storage for farm configurations.

### Phase 2 - Livestock Simulator (Python)
A sophisticated producer service that:
- Simulates a herd of **50 animals** (Cows, Sheep, Goats).
- Uses **Geofencing logic** to constrain movement within simulated pastures.
- Implements a **Health State Machine** where animals can contract illnesses, exhibit symptoms (fever, low rumination), and recover or deteriorate.
- Streams JSON telemetry to Kafka in real-time.

### Phase 3 - Anomaly Detection (Machine Learning)
A real-time consumer service using **Scikit-Learn**:
- **Trainer (`trainer.py`):** Listens to the stream for a set period to learn the statistical baseline of a "healthy" herd. Generates a serialized model (`brain.pkl`).
- **Detector (`detector.py`):** Loads the trained model and performs real-time inference on live Kafka messages.
- **Algorithm:** Uses **Isolation Forest** (Unsupervised Learning) to detect outliers in multi-dimensional data (Temperature vs Heart Rate vs Rumination).

---

## Repository Structure

```text
fieldguard-project/
├── requirements.txt           # Python dependencies (Main)
├── docker-compose/
│   └── docker-compose.yml     # Infrastructure definitions
├── livestock-simulator/
│   ├── animal_model.py        # OO Logic: State machine, GPS movement, Biology
│   ├── simulator.py           # Main Loop: Kafka Producer & Herd Management
├── anomaly-detector/
│   ├── trainer.py             # ML Training Script (Run Once)
│   ├── detector.py            # Real-time Inference Script (Run Continuously)
│   └── brain.pkl              # Trained Model (Generated file)
├── fieldguard-backend/        # (Planned Phase 4)
├── README.md
└── .gitignore
```

---

## Getting Started

### Prerequisites
- **Docker Desktop**
- **Python 3.8+**
- **Git**

### 1. Start the Infrastructure (Phase 1)
From the `docker-compose` folder:

```powershell
cd .\docker-compose
docker-compose up -d
```
Verify containers are running:
```powershell
docker-compose ps
```

### 2. Setup Kafka Topic
Create the topic that the simulator will write to:

```powershell
# Enter Kafka container
docker exec -it kafka bash

# Create topic
kafka-topics --create --topic animal-health-stream \
  --bootstrap-server localhost:29092 \
  --partitions 3 \
  --replication-factor 1

# Exit container
exit
```

### 3. Run the Simulator (Phase 2)
The simulator runs locally on the host machine and talks to Kafka on port `9092`.

1. **Install Dependencies:**
   Since you are currently in `docker-compose/`, go back to the root to find `requirements.txt`:
   ```powershell
   cd ..
   pip install -r requirements.txt
   ```

2. **Run the Simulation:**
   Navigate into the simulator folder and start:
   ```powershell
   cd livestock-simulator
   python simulator.py
   ```
   *Leave this terminal running. It acts as the data source.*

### 4. Run Anomaly Detection (Phase 3)
Open a **new terminal** to run the Machine Learning components.

1. **Install ML Dependencies:**
   ```powershell
   pip install scikit-learn pandas numpy
   ```

2. **Train the Brain (First Run Only):**
   Ensure the Simulator is running. Run the trainer to learn what "Healthy" looks like.
   ```powershell
   cd ..\anomaly-detector
   python trainer.py
   ```
   *Wait for it to collect 30,000 messages and save `brain.pkl`.*

3. **Start the Detector:**
   Once trained, start the real-time monitoring:
   ```powershell
   python detector.py
   ```

**What to expect:**
- The detector will print dots `......` indicating healthy animals.
- If the Simulator generates a sick animal (e.g., `ALERT: Cow #12 is FEVER`), the Detector will immediately interrupt and print:
  `🚨 ANOMALY DETECTED for Cow #12 | AI Prediction: SICK`.

---

## Data Model
The simulator generates realistic JSON packets. Example payload:

```json
{
    "animal_id": 12,
    "timestamp": "2026-01-08T11:05:00+00:00",
    "location": {
        "lat": 35.00023,
        "lon": -97.00045
    },
    "metrics": {
        "temperature": 39.2,
        "heart_rate": 78,
        "rumination_index": 45,
        "battery_level": 98.5
    },
    "_debug_state": "HEALTHY"
}
```

### Simulation Logic Details
- **Movement:** Animals perform a "random walk" but are nudged back if they cross the geofence radius of their assigned pasture.
- **Vitals:**
  - **Healthy:** metrics drift naturally around species baselines.
  - **Fever:** Temperature spikes, heart rate increases, rumination drops.
  - **Battery:** Slowly drains; simulates IoT hardware constraints.

---

## Verifying Data Flow

To ensure Phase 2 is talking to Phase 1, you can run a console consumer inside the Docker container:

```powershell
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:29092 \
  --topic animal-health-stream \
  --from-beginning
```
You should see a stream of JSON data appearing in real-time.

---

## Status & Roadmap

| Phase | Component | Tech Stack | Status |
| :--- | :--- | :--- | :--- |
| **1** | **Infrastructure** | Docker, Zookeeper, Kafka, MySQL, Mongo | ✅ **Completed** |
| **2** | **Simulator** | Python, OOP, State Machines, Kafka Producer | ✅ **Completed** |
| **3** | **Anomaly Detection** | Python, Scikit-Learn (Isolation Forest) | ✅ **Completed** |
| **4** | **Backend Service** | Spring Boot, Kafka Consumer, JPA | ⏳ Next Step |
| **5** | **Dashboard** | React/Angular or Streamlit | ⏳ Planned |