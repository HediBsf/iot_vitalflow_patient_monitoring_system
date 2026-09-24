import time
import json
import random
import threading
import pandas as pd
from kafka import KafkaProducer
import os

# Configuration
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
TOPIC = 'icu-vitals'
CSV_PATH = '/app/data/chartevents.csv.gz'

# Shared Producer (KafkaProducer is thread-safe)
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

class PatientSimulator(threading.Thread):
    def __init__(self, patient_id):
        threading.Thread.__init__(self)
        self.patient_id = patient_id
        self.daemon = True  # Kill thread if main program exits
        self.running = True
        
        # Generate a static Device ID for this patient's monitor
        self.device_id = f"DEV-{random.randint(1000, 9999)}-{self.patient_id}"
        
        # Initial State
        self.state = {
            'HeartRate': random.randint(60, 100),
            'O2Sat': random.randint(95, 100),
            'RespRate': random.randint(12, 20),
            'SysBP': random.randint(110, 130),
            'DiasBP': random.randint(70, 90)
        }
        
        # Define Units
        self.units = {
            'HeartRate': 'bpm',
            'O2Sat': '%',
            'RespRate': 'bpm',
            'SysBP': 'mmHg',
            'DiasBP': 'mmHg'
        }

    def run(self):
        """The life of a single patient thread"""
        print(f"🟢 Patient {self.patient_id} monitor started on Device {self.device_id}.")
        
        while self.running:
            # 1. Update State (Random Walk)
            self.update_vitals()
            
            # 2. Send Data
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            for metric, value in self.state.items():
                msg = {
                    'subject_id': int(self.patient_id),
                    'device_id': self.device_id,
                    'charttime': timestamp,
                    'valuenum': float(value),
                    'label': metric,
                    'unit': self.units.get(metric, '')
                }
                producer.send(TOPIC, msg)
                
                # Visual Log (Only print HeartRate to keep terminal readable)
                if metric == 'HeartRate':
                    # Color coding for better demo visualization
                    color = "\033[96m" # Cyan
                    if value > 100: color = "\033[91m" # Red for high HR
                    reset = "\033[0m"
                    print(f"{color}[{timestamp}] Patient {self.patient_id} | ❤️ {value} bpm{reset}")
            
            # 3. Sleep a random amount (0.8s to 1.2s) to desynchronize threads
            # This makes the logs look very realistic and "messy"
            time.sleep(random.uniform(0.8, 1.2))

    def update_vitals(self):
        # Logic to walk values up/down or trigger anomaly
        if random.random() < 0.02: # 2% chance of anomaly
            self.state['HeartRate'] = random.randint(110, 150)
            self.state['O2Sat'] = random.randint(85, 92)
        else:
            # Normal fluctuation
            self.state['HeartRate'] += random.randint(-2, 2)
            self.state['O2Sat'] += random.randint(-1, 1)
            
            # Clamp values
            self.state['HeartRate'] = max(50, min(160, self.state['HeartRate']))
            self.state['O2Sat'] = max(80, min(100, self.state['O2Sat']))

def get_real_patient_ids(limit=50):
    """Extracts real IDs from the CSV to make the demo authentic"""
    if os.path.exists(CSV_PATH):
        print(f"📂 Reading IDs from {CSV_PATH}...")
        try:
            # Increased scan to 100,000 rows to find more unique patients (approx 33)
            df = pd.read_csv(CSV_PATH, compression='gzip', nrows=100000)
            return df['subject_id'].unique()[:limit]
        except Exception as e:
            print(f"⚠️ Error reading CSV: {e}. Using fallback IDs.")
            return [10000000 + i for i in range(limit)]
    else:
        # Fallback if file missing
        print("⚠️ CSV not found. Using fallback IDs.")
        return [10000000 + i for i in range(limit)]

def main():
    # 1. Get Patients
    patient_ids = get_real_patient_ids(limit=50) # Simulate up to 50 concurrent patients
    print(f"🚀 Starting Concurrent Simulation for {len(patient_ids)} patients...")
    
    threads = []
    
    # 2. Spawn a Thread for each Patient
    for pid in patient_ids:
        t = PatientSimulator(pid)
        threads.append(t)
        t.start()
        time.sleep(0.1) # Stagger start slightly

    # 3. Keep Main Thread Alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Stopping simulation...")

if __name__ == "__main__":
    # Wait for Kafka
    time.sleep(5)
    main()
