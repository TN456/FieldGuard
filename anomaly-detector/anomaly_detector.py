"""
Phase 3: detector.py
Real-time Anomaly Detection
"""

import json
import pickle
import numpy as np
import warnings
from kafka import KafkaConsumer

# Suppress sklearn warnings
warnings.filterwarnings("ignore")

# CONFIG
TOPIC = "animal-health-stream"
BROKER = "localhost:9092"
MODEL_FILE = "brain.pkl"

def load_brain():
    try:
        print(f"Loading AI Model from {MODEL_FILE}")
        with open(MODEL_FILE, "rb") as f:
            return pickle.load(f)
        
    except FileNotFoundError:
        print(f"Error: {MODEL_FILE} not found")
        print(" Please run 'trainer.py' first")
        exit(1)

def run_detector():
    model = load_brain()
    print(f"Model loaded. Connecting the feed")

    consumer = KafkaConsumer(
        TOPIC, 
        bootstrap_servers = [BROKER],
        value_deserializer = lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset = 'latest'
    )

    print(f"Detector is watching")

    try:
        for message in consumer:
            data = message.value

            # 1. Parse your JSON
            if 'metrics' not in data:
                continue

            animal_id = data['animal_id']
            m = data['metrics']

            # 2. Extract features
            features = [
                m['temperature'],
                m['heart_rate'],
                m['rumination_index']
            ]

            # 3. Extract your debug tag
            actual_state = data.get('_debug_state', 'UNKNOWN')

            # 4. Predict 
            # reshape(1, -1) is requires for a single prediction
            prediction = model.predict([features])[0]

            # -1 = Anomaly, 1 = Normal
            if prediction == -1:
                print(f" ANOMALY DETECTED for {animal_id}")
                print(f" Stats: Temperature: {m['temperature']}C | Heart Rate: {m['heart_rate']} | Rumination Index: {m['rumination_index']}")
                print(f" AI Prediction: SICK | Actual State: {actual_state}")
                print("-" * 50)
            else:
                # Add this 'else' block to see a heartbeat!
                print(".", end="", flush=True)

    except KeyboardInterrupt:
        print("\n Surveillance stopped.")

if __name__ == "__main__":
    run_detector()