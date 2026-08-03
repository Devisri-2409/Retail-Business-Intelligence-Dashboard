import streamlit as st
import plotly.express as px
from utils.db import run_query

st.set_page_config(page_title="Customer Analysis", layout="wide")

st.title("👥 Customer Analysis")

# ============================================
# Customer KPIs
# ============================================

total_customers = run_query("""
SELECT COUNT(*) AS total_customers
FROM customers;
""")

avg_rating = run_query("""
SELECT ROUND(AVG(rate),2) AS avg_rating
FROM customers;
""")

repeat_customers = run_query("""
SELECT COUNT(*) AS repeat_customers
FROM (
    SELECT customer_id
    FROM sales
    GROUP BY customer_id
    HAVING COUNT(*) > 1
) t;
""")

avg_order = run_query("""
SELECT ROUND(AVG(total_amount),2) AS avg_order
FROM sales;
""")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "👥 Customers",
        int(total_customers.iloc[0]["total_customers"])
    )

with col2:
    st.metric(
        "⭐ Avg Rating",
        avg_rating.iloc[0]["avg_rating"]
    )

with col3:
    st.metric(
        "🔁 Repeat Customers",
        int(repeat_customers.iloc[0]["repeat_customers"])
    )

with col4:
    st.metric(
        "💵 Avg Order Value",
        f"₹{avg_order.iloc[0]['avg_order']}"
    )

st.divider()

# ============================================
# Customer Rating Distribution
# ============================================

ratings = run_query("""
SELECT
rate,
COUNT(*) AS Total
FROM customers
GROUP BY rate
ORDER BY rate;
""")

fig1 = px.bar(
    ratings,
    x="rate",
    y="Total",
    color="Total",
    title="Customer Rating Distribution"
)

# ============================================
# Top Customers
# ============================================

top_customers = run_query("""
SELECT
c.customer_name,
SUM(s.total_amount) AS TotalSpent
FROM sales s
JOIN customers c
ON s.customer_id=c.customer_id
GROUP BY c.customer_name
ORDER BY TotalSpent DESC
LIMIT 10;
""")

fig2 = px.bar(
    top_customers,
    x="TotalSpent",
    y="customer_name",
    orientation="h",
    color="TotalSpent",
    title="Top 10 Customers by Spending"
)

fig2.update_layout(
    yaxis={"categoryorder":"total ascending"}
)

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ============================================
# Customer Purchase Details
# ============================================

customer_details = run_query("""
SELECT
c.customer_name,
COUNT(s.sale_id) AS Orders,
SUM(s.total_amount) AS TotalSpent,
ROUND(AVG(s.total_amount),2) AS AvgPurchase
FROM customers c
LEFT JOIN sales s
ON c.customer_id=s.customer_id
GROUP BY c.customer_name
ORDER BY TotalSpent DESC;
""")

st.subheader("📋 Customer Purchase Summary")

st.dataframe(
    customer_details,
    use_container_width=True,
    hide_index=True
)

st.download_button(
    "📥 Download Customer Report",
    customer_details.to_csv(index=False),
    "customer_report.csv",
    "text/csv"
)