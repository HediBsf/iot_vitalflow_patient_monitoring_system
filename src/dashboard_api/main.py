from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime

app = FastAPI(title="ICU Dashboard API")

# CORS Configuration
# Allow requests from the frontend (localhost:3000)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://root:root@mongo:27017/')
client = MongoClient(MONGO_URI)
db = client['medical_iot']

# Models
class VitalReading(BaseModel):
    timestamp: str
    subject_id: int
    device_id: Optional[str] = None
    metric: str
    value: float
    unit: Optional[str] = None

class Alert(BaseModel):
    timestamp: str
    subject_id: int
    device_id: Optional[str] = None
    metric: str
    avg_value: float
    message: str

@app.get("/")
def read_root():
    return {"status": "online", "service": "ICU Dashboard API"}

@app.get("/patients")
def get_patients():
    """Get list of active patient IDs, sorted by last activity"""
    try:
        # Optimized: Query the patients collection instead of distinct scan
        # Sort by last_seen descending to show active patients first
        cursor = db.patients.find({}, {'subject_id': 1, '_id': 0}).sort('last_seen', -1)
        ids = [doc['subject_id'] for doc in cursor]
        return {"patients": ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vitals/{patient_id}")
def get_vitals(patient_id: int, metric: Optional[str] = None, limit: int = 100):
    """Get historical vitals for a patient"""
    query = {'subject_id': patient_id}
    if metric:
        query['metric'] = metric
        
    cursor = db.raw_vitals.find(query, {'_id': 0}).sort('timestamp', -1).limit(limit)
    data = list(cursor)
    # Reverse to get chronological order for graphs
    return data[::-1]

@app.get("/alerts")
def get_alerts(limit: int = 20):
    """Get recent critical alerts"""
    cursor = db.alerts.find({}, {'_id': 0}).sort('_id', -1).limit(limit)
    alerts = []
    for a in cursor:
        # Flatten structure for frontend convenience
        alerts.append({
            "timestamp": a.get('window', {}).get('start', datetime.now().isoformat()),
            "subject_id": a.get('subject_id'),
            "device_id": a.get('device_id'),
            "metric": a.get('metric'),
            "avg_value": a.get('avg_value'),
            "message": a.get('alert_message', 'Abnormal Value')
        })
    return alerts

@app.get("/latest/{patient_id}")
def get_latest_vitals(patient_id: int):
    """Get the absolute latest reading for each metric for a patient"""
    # Optimized: Use aggregation to get all latest metrics in one query
    pipeline = [
        {"$match": {"subject_id": patient_id}},
        {"$sort": {"timestamp": -1}},
        {"$group": {
            "_id": "$metric",
            "latest_value": {"$first": "$value"}
        }}
    ]
    
    try:
        cursor = db.raw_vitals.aggregate(pipeline)
        # Initialize with None for all expected metrics
        result = {m: None for m in ['HeartRate', 'O2Sat', 'RespRate', 'SysBP']}
        
        for doc in cursor:
            if doc['_id'] in result:
                result[doc['_id']] = doc['latest_value']
                
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
