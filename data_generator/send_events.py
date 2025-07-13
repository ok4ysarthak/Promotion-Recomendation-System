import pandas as pd
from kafka import KafkaProducer
import json
import time

# Load your real CSV
df = pd.read_csv('C:/Users/91704/OneDrive/Desktop/Workspace/retail-realtime-project/data/ecommerce_clickstream_transactions.csv')

# These should exactly match your CSV headers
EVENT_COLUMN = 'EventType'
PRODUCT_COLUMN = 'ProductID'
USER_COLUMN = 'UserID'
TIME_COLUMN = 'Timestamp'

# ✅ Normalize event column (lowercase, strip spaces)
df[EVENT_COLUMN] = df[EVENT_COLUMN].str.lower().str.strip()

# ✅ Map your raw events to simplified ones
EVENT_MAPPING = {
    'page_view': 'view',
    'product_view': 'view',
    'add_to_cart': 'add_to_cart',
    'purchase': 'purchase'
}

# ✅ Keep only useful events
df = df[df[EVENT_COLUMN].isin(EVENT_MAPPING.keys())]

# ✅ Map to unified event labels
df['event_type'] = df[EVENT_COLUMN].map(EVENT_MAPPING)

# ✅ Drop incomplete rows
df = df.dropna(subset=[USER_COLUMN, PRODUCT_COLUMN, TIME_COLUMN])

# ✅ Kafka setup
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# ✅ Produce to Kafka
for _, row in df.iterrows():
    event = {
        "customer_id": str(row[USER_COLUMN]),
        "product_id": str(row[PRODUCT_COLUMN]),
        "event_type": row['event_type'],
        "timestamp": row[TIME_COLUMN]
    }
    producer.send("customer_events", value=event)
    print("✅ Sent:", event)
    time.sleep(0.2)
