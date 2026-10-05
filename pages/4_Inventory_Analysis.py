import streamlit as st
import plotly.express as px
from utils.db import run_query

st.set_page_config(page_title="Inventory Analysis", layout="wide")

st.title("📦 Inventory Analysis")

# ============================================
# Inventory KPIs
# ============================================

total_products = run_query("""
SELECT COUNT(*) AS total_products
FROM products;
""")

total_stock = run_query("""
SELECT COALESCE(SUM(stock), 0) AS total_stock
FROM products;
""")

low_stock = run_query("""
SELECT COUNT(*) AS low_stock
FROM products
WHERE stock <= 10;
""")

out_stock = run_query("""
SELECT COUNT(*) AS out_stock
FROM products
WHERE stock = 0;
""")

tot_prod_val = int(total_products.iloc[0]["total_products"]) if not total_products.empty else 0
tot_stock_val = int(total_stock.iloc[0]["total_stock"]) if not total_stock.empty else 0
low_stock_val = int(low_stock.iloc[0]["low_stock"]) if not low_stock.empty else 0
out_stock_val = int(out_stock.iloc[0]["out_stock"]) if not out_stock.empty else 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📦 Products",
        tot_prod_val
    )

with col2:
    st.metric(
        "📊 Total Stock",
        tot_stock_val
    )

with col3:
    st.metric(
        "⚠ Low Stock",
        low_stock_val
    )

with col4:
    st.metric(
        "❌ Out of Stock",
        out_stock_val
    )

st.divider()

# ============================================
# Inventory Status
# ============================================

status = run_query("""
SELECT
    status,
    COUNT(*) AS "Total"
FROM
(
    SELECT
        CASE
            WHEN stock = 0 THEN 'Out of Stock'
            WHEN stock <= 10 THEN 'Low Stock'
            ELSE 'In Stock'
        END AS status
    FROM products
) AS inventory_status
GROUP BY status;
""")

fig1 = px.pie(
    status,
    names="status",
    values="Total",
    hole=0.45,
    title="Inventory Status"
)

# ============================================
# Stock by Category
# ============================================

category = run_query("""
SELECT
    category,
    COALESCE(SUM(stock), 0) AS "Stock"
FROM products
GROUP BY category
ORDER BY "Stock" DESC;
""")

fig2 = px.bar(
    category,
    x="category",
    y="Stock",
    color="Stock",
    title="Stock by Category"
)

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ============================================
# Low Stock Products
# ============================================

low_stock_products = run_query("""
SELECT
product_id,
product_name,
category,
stock
FROM products
WHERE stock <= 10
ORDER BY stock;
""")

st.subheader("⚠ Low Stock Products")

st.dataframe(
    low_stock_products,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ============================================
# Complete Inventory
# ============================================

inventory = run_query("""
SELECT
product_id,
product_name,
category,
price,
stock
FROM products
ORDER BY category;
""")

st.subheader("📋 Inventory Summary")

st.dataframe(
    inventory,
    use_container_width=True,
    hide_index=True
)

# ============================================
# Download Inventory Report
# ============================================

csv = inventory.to_csv(index=False)

st.download_button(
    "📥 Download Inventory Report",
    csv,
    "inventory_report.csv",
    "text/csv"
)