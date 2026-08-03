import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import run_query

st.set_page_config(page_title="OLAP Analysis", layout="wide")

st.title("📊 OLAP Analysis Dashboard")
# ======================================================
# Sidebar Filters
# ======================================================

categories = run_query("""
SELECT DISTINCT category
FROM products
ORDER BY category;
""")

months = run_query("""
SELECT DISTINCT MONTHNAME(sale_date) AS month,
       MONTH(sale_date) AS month_no
FROM sales
ORDER BY month_no;
""")

category = st.sidebar.selectbox(
    "Category",
    ["All"] + categories["category"].tolist()
)

month = st.sidebar.selectbox(
    "Month",
    ["All"] + months["month"].tolist()
)

# ======================================================
# 1. ROLL-UP
# ======================================================

st.subheader("🔼 Roll-up Analysis")

rollup = run_query("""
SELECT
YEAR(sale_date) AS Year,
SUM(total_amount) AS Revenue
FROM sales
GROUP BY YEAR(sale_date)
ORDER BY Year;
""")

fig1 = px.bar(
    rollup,
    x="Year",
    y="Revenue",
    color="Revenue",
    title="Year-wise Revenue"
)

# ======================================================
# 2. DRILL-DOWN
# ======================================================

st.subheader("🔽 Drill-down Analysis")

drill = run_query("""
SELECT
MONTHNAME(sale_date) AS Month,
MONTH(sale_date) AS MonthNo,
SUM(total_amount) AS Revenue
FROM sales
GROUP BY MONTH(sale_date), MONTHNAME(sale_date)
ORDER BY MonthNo;
""")

fig2 = px.line(
    drill,
    x="Month",
    y="Revenue",
    markers=True,
    title="Month-wise Revenue"
)
st.subheader(" Slice Analysis")

if category == "All":

    slice_query = """
    SELECT
    p.category,
    SUM(s.total_amount) AS Revenue
    FROM sales s
    JOIN products p
    ON s.product_id=p.product_id
    GROUP BY p.category;
    """

else:

    slice_query = f"""
    SELECT
    p.product_name,
    SUM(s.total_amount) AS Revenue
    FROM sales s
    JOIN products p
    ON s.product_id=p.product_id
    WHERE p.category='{category}'
    GROUP BY p.product_name;
    """

slice_df = run_query(slice_query)

fig3 = px.bar(
    slice_df,
    x=slice_df.columns[0],
    y="Revenue",
    color="Revenue",
    title="Slice Analysis"
)


col1, col2, col3 = st.columns(3)

with col1:
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.plotly_chart(fig2, use_container_width=True)

with col3:
    st.plotly_chart(fig3, use_container_width=True)
# ======================================================
# 4. DICE
# ======================================================

st.subheader("🎲 Dice Analysis")

query = """
SELECT
p.category,
MONTHNAME(s.sale_date) AS Month,
SUM(s.total_amount) AS Revenue
FROM sales s
JOIN products p
ON s.product_id=p.product_id
WHERE 1=1
"""

if category != "All":
    query += f" AND p.category='{category}'"

if month != "All":
    query += f" AND MONTHNAME(s.sale_date)='{month}'"

query += """
GROUP BY
p.category,
MONTH(s.sale_date),
MONTHNAME(s.sale_date)
ORDER BY
MONTH(s.sale_date);
"""

dice = run_query(query)

st.dataframe(
    dice,
    use_container_width=True,
    hide_index=True
)

# ======================================================
# 5. PIVOT TABLE
# ======================================================

st.subheader("🔄 Pivot Analysis")

pivot_source = run_query("""
SELECT
p.category,
MONTHNAME(s.sale_date) AS Month,
MONTH(s.sale_date) AS MonthNo,
s.total_amount
FROM sales s
JOIN products p
ON s.product_id=p.product_id
ORDER BY MonthNo;
""")

pivot = pivot_source.pivot_table(
    values="total_amount",
    index="category",
    columns="Month",
    aggfunc="sum",
    fill_value=0
)

st.dataframe(
    pivot,
    use_container_width=True
)

# ======================================================
# BUSINESS INSIGHTS
# ======================================================

st.subheader("💡 Business Insights")

best_product = run_query("""
SELECT
p.product_name,
SUM(s.quantity) AS UnitsSold
FROM sales s
JOIN products p
ON s.product_id=p.product_id
GROUP BY p.product_name
ORDER BY UnitsSold DESC
LIMIT 1;
""")

best_category = run_query("""
SELECT
p.category,
SUM(s.total_amount) AS Revenue
FROM sales s
JOIN products p
ON s.product_id=p.product_id
GROUP BY p.category
ORDER BY Revenue DESC
LIMIT 1;
""")

avg_order = run_query("""
SELECT ROUND(AVG(total_amount),2) AS avg_order
FROM sales;
""")

low_stock = run_query("""
SELECT COUNT(*) AS low_stock
FROM products
WHERE stock<=10;
""")

col1, col2 = st.columns(2)

with col1:

    st.success(
        f"🏆 Best Selling Product: "
        f"{best_product.iloc[0]['product_name']}"
    )

    st.info(
        f"💵 Average Order Value: "
        f"₹{avg_order.iloc[0]['avg_order']}"
    )

with col2:

    st.success(
        f"📦 Highest Revenue Category: "
        f"{best_category.iloc[0]['category']}"
    )

    st.warning(
        f"⚠ Low Stock Products: "
        f"{low_stock.iloc[0]['low_stock']}"
    )