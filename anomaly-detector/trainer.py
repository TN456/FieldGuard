"""
Phase 3: trainer.py
"""

import json
import pickle
import pandas as pd
from kafka import KafkaConsumer
from sklearn.ensemble import IsolationForest

# CONFIG
TOPIC = "animal-health-stream"
BROKER = "localhost:9092"
TARGET_COUNT = 30000

print(f"Starting AI Trainer...")
print(f"Target: {TARGET_COUNT} messages")

# Connect to Kafka
consumer = KafkaConsumer(
    TOPIC, 
    bootstrap_servers = [BROKER],
    value_deserializer = lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset = 'latest'
)

data_buffer = []

print("Collecting training data")

try: 
    for message in consumer:
        data = message.value

        if 'metrics' in data:
            m = data['metrics']

            # We select the 3 biological features 
            features = [
                m['temperature'],
                m['heart_rate'],
                m['rumination_index']
            ] 
            data_buffer.append(features)

        # Progress Bar
        if len(data_buffer) % 500 == 0:
            print(f"Collected {len(data_buffer)} / {TARGET_COUNT}")

        # Stop when we hit the target
        if len(data_buffer) >= TARGET_COUNT:
            break
    
    print("Collection complete")

    # 2. Train the Brain
    print("Training Isolation Forest")

    # Create a DataFrame with clear column names
    df = pd.DataFrame(data_buffer, columns = ['temperature', 'heart_rate', 'rumination'])

    # Train the model (contamination = 0.01 means ~1% anomalies expected)
    model = IsolationForest(n_estimators = 100, contamination = 0.01, random_state = 42)
    model.fit(df)

    # 3. Save the Brain
    with open("brain.pkl", "wb") as f:
        pickle.dump(model, f)

    print("Model saved to 'brain.pkl'")

except Exception as e:
    print("f Error: {e}")
