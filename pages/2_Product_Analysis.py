import streamlit as st
import plotly.express as px
from utils.db import run_query

st.set_page_config(page_title="Product Analysis", layout="wide")

st.title("📦 Product Analysis")

# ---------------------------------------------------
# Category Filter (OLAP Slice)
# ---------------------------------------------------

categories = run_query("""
SELECT DISTINCT category
FROM products
ORDER BY category;
""")

category_list = ["All"] + categories["category"].tolist()

selected_category = st.sidebar.selectbox(
    "Select Category",
    category_list
)

# ---------------------------------------------------
# Category-wise Revenue
# ---------------------------------------------------

if selected_category == "All":

    revenue_query = """
    SELECT
        p.category,
        SUM(s.total_amount) AS Revenue
    FROM sales s
    JOIN products p
        ON s.product_id = p.product_id
    GROUP BY p.category
    ORDER BY Revenue DESC;
    """

    product_query = """
    SELECT
        p.product_name,
        SUM(s.quantity) AS UnitsSold
    FROM sales s
    JOIN products p
        ON s.product_id = p.product_id
    GROUP BY p.product_name
    ORDER BY UnitsSold DESC
    LIMIT 10;
    """

else:

    revenue_query = f"""
    SELECT
        p.category,
        SUM(s.total_amount) AS Revenue
    FROM sales s
    JOIN products p
        ON s.product_id = p.product_id
    WHERE p.category='{selected_category}'
    GROUP BY p.category;
    """

    product_query = f"""
    SELECT
        p.product_name,
        SUM(s.quantity) AS UnitsSold
    FROM sales s
    JOIN products p
        ON s.product_id = p.product_id
    WHERE p.category='{selected_category}'
    GROUP BY p.product_name
    ORDER BY UnitsSold DESC
    LIMIT 10;
    """

category_sales = run_query(revenue_query)

top_products = run_query(product_query)

# ---------------------------------------------------
# Charts
# ---------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    fig1 = px.pie(
        category_sales,
        names="category",
        values="Revenue",
        hole=0.45,
        title="Category-wise Revenue"
    )

    st.plotly_chart(fig1, use_container_width=True)

with col2:

    fig2 = px.bar(
        top_products,
        x="UnitsSold",
        y="product_name",
        orientation="h",
        color="UnitsSold",
        title="Top 10 Best Selling Products"
    )

    fig2.update_layout(yaxis={"categoryorder": "total ascending"})

    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------
# Product Performance Table
# ---------------------------------------------------

st.subheader("📋 Product Performance")

table_query = f"""
SELECT
    p.product_name,
    p.category,
    SUM(s.quantity) AS UnitsSold,
    SUM(s.total_amount) AS Revenue
FROM sales s
JOIN products p
ON s.product_id = p.product_id
{"WHERE p.category='" + selected_category + "'" if selected_category != "All" else ""}
GROUP BY p.product_name,p.category
ORDER BY Revenue DESC;
"""

table = run_query(table_query)

st.dataframe(
    table,
    use_container_width=True,
    hide_index=True
)