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
        EXTRACT(YEAR FROM sale_date)::INTEGER AS "Period",
        COALESCE(SUM(total_amount), 0) AS "Revenue"
    FROM sales
    GROUP BY EXTRACT(YEAR FROM sale_date)
    ORDER BY "Period";
    """

elif level == "Quarter":

    query = """
    SELECT
        EXTRACT(QUARTER FROM sale_date)::INTEGER AS "QuarterNo",
        CONCAT('Q', EXTRACT(QUARTER FROM sale_date)::INTEGER) AS "Period",
        COALESCE(SUM(total_amount), 0) AS "Revenue"
    FROM sales
    GROUP BY EXTRACT(QUARTER FROM sale_date)
    ORDER BY "QuarterNo";
    """

else:

    query = """
    SELECT
        TRIM(TO_CHAR(sale_date, 'Month')) AS "Period",
        EXTRACT(MONTH FROM sale_date)::INTEGER AS "MonthNo",
        COALESCE(SUM(total_amount), 0) AS "Revenue"
    FROM sales
    GROUP BY EXTRACT(MONTH FROM sale_date), TRIM(TO_CHAR(sale_date, 'Month'))
    ORDER BY "MonthNo";
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