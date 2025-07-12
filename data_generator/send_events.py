import time
import json
import random
from datetime import datetime
from kafka import KafkaProducer

# Connect to local Kafka broker
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

customers = ['C1', 'C2', 'C3']
products = ['P1', 'P2', 'P3']
stores = ['S1', 'S2']

def generate_event():
    return {
        "customer_id": random.choice(customers),
        "event": random.choice(["view", "purchase"]),
        "product_id": random.choice(products),
        "store_id": random.choice(stores),
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    topic_name = 'customer_events'
    print(f"Sending events to topic: {topic_name}")

    while True:
        event = generate_event()
        producer.send(topic_name, event)
        print("Sent:", event)
        time.sleep(1)
