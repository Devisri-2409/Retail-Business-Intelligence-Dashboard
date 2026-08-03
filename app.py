import streamlit as st
import plotly.express as px
from datetime import date
from streamlit_autorefresh import st_autorefresh
from utils.db import run_query

# ------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------
st.set_page_config(
    page_title="Retail Business Intelligence Dashboard",
    layout="wide"
)

# ------------------------------------------
# AUTO REFRESH
# ------------------------------------------
st_autorefresh(
    interval=10000,
    key="dashboard_refresh"
)

# ------------------------------------------
# LOGO
# ------------------------------------------

st.image("assets/logo.png", width=110)
st.title(" Retail Business Intelligence Dashboard")
st.markdown("### Dynamic Sales Analytics using Python • Streamlit • MySQL")

st.divider()

# ------------------------------------------
# SIDEBAR
# ------------------------------------------

st.sidebar.header("🔍 Dashboard Filters")

start_date = st.sidebar.date_input(
    "Start Date",
    date(2024,1,1)
)

end_date = st.sidebar.date_input(
    "End Date",
    date.today()
)

category = st.sidebar.selectbox(
    "Product Category",
    [
        "All",
        "Electronics",
        "Furniture",
        "Accessories",
        "Stationery"
    ]
)

# ------------------------------------------
# KPI QUERIES
# ------------------------------------------

revenue = run_query("""
SELECT
SUM(total_amount) revenue
FROM sales;
""").iloc[0]["revenue"]

orders = run_query("""
SELECT
COUNT(*) orders
FROM sales;
""").iloc[0]["orders"]

customers = run_query("""
SELECT
COUNT(*) customers
FROM customers;
""").iloc[0]["customers"]

products = run_query("""
SELECT
COUNT(*) products
FROM products;
""").iloc[0]["products"]

avg_order = run_query("""
SELECT
AVG(total_amount) avg_order
FROM sales;
""").iloc[0]["avg_order"]

rating = run_query("""
SELECT
AVG(rate) rating
FROM customers;
""").iloc[0]["rating"]

# ------------------------------------------
# KPI CARDS
# ------------------------------------------

col1,col2,col3 = st.columns(3)

with col1:
    st.metric(
        "💰 Total Revenue",
        f"₹{revenue:,.0f}"
    )

with col2:
    st.metric(
        "🛒 Total Orders",
        f"{orders:,}"
    )

with col3:
    st.metric(
        "👥 Customers",
        f"{customers:,}"
    )

col4,col5,col6 = st.columns(3)

with col4:
    st.metric(
        "📦 Products",
        f"{products:,}"
    )

with col5:
    st.metric(
        "💳 Avg Order Value",
        f"₹{avg_order:,.0f}"
    )

with col6:
    st.metric(
        "⭐ Satisfaction",
        f"{rating:.1f}/5"
    )

st.divider()

# ==========================================
# MONTHLY SALES TREND
# ==========================================

monthly_sales = run_query("""
SELECT
    MONTH(sale_date) AS MonthNo,
    MONTHNAME(sale_date) AS Month,
    SUM(total_amount) AS Revenue
FROM sales
GROUP BY MonthNo, Month
ORDER BY MonthNo;
""")

fig1 = px.line(
    monthly_sales,
    x="Month",
    y="Revenue",
    markers=True,
    title="📈 Monthly Sales Trend"
)

fig1.update_layout(
    template="plotly_white",
    xaxis_title="Month",
    yaxis_title="Revenue (₹)"
)

# ==========================================
# REVENUE BY CATEGORY
# ==========================================

category_sales = run_query("""
SELECT
    p.category,
    SUM(s.total_amount) AS Revenue
FROM sales s
JOIN products p
ON s.product_id = p.product_id
GROUP BY p.category
ORDER BY Revenue DESC;
""")

fig2 = px.bar(
    category_sales,
    x="category",
    y="Revenue",
    color="Revenue",
    text_auto=True,
    title="📊 Revenue by Category"
)

fig2.update_layout(
    template="plotly_white",
    xaxis_title="Category",
    yaxis_title="Revenue (₹)"
)

# ==========================================
# DONUT CHART
# ==========================================

fig3 = px.pie(
    category_sales,
    names="category",
    values="Revenue",
    hole=0.55,
    title="🥧 Category-wise Revenue"
)

fig3.update_layout(template="plotly_white")

# ==========================================
# TOP SELLING PRODUCTS
# ==========================================

top_products = run_query("""
SELECT
    p.product_name,
    SUM(s.quantity) AS UnitsSold
FROM sales s
JOIN products p
ON s.product_id = p.product_id
GROUP BY p.product_name
ORDER BY UnitsSold DESC
LIMIT 10;
""")

fig4 = px.bar(
    top_products,
    x="UnitsSold",
    y="product_name",
    orientation="h",
    color="UnitsSold",
    text_auto=True,
    title="🏆 Top 10 Best Selling Products"
)

fig4.update_layout(
    template="plotly_white",
    yaxis_title="",
    xaxis_title="Units Sold"
)

# ==========================================
# QUARTERLY REVENUE
# ==========================================

quarter_sales = run_query("""
SELECT
    YEAR(sale_date) AS Year,
    CONCAT('Q', QUARTER(sale_date)) AS Quarter,
    SUM(total_amount) AS Revenue
FROM sales
GROUP BY
    YEAR(sale_date),
    QUARTER(sale_date),
    CONCAT('Q', QUARTER(sale_date))
ORDER BY
    YEAR(sale_date),
    QUARTER(sale_date);
""")

fig5 = px.bar(
    quarter_sales,
    x="Quarter",
    y="Revenue",
    color="Revenue",
    text_auto=True,
    title="📈 Quarterly Revenue"
)

fig5.update_layout(
    template="plotly_white",
    xaxis_title="Quarter",
    yaxis_title="Revenue (₹)"
)

# ==========================================
# DISPLAY CHARTS
# ==========================================

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.plotly_chart(fig4, use_container_width=True)

st.plotly_chart(
    fig5,
    use_container_width=True
)

st.divider()

# ==========================================================
# INVENTORY STATUS
# ==========================================================

inventory_status = run_query("""
SELECT
    status,
    COUNT(*) AS Total
FROM
(
    SELECT
        CASE
            WHEN stock = 0 THEN 'Out of Stock'
            WHEN stock <= 10 THEN 'Low Stock'
            ELSE 'In Stock'
        END AS status
    FROM products
) AS inventory
GROUP BY status;
""")

fig6 = px.pie(
    inventory_status,
    names="status",
    values="Total",
    
    title="📦 Inventory Status"
)

fig6.update_layout(template="plotly_white")

# ==========================================================
# CUSTOMER RATINGS
# ==========================================================

ratings = run_query("""
SELECT
rate
FROM customers;
""")

fig7 = px.histogram(
    ratings,
    x="rate",
    nbins=5,
    title="⭐ Customer Rating Distribution"
)

fig7.update_layout(
    template="plotly_white",
    xaxis_title="Rating",
    yaxis_title="Customers"
)

# ==========================================================
# DISPLAY BOTH CHARTS
# ==========================================================

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig6, use_container_width=True)

with col2:
    st.plotly_chart(fig7, use_container_width=True)

st.divider()

# ==========================================================
# LOW STOCK PRODUCTS
# ==========================================================

low_stock = run_query("""
SELECT
product_name,
category,
stock
FROM products
WHERE stock <=10
ORDER BY stock;
""")

st.subheader("⚠️ Low Stock Products")

st.dataframe(
    low_stock,
    use_container_width=True,
    hide_index=True
)

# ==========================================================
# RECENT SALES
# ==========================================================

recent_sales = run_query("""
SELECT
sale_id,
sale_date,
customer_id,
product_id,
quantity,
total_amount
FROM sales
ORDER BY sale_date DESC
LIMIT 10;
""")

st.subheader("🧾 Recent Sales")

st.dataframe(
    recent_sales,
    use_container_width=True,
    hide_index=True
)

# ==========================================================
# DOWNLOAD CSV
# ==========================================================

csv = recent_sales.to_csv(index=False)

st.download_button(
    label="📥 Download Sales Report",
    data=csv,
    file_name="Retail_Sales_Report.csv",
    mime="text/csv"
)

st.divider()

# ==========================================================
# BUSINESS INSIGHTS
# ==========================================================

st.header("💡 Business Insights")

# Best Selling Product
best_product = run_query("""
SELECT
    p.product_name,
    SUM(s.quantity) AS UnitsSold
FROM sales s
JOIN products p
ON s.product_id = p.product_id
GROUP BY p.product_name
ORDER BY UnitsSold DESC
LIMIT 1;
""")

# Highest Revenue Category
best_category = run_query("""
SELECT
    p.category,
    SUM(s.total_amount) AS Revenue
FROM sales s
JOIN products p
ON s.product_id = p.product_id
GROUP BY p.category
ORDER BY Revenue DESC
LIMIT 1;
""")

# Average Order Value
avg_order = run_query("""
SELECT
AVG(total_amount) AS AvgOrder
FROM sales;
""")

# Low Stock Count
low_stock_count = run_query("""
SELECT
COUNT(*) AS Total
FROM products
WHERE stock <= 10;
""")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.success(
        f"🏆 Best Seller\n\n{best_product.iloc[0]['product_name']}"
    )

with c2:
    st.info(
        f"💰 Top Category\n\n{best_category.iloc[0]['category']}"
    )

with c3:
    st.warning(
        f"💳 Avg Order\n\n₹{avg_order.iloc[0]['AvgOrder']:,.0f}"
    )

with c4:
    st.error(
        f"⚠ Low Stock\n\n{low_stock_count.iloc[0]['Total']} Products"
    )

st.divider()