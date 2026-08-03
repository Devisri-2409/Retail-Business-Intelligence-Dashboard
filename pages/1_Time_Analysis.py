import streamlit as st
import plotly.express as px
from utils.db import run_query

st.set_page_config(page_title="Time Analysis", layout="wide")

st.title("📅 Time Analysis")

level = st.selectbox(
    "View Sales By",
    ["Year", "Quarter", "Month"]
)

if level == "Year":

    query = """
    SELECT
    YEAR(sale_date) AS Period,
    SUM(total_amount) AS Revenue
    FROM sales
    GROUP BY YEAR(sale_date)
    ORDER BY YEAR(sale_date)
    """

elif level == "Quarter":

    query = """
    SELECT
QUARTER(sale_date) AS QuarterNo,
CONCAT('Q', QUARTER(sale_date)) AS Period,
SUM(total_amount) AS Revenue
FROM sales
GROUP BY QuarterNo
ORDER BY QuarterNo;
    """

else:

    query = """
    SELECT
    MONTHNAME(sale_date) AS Period,
    MONTH(sale_date) AS MonthNo,
    SUM(total_amount) AS Revenue
    FROM sales
    GROUP BY MONTH(sale_date),MONTHNAME(sale_date)
    ORDER BY MonthNo
    """

data = run_query(query)
fig = px.line(
    data,
    x="Period",
    y="Revenue",
    markers=True
)

st.plotly_chart(fig, use_container_width=True)

st.dataframe(data, use_container_width=True)