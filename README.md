# FieldGuard - Livestock Health Monitoring System

FieldGuard is a multi-phase, Docker-based project that simulates livestock health data, streams it through Apache Kafka and prepares the foundation for anomaly detection, APIs, and dashboards. Phase 1 focuses on setting up the infrastructure on Windows using Docker compose (Kafka, Zookeeper, MongoDB, and MySQL).

## Project Goals

- Provide an end-to-end, realistic data streaming/ backend project centered on livestock health. 
- Use **event-driven architecture** with Kafka as the message broker. 
- Store data in both **MongoDB** (for alerts/documents) and **MySQL** (for relational/job data).

---

## Phase 1 - Infrastructure (Windows + Docker)

### Services Provisioned

All services are started via `docker-compose.yml`:

- **Zookeeper** - Coordinates Kafka broker metadata. 
- **Kafka** - Message broker for livestock telemetry. 
    - Internal listener for Docker network. 
    - External listener for the Windows host. 
- **MongoDB** - NoSQL store for alerts and health events. 
- **MySQL** - Relational database for jobs, configurations, and aggregated data. 

---

## Repository Structure

```text 
fieldguard-project/
├── docker-compose/
|   └── docker-compose.yml     
├── livestock-simulator/
├── anomaly-detector/
├── fieldguard-backend/
├── README.md 
├── requirements.txt
├── .gitignore
```
---

## Docker Compose Overview

The `docker-compose.yml` file (in `docker-compose/`)
defines four services:

- `zookeeper`
- `kafka`
- `mongo`
- `mysql`

Key points: 

- Kafka is configured with **two advertised listeners**:
    - Internal: `PLAINTEXT://kafka:29092` (for containers on the Docker network)
    - External: `PLAINTEXT_HOST://host.docker.internal:9092` (for the Windows host).
- MongoDB is secured with root username and password
- MySQL is initialized with root password and a database (`fieldguard`).

---

## Getting Started

### Prerequisites 

- **Docker Desktop** installed and running on Windows. 
- **Git** version control and publishing project

### 1. Start the infrastructure

From a terminal in the `docker-compose` folder:

```powershell
cd .\docker-compose
docker-compose up -d
docker-compose ps
```
You should see all four containers 
- `zookeeper`
- `kafka`
- `mongo`
- `mysql` in `Up` state

If any service fails, check logs:

```powershell
# Check specific service
docker-compose logs kafka
docker-compose logs mysql
docker-compose logs mongo

# View all logs
docker-compose logs -f

# Stop all services
docker-compose down

# Remove everything and start fresh
docker-compose down -v
docker-compose up -d
```

### 2. Create Kafka Topic 

Create the topic used for livestock health streaming:

```powershell
# Enter Kafka container
docker exec -it kafka bash

# Inside container, create topic
kafka-topics --create --topic animal-health-stream \
  --bootstrap-server localhost:29092 \
  --partitions 3 \
  --replication-factor 1

# Verify topic created
kafka-topics --list --bootstrap-server localhost:29092
```
You should see:

```text
animal-health-stream
```

---

## Verifying Databases

### MongoDB

```powershell
# Connect to MongoDB
docker exec -it mongo mongosh -u admin -p admin123

# Inside MongoDB shell:
use fieldguard
db.health_alerts.insertOne({test: "hello"})
db.health_alerts.find()

# Exit
exit
```

### MySQL

```powershell
# Connect to MySQL
docker exec -it mysql mysql -u root -p

# Password: root123

# Inside MySQL:
SHOW DATABASES;
USE fieldguard;
SHOW TABLES;

# Exit
exit
```
---

## Future Phases (Planned)

- **Phase 2 - Livestock Simulator & Kafka Producer**
    - Python-based simulator generating heart rate, temperature, and location data for ~50 animals. 
    - Publishes messages to `animal-health-stream` topic in Kafka. 

- **Phase 3 - Anomaly Detection & Backend**
    - Anomaly detection service consuming from Kafka and writing alerts to MongoDB/MySQL. 
    - Spring Boot or similar backend exposing REST APIs. 

- **Phase 4 - Dashboard**
    - Web UI for viewing real-time alerts, historical data, and animal health status. 

---

## Status 

- ✅ Phase 1 -  Docker infrastructure and topic setup completed. 
- ⏳Phase 2 - Simulator and anomaly detection in progress. 
- ⏳Phase 3 - Backend/Service layer planned. 
- ⏳Phase 4 - Dashboard/UI planned. 

--- 