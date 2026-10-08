"""
Time Analysis Dashboard
Provides historical revenue trends and periodic comparisons (Year, Quarter, Month)
with chronological ordering, zero-based baselines, and categorical axis scaling.
"""

import os
import base64
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import run_query
from utils.ui import (
    render_theme_toggle,
    apply_custom_css,
    render_kpi_card,
    style_plotly_chart,
    render_sidebar_footer,
    THEME_CONFIGS
)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Time Analysis",
    page_icon="assets/logo.png" if os.path.exists("assets/logo.png") else "📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme & apply unified executive CSS
active_theme = render_theme_toggle()
apply_custom_css(active_theme)
theme_cfg = THEME_CONFIGS.get(active_theme, THEME_CONFIGS["Light"])

# --------------------------------------------------
# DATABASE CONNECTION HEALTH CHECK
# --------------------------------------------------
def check_db_connection() -> tuple[bool, str]:
    """Test actual database connection to local PostgreSQL."""
    try:
        run_query("SELECT 1;")
        return True, "Connected to local PostgreSQL"
    except Exception:
        return False, "PostgreSQL disconnected"

# --------------------------------------------------
# EXECUTIVE HEADER SECTION
# --------------------------------------------------
is_db_connected, db_status_msg = check_db_connection()
dot_class = "status-dot-online" if is_db_connected else "status-dot-offline"

# Read logo image as base64 for inline flex alignment
logo_b64 = ""
if os.path.exists("assets/logo.png"):
    with open("assets/logo.png", "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")

logo_html = f'<img src="data:image/png;base64,{logo_b64}" width="42" height="42" style="border-radius: 8px; flex-shrink: 0;" />' if logo_b64 else ''

header_html = f"""
<div class="exec-header-container">
    <div class="exec-header-left">
        {logo_html}
        <div>
            <h1 class="exec-title">Time Analysis</h1>
            <p class="exec-subtitle">Historical revenue trends and periodic comparisons</p>
        </div>
    </div>
    <div class="exec-badge">
        <span class="{dot_class}"></span> {db_status_msg}
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# --------------------------------------------------
# TIME GRANULARITY SELECTOR
# --------------------------------------------------
with st.container(border=True):
    col_ctrl, col_info = st.columns([0.35, 0.65])
    with col_ctrl:
        level = st.selectbox(
            "View Sales By",
            ["Year", "Quarter", "Month"],
            index=0,
            help="Select time aggregation granularity"
        )
    with col_info:
        st.caption(
            "Analyze periodic sales performance across time. Charts automatically enforce chronological ordering, "
            "zero-based revenue baselines, and categorical axis scaling to avoid misleading trend projections."
        )

# --------------------------------------------------
# DATA RETRIEVAL (PRESERVING EXACT SQL INTERFACE)
# --------------------------------------------------
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

# --------------------------------------------------
# DATA VALIDATION & NORMALIZATION
# --------------------------------------------------
if data is None or data.empty:
    st.info("No sales records available for the selected time grouping.")
    st.stop()

# Ensure Revenue is float
data["Revenue"] = pd.to_numeric(data["Revenue"], errors="coerce").fillna(0.0)
total_revenue = float(data["Revenue"].sum())

# Format readable currency labels
data["Revenue_Formatted"] = data["Revenue"].apply(lambda v: f"₹{v:,.0f}")

# Chronological sorting and categorical axis enforcement
month_order = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

if level == "Year":
    # Convert Period to int then string to enforce categorical axis (prevents fractional years like 2023.5 or 2024.0)
    data["Period"] = pd.to_numeric(data["Period"], errors="coerce").fillna(0).astype(int).astype(str)
    data = data.sort_values("Period").reset_index(drop=True)

elif level == "Quarter":
    quarter_order = ["Q1", "Q2", "Q3", "Q4"]
    data["QuarterNo"] = pd.to_numeric(data["QuarterNo"], errors="coerce").fillna(0).astype(int)
    data["Period"] = data["Period"].astype(str).str.strip()
    data = data.sort_values("QuarterNo").reset_index(drop=True)

else:  # Month
    data["MonthNo"] = pd.to_numeric(data["MonthNo"], errors="coerce").fillna(0).astype(int)
    data["Period"] = data["Period"].astype(str).str.strip()
    data = data.sort_values("MonthNo").reset_index(drop=True)

# --------------------------------------------------
# EXECUTIVE PERIODIC KPIS
# --------------------------------------------------
period_count = len(data)
avg_revenue = (total_revenue / period_count) if period_count > 0 else 0.0
peak_idx = data["Revenue"].idxmax()
peak_period = str(data.loc[peak_idx, "Period"])
peak_rev = float(data.loc[peak_idx, "Revenue"])

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    render_kpi_card(
        "Total Revenue",
        f"₹{total_revenue:,.0f}",
        f"{period_count} {level}{'s' if period_count > 1 else ''}",
        "neutral"
    )

with kpi2:
    render_kpi_card(
        f"Average / {level}",
        f"₹{avg_revenue:,.0f}",
        "Periodic mean revenue",
        "neutral"
    )

with kpi3:
    render_kpi_card(
        f"Peak {level}",
        peak_period,
        f"₹{peak_rev:,.0f}",
        "up"
    )

with kpi4:
    render_kpi_card(
        "Periods Evaluated",
        f"{period_count}",
        f"Grouping: {level}",
        "neutral"
    )

# --------------------------------------------------
# REVENUE VISUALIZATION
# --------------------------------------------------
with st.container(border=True):
    st.markdown(f'<div class="section-header">📈 {level}-wise Revenue Performance</div>', unsafe_allow_html=True)

    y_max = float(data["Revenue"].max())
    y_upper = (y_max * 1.20) if y_max > 0 else 1000.0

    if level == "Year":
        if len(data) == 1:
            # Single year dataset: Display a clean bar chart with categorical axis rather than a misleading line chart
            fig = px.bar(
                data,
                x="Period",
                y="Revenue",
                text="Revenue_Formatted",
                title=f"Annual Sales Revenue ({data['Period'].iloc[0]})",
                labels={"Period": "Fiscal Year", "Revenue": "Revenue (₹)"}
            )
            fig.update_traces(
                width=0.35,
                marker_color=theme_cfg["palette"][0],
                textposition="outside",
                hovertemplate="<b>Year %{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>"
            )
            st.caption("ℹ️ Only a single annual period (2024) is currently on record. Multi-year trend lines will activate automatically when additional fiscal years are logged.")
        else:
            # Multiple years: Categorical bar visualization
            fig = px.bar(
                data,
                x="Period",
                y="Revenue",
                text="Revenue_Formatted",
                title="Annual Sales Revenue by Year",
                labels={"Period": "Fiscal Year", "Revenue": "Revenue (₹)"}
            )
            fig.update_traces(
                marker_color=theme_cfg["palette"][0],
                textposition="outside",
                hovertemplate="<b>Year %{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>"
            )

        fig.update_xaxes(type="category")
        fig.update_yaxes(rangemode="tozero", range=[0, y_upper])

    elif level == "Quarter":
        fig = px.line(
            data,
            x="Period",
            y="Revenue",
            markers=True,
            text="Revenue_Formatted",
            title="Quarterly Sales Revenue Trend (Q1 – Q4)",
            labels={"Period": "Fiscal Quarter", "Revenue": "Revenue (₹)"}
        )
        fig.update_traces(
            line=dict(color=theme_cfg["palette"][0], width=3),
            marker=dict(size=9, color=theme_cfg["palette"][1]),
            textposition="top center",
            hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>"
        )
        fig.update_xaxes(type="category", categoryorder="array", categoryarray=["Q1", "Q2", "Q3", "Q4"])
        fig.update_yaxes(rangemode="tozero", range=[0, y_upper])

    else:  # Month
        fig = px.line(
            data,
            x="Period",
            y="Revenue",
            markers=True,
            text="Revenue_Formatted",
            title="Monthly Sales Revenue Trend (Jan – Dec)",
            labels={"Period": "Calendar Month", "Revenue": "Revenue (₹)"}
        )
        fig.update_traces(
            line=dict(color=theme_cfg["palette"][0], width=3),
            marker=dict(size=8, color=theme_cfg["palette"][1]),
            textposition="top center",
            hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>"
        )
        fig.update_xaxes(type="category", categoryorder="array", categoryarray=month_order)
        fig.update_yaxes(rangemode="tozero", range=[0, y_upper])

    fig = style_plotly_chart(fig, active_theme, height=360)
    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# SYNCHRONIZED REVENUE BREAKDOWN TABLE
# --------------------------------------------------
with st.container(border=True):
    st.markdown(f'<div class="section-header">📋 {level} Revenue Breakdown Table</div>', unsafe_allow_html=True)

    table_df = data.copy()
    table_df["Revenue (₹)"] = table_df["Revenue"].apply(lambda v: f"₹{v:,.2f}")
    if total_revenue > 0:
        table_df["Share (%)"] = table_df["Revenue"].apply(lambda v: f"{(v / total_revenue) * 100:.1f}%")
    else:
        table_df["Share (%)"] = "0.0%"

    display_cols = ["Period", "Revenue (₹)", "Share (%)"]
    col_rename = {
        "Period": f"{level}",
        "Revenue (₹)": "Revenue (₹)",
        "Share (%)": "% of Total Revenue"
    }

    st.dataframe(
        table_df[display_cols].rename(columns=col_rename),
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------
# SIDEBAR FOOTER BRANDING
# --------------------------------------------------
render_sidebar_footer()