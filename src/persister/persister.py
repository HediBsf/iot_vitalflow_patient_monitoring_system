import json
import os
from kafka import KafkaConsumer
from pymongo import MongoClient

# This script bridges Kafka -> MongoDB so the Dashboard can query history
BOOTSTRAP_SERVERS = os.getenv('KAFKA_BROKER', 'localhost:9092')
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://root:root@localhost:27017/')
DB_NAME = 'medical_iot'

def run():
    print("💾 Starting MongoDB Persister Service...")
    
    # Connect to Mongo
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Consume Vitals and Alerts
    consumer = KafkaConsumer(
        'icu-vitals', 'icu-alerts',
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    for message in consumer:
        try:
            data = message.value

            # Normalize keys for Dashboard API compatibility
            if message.topic == 'icu-vitals':
                if 'charttime' in data:
                    data['timestamp'] = data.pop('charttime')
                if 'valuenum' in data:
                    data['value'] = data.pop('valuenum')
                if 'label' in data:
                    data['metric'] = data.pop('label')

            collection_name = 'raw_vitals' if message.topic == 'icu-vitals' else 'alerts'
            
            db[collection_name].insert_one(data)

            # Optimization: Maintain a separate patients collection
            if message.topic == 'icu-vitals':
                db['patients'].update_one(
                    {'subject_id': data['subject_id']},
                    {'$set': {'last_seen': data.get('timestamp') or data.get('charttime')}},
                    upsert=True
                )
            
            if message.topic == 'icu-alerts':
                print(f"\033[91m\033[1m[MONGO] ⚠️  ALERT SAVED: {data['metric']} for Patient {data['subject_id']}\033[0m")
            else:
                # Handle both 'metric' (old format) and 'label' (new format)
                metric_name = data.get('metric') or data.get('label')
                print(f"\033[92m[MONGO] ✅ Saved {metric_name} for Patient {data['subject_id']}\033[0m")
                
        except Exception as e:
            print(f"Error saving to DB: {e}")

if __name__ == "__main__":
    run()
