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
SELECT DISTINCT 
    TRIM(TO_CHAR(sale_date, 'Month')) AS month,
    EXTRACT(MONTH FROM sale_date)::INTEGER AS month_no
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
    EXTRACT(YEAR FROM sale_date)::INTEGER AS "Year",
    COALESCE(SUM(total_amount), 0) AS "Revenue"
FROM sales
GROUP BY EXTRACT(YEAR FROM sale_date)
ORDER BY "Year";
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
    TRIM(TO_CHAR(sale_date, 'Month')) AS "Month",
    EXTRACT(MONTH FROM sale_date)::INTEGER AS "MonthNo",
    COALESCE(SUM(total_amount), 0) AS "Revenue"
FROM sales
GROUP BY EXTRACT(MONTH FROM sale_date), TRIM(TO_CHAR(sale_date, 'Month'))
ORDER BY "MonthNo";
""")

fig2 = px.line(
    drill,
    x="Month",
    y="Revenue",
    markers=True,
    title="Month-wise Revenue"
)

# ======================================================
# 3. SLICE
# ======================================================

st.subheader("🍕 Slice Analysis")

if category == "All":

    slice_query = """
    SELECT
        p.category,
        COALESCE(SUM(s.total_amount), 0) AS "Revenue"
    FROM sales s
    JOIN products p
    ON s.product_id = p.product_id
    GROUP BY p.category;
    """
    slice_params = None

else:

    slice_query = """
    SELECT
        p.product_name,
        COALESCE(SUM(s.total_amount), 0) AS "Revenue"
    FROM sales s
    JOIN products p
    ON s.product_id = p.product_id
    WHERE p.category = :category
    GROUP BY p.product_name;
    """
    slice_params = {"category": category}

slice_df = run_query(slice_query, params=slice_params)

fig3 = px.bar(
    slice_df,
    x=slice_df.columns[0] if not slice_df.empty else None,
    y="Revenue" if not slice_df.empty else None,
    color="Revenue" if not slice_df.empty else None,
    title=f"Slice Analysis - {category}"
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

conditions = ["1=1"]
dice_params = {}

if category != "All":
    conditions.append("p.category = :category")
    dice_params["category"] = category

if month != "All":
    conditions.append("TRIM(TO_CHAR(s.sale_date, 'Month')) = :month")
    dice_params["month"] = month

where_clause = " AND ".join(conditions)

query = f"""
SELECT
    p.category,
    TRIM(TO_CHAR(s.sale_date, 'Month')) AS "Month",
    COALESCE(SUM(s.total_amount), 0) AS "Revenue"
FROM sales s
JOIN products p
ON s.product_id = p.product_id
WHERE {where_clause}
GROUP BY
    p.category,
    EXTRACT(MONTH FROM s.sale_date),
    TRIM(TO_CHAR(s.sale_date, 'Month'))
ORDER BY
    EXTRACT(MONTH FROM s.sale_date);
"""

dice = run_query(query, params=dice_params)

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
    TRIM(TO_CHAR(s.sale_date, 'Month')) AS "Month",
    EXTRACT(MONTH FROM s.sale_date)::INTEGER AS "MonthNo",
    s.total_amount
FROM sales s
JOIN products p
ON s.product_id = p.product_id
ORDER BY "MonthNo";
""")

if not pivot_source.empty:
    pivot = pivot_source.pivot_table(
        values="total_amount",
        index="category",
        columns="Month",
        aggfunc="sum",
        fill_value=0
    )
else:
    pivot = pd.DataFrame()

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
    COALESCE(SUM(s.quantity), 0) AS "UnitsSold"
FROM sales s
JOIN products p
ON s.product_id = p.product_id
GROUP BY p.product_name
ORDER BY "UnitsSold" DESC
LIMIT 1;
""")

best_category = run_query("""
SELECT
    p.category,
    COALESCE(SUM(s.total_amount), 0) AS "Revenue"
FROM sales s
JOIN products p
ON s.product_id = p.product_id
GROUP BY p.category
ORDER BY "Revenue" DESC
LIMIT 1;
""")

avg_order = run_query("""
SELECT ROUND(COALESCE(AVG(total_amount), 0)::NUMERIC, 2) AS "avg_order"
FROM sales;
""")

low_stock = run_query("""
SELECT COUNT(*) AS "low_stock"
FROM products
WHERE stock <= 10;
""")

col1, col2 = st.columns(2)

best_p_name = best_product.iloc[0]["product_name"] if not best_product.empty else "N/A"
best_c_name = best_category.iloc[0]["category"] if not best_category.empty else "N/A"
avg_o_val = float(avg_order.iloc[0]["avg_order"]) if not avg_order.empty else 0.0
low_s_val = int(low_stock.iloc[0]["low_stock"]) if not low_stock.empty else 0

with col1:

    st.success(
        f"🏆 Best Selling Product: {best_p_name}"
    )

    st.info(
        f"💵 Average Order Value: ₹{avg_o_val:,.2f}"
    )

with col2:

    st.success(
        f"📦 Highest Revenue Category: {best_c_name}"
    )

    st.warning(
        f"⚠ Low Stock Products: {low_s_val}"
    )