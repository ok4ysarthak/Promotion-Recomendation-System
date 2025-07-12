import json
import psycopg2
from kafka import KafkaConsumer
from datetime import datetime

# PostgreSQL connection setup
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='retail',
    user='postgres',
    password='password'
)
cursor = conn.cursor()

# Kafka consumer setup
consumer = KafkaConsumer(
    'customer_events',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='retail-consumer-group'
)

print("✅ Listening to Kafka topic 'customer_events'...")

for message in consumer:
    event = message.value
    print("✅ Received:", event)

    # Parse timestamp from ISO string
    event_time = datetime.fromisoformat(event["timestamp"])

    # Insert into Postgres
    cursor.execute(
        """
        INSERT INTO customer_events (customer_id, event, product_id, store_id, event_timestamp)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            event['customer_id'],
            event['event'],
            event['product_id'],
            event['store_id'],
            event_time
        )
    )
    conn.commit()
    print("✅ Inserted into PostgreSQL.")
