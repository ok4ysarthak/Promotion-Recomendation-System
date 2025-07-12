import psycopg2
import pandas as pd

# Connect to Postgres
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='retail',
    user='postgres',
    password='password'
)

query = """
SELECT 
    store_id,
    product_id,
    event,
    COUNT(*) as count
FROM 
    customer_events
GROUP BY 
    store_id, product_id, event
ORDER BY 
    store_id, product_id;
"""

df = pd.read_sql_query(query, conn)

print("\n📦 📊 Dynamic Inventory Dashboard 📊 📦\n")
print(df)

conn.close()
