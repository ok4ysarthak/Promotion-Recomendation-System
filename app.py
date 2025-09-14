import streamlit as st
import psycopg2
import pandas as pd
import altair as alt
from datetime import datetime

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="📦 Retail Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📦 Retail Analytics & Promotions Dashboard")
st.markdown("A modern, interactive dashboard for inventory, customer behavior, and promotions.")

# ---------------------------
# Database Connection
# ---------------------------
@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host='localhost',
        port=5432,
        database='retail',
        user='postgres',
        password='password'
    )

conn = get_connection()

# ---------------------------
# Load Data
# ---------------------------
@st.cache_data
def load_customer_events():
    query = """
    SELECT product_id, event_type, customer_id, COUNT(*) as count
    FROM customer_events
    GROUP BY product_id, event_type, customer_id
    ORDER BY product_id;
    """
    return pd.read_sql_query(query, conn)

@st.cache_data
def load_promotion_candidates(min_views=2):
    query = """
    SELECT 
        customer_id,
        product_id,
        SUM(CASE WHEN event_type='view' THEN 1 ELSE 0 END) AS views,
        SUM(CASE WHEN event_type='add_to_cart' THEN 1 ELSE 0 END) AS carts,
        SUM(CASE WHEN event_type='purchase' THEN 1 ELSE 0 END) AS purchases
    FROM customer_events
    GROUP BY customer_id, product_id;
    """
    df = pd.read_sql_query(query, conn)
    return df[(df["views"] >= min_views) & (df["purchases"] == 0)]

@st.cache_data
def load_active_promotions():
    query = """
    SELECT id, customer_id, product_id, discount_percent, created_at
    FROM promotions
    ORDER BY created_at DESC;
    """
    return pd.read_sql_query(query, conn)

def insert_promotion(customer_id, product_id, discount_percent=20):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO promotions (customer_id, product_id, discount_percent, created_at)
        VALUES (%s, %s, %s, %s)
    """, (customer_id, product_id, discount_percent, datetime.now()))
    conn.commit()
    cur.close()

# ---------------------------
# Sidebar Filters
# ---------------------------
st.sidebar.header("🔍 Filters")
event_filter = st.sidebar.multiselect(
    "Select Event Types",
    ["view", "add_to_cart", "purchase"],
    default=["view", "add_to_cart", "purchase"]
)
min_views = st.sidebar.slider("Minimum Views for Promotions", 1, 10, 2)

# ---------------------------
# Tabs Layout
# ---------------------------
tab1, tab2, tab3 = st.tabs(["📊 Events", "🎯 Promotions", "🎁 Active Promotions"])

# ---------------------------
# Tab 1: Events
# ---------------------------
with tab1:
    st.subheader("🗃️ Customer Events Overview")
    events_df = load_customer_events()
    events_df = events_df[events_df["event_type"].isin(event_filter)]
    st.dataframe(events_df, use_container_width=True)

    # KPIs
    total_views = events_df[events_df['event_type']=='view']['count'].sum()
    total_carts = events_df[events_df['event_type']=='add_to_cart']['count'].sum()
    total_purchases = events_df[events_df['event_type']=='purchase']['count'].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("👀 Total Views", total_views)
    col2.metric("🛒 Total Add-to-Carts", total_carts)
    col3.metric("💰 Total Purchases", total_purchases)

    # Chart: Events per Product
    st.subheader("📈 Events per Product")
    event_chart = alt.Chart(events_df).mark_bar().encode(
        x=alt.X("product_id:N", title="Product ID"),
        y=alt.Y("count:Q", title="Count"),
        color="event_type:N",
        tooltip=["product_id", "event_type", "count"]
    ).properties(height=400)
    st.altair_chart(event_chart, use_container_width=True)

# ---------------------------
# Tab 2: Promotion Candidates
# ---------------------------
with tab2:
    st.subheader("🎯 Suggested Promotions")
    promo_df = load_promotion_candidates(min_views=min_views)

    if promo_df.empty:
        st.success("✅ No customers need promotions right now.")
    else:
        st.dataframe(promo_df, use_container_width=True)
        st.info(f"Rules: Customers with ≥{min_views} views and 0 purchases are eligible.")

        # Select customer/product
        selected_row = st.selectbox(
            "Select Customer-Product to create promotion",
            promo_df.apply(lambda r: f"Customer {r['customer_id']} - Product {r['product_id']} (Views: {r['views']})", axis=1)
        )

        discount = st.slider("Discount Percent", 5, 50, 20, 5)

        if st.button("➕ Create Promotion"):
            row = promo_df.iloc[
                promo_df.apply(lambda r: f"Customer {r['customer_id']} - Product {r['product_id']} (Views: {r['views']})", axis=1) == selected_row
            ].iloc[0]
            insert_promotion(row["customer_id"], row["product_id"], discount)
            st.success(f"🎁 Promotion created for Customer {row['customer_id']} on Product {row['product_id']} with {discount}% discount!")

# ---------------------------
# Tab 3: Active Promotions
# ---------------------------
with tab3:
    st.subheader("🎁 Active Promotions")
    promotions_df = load_active_promotions()

    if promotions_df.empty:
        st.success("✅ No active promotions in database.")
    else:
        st.dataframe(promotions_df, use_container_width=True)

        st.subheader("🔥 Promotions by Product")
        promo_chart = alt.Chart(promotions_df).mark_bar(color="orange").encode(
            x=alt.X("product_id:N", title="Product ID"),
            y=alt.Y("count():Q", title="Number of Promotions"),
            tooltip=["product_id", "count()"]
        ).properties(height=400)
        st.altair_chart(promo_chart, use_container_width=True)
