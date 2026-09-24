# ICU Monitoring System - IoT Project

## Overview
This project is a real-time ICU monitoring system that processes vital signs from IoT devices, detects anomalies using Apache Spark Structured Streaming, and visualizes the data on a real-time dashboard.

## Architecture
- **Gateway**: Simulates IoT devices sending Heart Rate and O2 Saturation data to Kafka.
- **Kafka**: Message broker for decoupling services (`icu-vitals` and `icu-alerts` topics).
- **Spark Streaming**: Processes raw data, calculates windowed averages, and detects critical conditions (e.g., HR > 100, O2 < 95).
- **MongoDB**: Stores raw vitals and generated alerts.
- **Persister**: Consumes data from Kafka and saves it to MongoDB.
- **Dashboard API**: FastAPI backend serving data to the frontend.
- **Dashboard UI**: Next.js frontend for real-time visualization.

## Prerequisites
- Docker & Docker Compose

## Installation & Operation

1. **Start the Infrastructure**
   ```bash
   docker-compose up --build
   ```

2. **Access the Dashboard**
   Open [http://localhost:3000](http://localhost:3000) in your browser.

3. **Verify Components**
   - **Gateway**: Check logs of `python-apps` container.
   - **Spark**: Check logs of `spark-master` or submit the job manually if needed.
   - **Database**: Connect to MongoDB on port 27017.

## Dataset Description
The system generates synthetic data simulating:
- **Heart Rate**: Normal range 60-100 bpm.
- **O2 Saturation**: Normal range 95-100%.
- **Anomalies**: Random spikes introduced to test alert logic.

## Project Structure
- `src/gateway`: Data generator.
- `src/spark`: Stream processing logic.
- `src/persister`: Database ingestion.
- `src/dashboard_api`: Backend API.
- `src/dashboard_ui`: Frontend application.
