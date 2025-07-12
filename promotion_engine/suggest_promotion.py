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
    customer_id,
    product_id,
    SUM(CASE WHEN event = 'view' THEN 1 ELSE 0 END) AS views,
    SUM(CASE WHEN event = 'purchase' THEN 1 ELSE 0 END) AS purchases
FROM 
    customer_events
GROUP BY 
    customer_id, product_id;
"""

df = pd.read_sql_query(query, conn)

# Define promotion rule: many views, few purchases
promotion_candidates = df[(df['views'] >= 3) & (df['purchases'] < 1)]

print("\n🎯 🛍️ Personalized Promotion Suggestions 🛍️ 🎯\n")
if promotion_candidates.empty:
    print("✅ No promotions needed right now. Customers are buying!")
else:
    for _, row in promotion_candidates.iterrows():
        print(f"Offer 20% discount to Customer {row['customer_id']} on Product {row['product_id']} (Views: {row['views']}, Purchases: {row['purchases']})")

conn.close()
