import json
import os
from kafka import KafkaConsumer

def start_alert_system():
    print("🚨 ICU Alert System Online. Monitoring 'icu-alerts' topic...")
    
    consumer = KafkaConsumer(
        'icu-alerts',
        bootstrap_servers=os.getenv('KAFKA_BROKER', 'localhost:9092'),
        auto_offset_reset='latest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    for msg in consumer:
        alert = msg.value
        
        RED = "\033[91m"
        BOLD = "\033[1m"
        RESET = "\033[0m"
        YELLOW = "\033[93m"
        
        print(f"{RED}{BOLD}" + "="*60)
        print(f"‼️  URGENT MEDICAL ALERT RECEIVED ‼️")
        print(f"{RESET}{YELLOW}Patient ID: {alert['subject_id']}")
        print(f"Condition:  {alert['metric']} avg is {round(alert['avg_value'], 1)}")
        print(f"Time:       {alert['window']['start']}")
        print(f"{RED}{BOLD}" + "="*60 + f"{RESET}\n")

if __name__ == "__main__":
    start_alert_system()
