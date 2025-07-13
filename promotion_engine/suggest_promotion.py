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
    SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END) AS views,
    SUM(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS add_to_carts,
    SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS purchases
FROM 
    customer_events
GROUP BY 
    customer_id, product_id;
"""

df = pd.read_sql_query(query, conn)

# Define promotion rule:
# Customers with many views but few purchases AND few add_to_carts
promotion_candidates = df[
    (df['views'] >= 2) |
    (df['purchases'] < 1) |
    (df['add_to_carts'] > 0)
]

print("\n🎯 🛍️ Personalized Promotion Suggestions 🛍️ 🎯\n")
if promotion_candidates.empty:
    print("\n✅ No promotions needed right now. Customers are buying or adding to cart!")
else:
    print("\n🎯 🛍️ Personalized Promotion Suggestions 🛍️ 🎯\n")
    cursor = conn.cursor()
    for _, row in promotion_candidates.iterrows():
        print(f"Offer 20% discount to Customer {row['customer_id']} on Product {row['product_id']} (Views: {row['views']}, Add-to-Carts: {row['add_to_carts']}, Purchases: {row['purchases']})")
        
        # Insert promotion into table
        cursor.execute(
            """
            INSERT INTO promotions (customer_id, product_id, discount_percent)
            VALUES (%s, %s, %s)
            """,
            (row['customer_id'], row['product_id'], '20%')
        )
    conn.commit()
    cursor.close()
    print("\n✅ Promotions saved to database!")

conn.close()
