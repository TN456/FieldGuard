# FieldGuard - Livestock Health Monitoring System

FieldGuard is a multi-phase, event-driven project that simulates livestock health data, streams it through Apache Kafka, and processes it for anomaly detection.

**Phase 1 & 2 are complete:** The project currently provisions a full data infrastructure via Docker and runs a realistic Python-based simulator that generates complex telemetry (GPS, heart rate, temperature) based on biological state machines.

## Project Goals

- **Realistic Simulation:** Move beyond random number generation by using state machines to simulate biological health events (Healthy -> Incubating -> Fever -> Recovery).
- **Event-Driven Architecture:** Utilize Apache Kafka as the central nervous system for data streaming.
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

---

## Repository Structure

```text 
fieldguard-project/
├── docker-compose/
|   └── docker-compose.yml     
├── livestock-simulator/
│   ├── animal_model.py        
│   ├── simulator.py           
├── anomaly-detector/
├── fieldguard-backend/
├── README.md 
├── requirements.txt
├── .gitignore
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
   Create a `requirements.txt` inside `livestock-simulator/` with the content `kafka-python`, then install:
   ```powershell
   cd ..\livestock-simulator
   pip install -r requirements.txt
   ```

2. **Run the Simulation:**
   ```powershell
   python simulator.py
   ```

**What to expect:**
- The console will show herd status (e.g., `[Iteration 10] Sending 50 messages | Sick: 2 | Low Batt: 0`).
- If an animal gets sick, you will see a console alert: `ALERT: Cow #12 is FEVER (Temp: 40.5°C)`.
- Data is now flowing into the Kafka topic `animal-health-stream`.

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

---