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
        COALESCE(SUM(s.total_amount), 0) AS "Revenue"
    FROM sales s
    JOIN products p
        ON s.product_id = p.product_id
    GROUP BY p.category
    ORDER BY "Revenue" DESC;
    """
    revenue_params = None

    product_query = """
    SELECT
        p.product_name,
        COALESCE(SUM(s.quantity), 0) AS "UnitsSold"
    FROM sales s
    JOIN products p
        ON s.product_id = p.product_id
    GROUP BY p.product_name
    ORDER BY "UnitsSold" DESC
    LIMIT 10;
    """
    product_params = None

else:

    revenue_query = """
    SELECT
        p.category,
        COALESCE(SUM(s.total_amount), 0) AS "Revenue"
    FROM sales s
    JOIN products p
        ON s.product_id = p.product_id
    WHERE p.category = :category
    GROUP BY p.category;
    """
    revenue_params = {"category": selected_category}

    product_query = """
    SELECT
        p.product_name,
        COALESCE(SUM(s.quantity), 0) AS "UnitsSold"
    FROM sales s
    JOIN products p
        ON s.product_id = p.product_id
    WHERE p.category = :category
    GROUP BY p.product_name
    ORDER BY "UnitsSold" DESC
    LIMIT 10;
    """
    product_params = {"category": selected_category}

category_sales = run_query(revenue_query, params=revenue_params)
top_products = run_query(product_query, params=product_params)

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

if selected_category == "All":
    table_query = """
    SELECT
        p.product_name,
        p.category,
        COALESCE(SUM(s.quantity), 0) AS "UnitsSold",
        COALESCE(SUM(s.total_amount), 0) AS "Revenue"
    FROM sales s
    JOIN products p
    ON s.product_id = p.product_id
    GROUP BY p.product_name, p.category
    ORDER BY "Revenue" DESC;
    """
    table_params = None
else:
    table_query = """
    SELECT
        p.product_name,
        p.category,
        COALESCE(SUM(s.quantity), 0) AS "UnitsSold",
        COALESCE(SUM(s.total_amount), 0) AS "Revenue"
    FROM sales s
    JOIN products p
    ON s.product_id = p.product_id
    WHERE p.category = :category
    GROUP BY p.product_name, p.category
    ORDER BY "Revenue" DESC;
    """
    table_params = {"category": selected_category}

table = run_query(table_query, params=table_params)

st.dataframe(
    table,
    use_container_width=True,
    hide_index=True
)