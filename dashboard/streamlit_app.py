import streamlit as st
import psycopg2
import pandas as pd
import altair as alt

st.set_page_config(page_title="Retail Real-Time Dashboard", layout="wide")

st.title("📦 Retail Real-Time Dashboard")
st.subheader("Dynamic Inventory + Personalized Promotion Engine")

# ---------------------------
# Database connection
# ---------------------------
@st.cache_resource
def get_conn():
    return psycopg2.connect(
        host='localhost',
        port=5432,
        database='retail',
        user='postgres',
        password='password'
    )

conn = get_conn()

# ---------------------------
# Inventory Query
# ---------------------------
inventory_query = """
SELECT 
    product_id,
    event_type,
    COUNT(*) AS count
FROM 
    customer_events
GROUP BY 
    product_id, event_type
ORDER BY 
    product_id, event_type;
"""
inventory_df = pd.read_sql_query(inventory_query, conn)

st.header("🗃️ Inventory Dashboard")
st.dataframe(inventory_df)

# ---------------------------
# Top Viewed Products (Bar Chart)
# ---------------------------
view_df = inventory_df[inventory_df['event_type'] == 'view']
if not view_df.empty:
    view_chart = alt.Chart(view_df).mark_bar(color="skyblue").encode(
        x=alt.X('product_id:N', title='Product ID', sort='-y'),
        y=alt.Y('count:Q', title='Views'),
        tooltip=['product_id', 'count']
    ).properties(title="👀 Top Viewed Products")
    st.altair_chart(view_chart, use_container_width=True)
else:
    st.info("No product view events found in data.")

# ---------------------------
# Promotion Candidates Query
# ---------------------------
promotion_query = """
SELECT 
    customer_id,
    product_id,
    SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END) AS views,
    SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS purchases
FROM 
    customer_events
GROUP BY 
    customer_id, product_id;
"""
promo_df = pd.read_sql_query(promotion_query, conn)

# Rule: >= 3 views but < 1 purchase → needs promotion
promo_candidates = promo_df[(promo_df['views'] >= 3) & (promo_df['purchases'] < 1)]

st.header("🎯 Personalized Promotion Suggestions")
if promo_candidates.empty:
    st.success("✅ No promotions needed right now. Customers are buying!")
else:
    st.dataframe(promo_candidates)
    for _, row in promo_candidates.iterrows():
        st.warning(
            f"Offer 20% discount to Customer {row['customer_id']} on Product {row['product_id']} "
            f"(Views: {row['views']}, Purchases: {row['purchases']})"
        )

# ---------------------------
# Active Promotions (Table + Chart)
# ---------------------------
st.header("🎁 Active Promotions")
try:
    promotions_df = pd.read_sql_query("SELECT * FROM promotions ORDER BY created_at DESC", conn)

    if promotions_df.empty:
        st.success("✅ No active promotions.")
    else:
        st.dataframe(promotions_df)

        # ✅ Graph: Count of promotions per product
        promo_chart = alt.Chart(promotions_df).mark_bar(color="orange").encode(
            x=alt.X('product_id:N', title='Product ID'),
            y=alt.Y('count():Q', title='Active Promotions'),
            tooltip=['product_id', 'count()']
        ).properties(title="🔥 Promotions by Product")
        st.altair_chart(promo_chart, use_container_width=True)

except Exception as e:
    st.error(f"Could not load promotions table: {e}")
