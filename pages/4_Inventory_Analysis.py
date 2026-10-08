"""
Retail Operations and Inventory Management Dashboard
Provides real-time stock monitoring, category breakdown, stock-status classification,
and prioritized replenishment recommendations based on configurable target stock levels.
"""

import os
import base64
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    page_title="Inventory Analysis",
    page_icon="assets/logo.png" if os.path.exists("assets/logo.png") else "📦",
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
# DATA ACCESS LAYER
# --------------------------------------------------
@st.cache_data(ttl=60)
def load_products_inventory() -> pd.DataFrame:
    """Fetch complete product inventory from PostgreSQL."""
    sql = """
        SELECT 
            product_id,
            product_name,
            category,
            price,
            stock
        FROM products
        ORDER BY category, product_name;
    """
    return run_query(sql)

# --------------------------------------------------
# EXECUTIVE HEADER SECTION
# --------------------------------------------------
is_db_connected, db_status_msg = check_db_connection()
dot_class = "status-dot-online" if is_db_connected else "status-dot-offline"

# Read logo image as base64 for perfect inline flex alignment
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
            <h1 class="exec-title">Inventory Operations & Management</h1>
            <p class="exec-subtitle">Real-time stock monitoring, category breakdown, and replenishment recommendations</p>
        </div>
    </div>
    <div class="exec-badge">
        <span class="{dot_class}"></span> {db_status_msg}
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# Advisory context banner
st.caption("ℹ️ **Demo Retail Dataset**: Showing realistic inventory levels from local PostgreSQL (`retail_dashboard`). Restocking calculations are advisory recommendations based on configurable target stock levels.")

# --------------------------------------------------
# DATA RETRIEVAL & ENRICHMENT
# --------------------------------------------------
raw_df = load_products_inventory()

if raw_df.empty:
    st.error("No product inventory records found in PostgreSQL database.")
    st.stop()

# Enrich raw dataset with operational classifications
working_df = raw_df.copy()
working_df["price"] = pd.to_numeric(working_df["price"], errors="coerce").fillna(0.0)
working_df["stock"] = pd.to_numeric(working_df["stock"], errors="coerce").fillna(0).astype(int)

# Stock status classification
def classify_stock_status(stock: int) -> str:
    if stock == 0:
        return "Out of Stock"
    elif stock <= 10:
        return "Low Stock"
    return "In Stock"

working_df["stock_status"] = working_df["stock"].apply(classify_stock_status)

# --------------------------------------------------
# FILTER & CONFIGURATION CONTROL BAR
# --------------------------------------------------
available_categories = sorted(working_df["category"].dropna().unique().tolist())

with st.container(border=True):
    f_col1, f_col2, f_col3, f_col4 = st.columns([0.28, 0.24, 0.28, 0.20])

    with f_col1:
        search_query = st.text_input(
            "🔍 Search Product",
            value="",
            placeholder="Filter by product name...",
            help="Case-insensitive search across product catalog"
        ).strip().lower()

    with f_col2:
        selected_category = st.selectbox(
            "📁 Category",
            options=["All"] + available_categories,
            index=0,
            help="Filter by product category"
        )

    with f_col3:
        status_options = [
            "All",
            "Requires Attention (Out & Low)",
            "Out of Stock (0 units)",
            "Low Stock (1–10 units)",
            "In Stock (>10 units)"
        ]
        selected_status = st.selectbox(
            "🏷️ Stock Status",
            options=status_options,
            index=0,
            help="Filter by current stock status level"
        )

    with f_col4:
        target_stock = st.number_input(
            "🎯 Target Stock",
            min_value=10,
            max_value=500,
            value=50,
            step=5,
            help="Standard replenishment inventory target per SKU"
        )

# Compute replenishment parameters based on configurable target stock
working_df["target_stock"] = target_stock
working_df["suggested_reorder"] = working_df["stock"].apply(lambda s: max(0, target_stock - s))
working_df["est_reorder_cost"] = working_df["suggested_reorder"] * working_df["price"]

# Severity ranking for sorting (Out of Stock = 1, Low Stock = 2, In Stock = 3)
def get_severity(stock: int) -> int:
    if stock == 0:
        return 1
    elif stock <= 10:
        return 2
    return 3

working_df["severity"] = working_df["stock"].apply(get_severity)

# Apply filters
filtered_df = working_df.copy()

if search_query:
    filtered_df = filtered_df[filtered_df["product_name"].str.lower().str.contains(search_query, na=False)]

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["category"] == selected_category]

if selected_status == "Requires Attention (Out & Low)":
    filtered_df = filtered_df[filtered_df["stock"] <= 10]
elif selected_status == "Out of Stock (0 units)":
    filtered_df = filtered_df[filtered_df["stock"] == 0]
elif selected_status == "Low Stock (1–10 units)":
    filtered_df = filtered_df[(filtered_df["stock"] > 0) & (filtered_df["stock"] <= 10)]
elif selected_status == "In Stock (>10 units)":
    filtered_df = filtered_df[filtered_df["stock"] > 10]

# --------------------------------------------------
# EXECUTIVE INVENTORY OVERVIEW (KPI CARDS)
# --------------------------------------------------
total_products_count = len(filtered_df)
in_stock_count = int((filtered_df["stock"] > 10).sum())
low_stock_count = int(((filtered_df["stock"] > 0) & (filtered_df["stock"] <= 10)).sum())
out_stock_count = int((filtered_df["stock"] == 0).sum())
total_stock_units = int(filtered_df["stock"].sum())

# Units needing restock for critical/low-stock items
attention_df = filtered_df[filtered_df["stock"] <= 10]
reorder_units_needed = int(attention_df["suggested_reorder"].sum())

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

with kpi_col1:
    render_kpi_card(
        "Total SKUs",
        f"{total_products_count:,}",
        f"{len(filtered_df['category'].unique())} Categories" if total_products_count > 0 else "0 Categories",
        "neutral"
    )

with kpi_col2:
    render_kpi_card(
        "In Stock",
        f"{in_stock_count:,}",
        "> 10 units (Healthy)",
        "up" if in_stock_count > 0 else "neutral"
    )

with kpi_col3:
    render_kpi_card(
        "Low Stock",
        f"{low_stock_count:,}",
        "1 – 10 units left",
        "down" if low_stock_count > 0 else "up"
    )

with kpi_col4:
    render_kpi_card(
        "Out of Stock",
        f"{out_stock_count:,}",
        "0 units remaining",
        "down" if out_stock_count > 0 else "up"
    )

with kpi_col5:
    render_kpi_card(
        "Stock on Hand",
        f"{total_stock_units:,}",
        "Total units in warehouse",
        "neutral"
    )

with kpi_col6:
    render_kpi_card(
        "Restock Units",
        f"{reorder_units_needed:,}",
        f"Target: {target_stock} units",
        "down" if reorder_units_needed > 0 else "up"
    )

# --------------------------------------------------
# VISUAL ANALYTICS BREAKDOWN
# --------------------------------------------------
with st.container(border=True):
    st.markdown('<div class="section-header">📊 Inventory Visual Breakdown</div>', unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns(2)

    # 1. Stock Status Distribution Donut Chart
    with chart_col1:
        status_counts = pd.DataFrame([
            {"Status": "In Stock", "Count": in_stock_count},
            {"Status": "Low Stock", "Count": low_stock_count},
            {"Status": "Out of Stock", "Count": out_stock_count}
        ])
        status_counts = status_counts[status_counts["Count"] > 0]

        color_map = {
            "Out of Stock": "#ef4444",
            "Low Stock": "#f59e0b",
            "In Stock": "#10b981"
        }

        if not status_counts.empty:
            fig_status = px.pie(
                status_counts,
                names="Status",
                values="Count",
                hole=0.55,
                color="Status",
                color_discrete_map=color_map,
                title="Stock Status Distribution"
            )
            fig_status.update_traces(
                textposition="inside",
                textinfo="percent+value",
                hovertemplate="<b>%{label}</b><br>SKUs: %{value} (%{percent})<extra></extra>"
            )
            fig_status = style_plotly_chart(fig_status, active_theme, height=310)
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("No items match the current filter selection.")

    # 2. Stock Units and SKUs by Category Bar Chart
    with chart_col2:
        if not filtered_df.empty:
            cat_agg = filtered_df.groupby("category").agg(
                Total_Stock=("stock", "sum"),
                SKU_Count=("product_id", "count")
            ).reset_index().sort_values("Total_Stock", ascending=False)

            fig_cat = px.bar(
                cat_agg,
                x="category",
                y="Total_Stock",
                text="Total_Stock",
                color="category",
                color_discrete_sequence=theme_cfg["palette"],
                title="Inventory Units by Category",
                labels={"category": "Category", "Total_Stock": "Units in Stock"}
            )
            fig_cat.update_traces(
                texttemplate="%{text:,}",
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Stock: %{y:,} units<extra></extra>"
            )
            fig_cat = style_plotly_chart(fig_cat, active_theme, height=310)
            fig_cat.update_layout(showlegend=False)
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("No category data available for current filter.")

# --------------------------------------------------
# RESTOCKING RECOMMENDATIONS (PRIORITIZED)
# --------------------------------------------------
with st.container(border=True):
    st.markdown('<div class="section-header">🚨 Priority Restocking Recommendations (Advisory)</div>', unsafe_allow_html=True)
    st.caption(
        f"Prioritized replenishment schedule: **Out-of-Stock** SKUs appear first, followed by **Low-Stock** SKUs. "
        f"Quantities indicate the units needed to restore stock to the target of **{target_stock} units**. "
        "Advisory recommendations only — no automatic purchase orders are executed."
    )

    # Restock prioritized dataset (Severity 1: Out of Stock, Severity 2: Low Stock)
    restock_scope = filtered_df[filtered_df["severity"] <= 2].copy()

    # Prioritize: Out of Stock first (severity 1), Low Stock second (severity 2), then ascending stock, then descending price
    restock_sorted = restock_scope.sort_values(
        by=["severity", "stock", "price"],
        ascending=[True, True, False]
    )

    if not restock_sorted.empty:
        total_restock_skus = len(restock_sorted)
        total_restock_units = int(restock_sorted["suggested_reorder"].sum())
        total_est_cost = float(restock_sorted["est_reorder_cost"].sum())

        r_sub1, r_sub2, r_sub3 = st.columns(3)
        with r_sub1:
            st.metric("SKUs Requiring Restock", f"{total_restock_skus} products")
        with r_sub2:
            st.metric("Total Replenishment Units", f"{total_restock_units:,} units")
        with r_sub3:
            st.metric("Est. Capital Required", f"₹{total_est_cost:,.2f}")

        # Format presentation table
        def format_urgency_badge(stock: int) -> str:
            if stock == 0:
                return "🔴 Critical (Out of Stock)"
            return "🟡 Urgent (Low Stock)"

        display_restock = restock_sorted.copy()
        display_restock["Priority Urgency"] = display_restock["stock"].apply(format_urgency_badge)
        display_restock["Unit Price"] = display_restock["price"].apply(lambda p: f"₹{p:,.2f}")
        display_restock["Est. Restock Cost"] = display_restock["est_reorder_cost"].apply(lambda c: f"₹{c:,.2f}")

        restock_columns = [
            "Priority Urgency",
            "product_name",
            "category",
            "stock",
            "target_stock",
            "suggested_reorder",
            "Unit Price",
            "Est. Restock Cost"
        ]

        display_restock_view = display_restock[restock_columns].rename(columns={
            "product_name": "Product Name",
            "category": "Category",
            "stock": "Current Stock",
            "target_stock": "Target Stock",
            "suggested_reorder": "Suggested Reorder Qty"
        })

        st.dataframe(
            display_restock_view,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("✅ All products in the selected view have healthy stock levels (> 10 units). No immediate replenishment required.")

# --------------------------------------------------
# COMPREHENSIVE INVENTORY MONITORING & CATALOG
# --------------------------------------------------
with st.container(border=True):
    st.markdown('<div class="section-header">📋 Complete Inventory Monitoring & Catalog</div>', unsafe_allow_html=True)
    st.caption("Searchable and filterable master inventory catalog with unit pricing and replenishment targets.")

    if not filtered_df.empty:
        # Sort catalog by category, then product name
        catalog_df = filtered_df.sort_values(by=["category", "product_name"]).copy()

        def format_catalog_status(stock: int) -> str:
            if stock == 0:
                return "🔴 Out of Stock"
            elif stock <= 10:
                return f"🟡 Low ({stock} left)"
            return f"🟢 In Stock ({stock} units)"

        catalog_df["Status"] = catalog_df["stock"].apply(format_catalog_status)
        catalog_df["Unit Price (₹)"] = catalog_df["price"].apply(lambda p: f"₹{p:,.2f}")
        catalog_df["Est. Restock Cost (₹)"] = catalog_df["est_reorder_cost"].apply(lambda c: f"₹{c:,.2f}")

        catalog_view = catalog_df[[
            "product_id",
            "product_name",
            "category",
            "Unit Price (₹)",
            "stock",
            "Status",
            "target_stock",
            "suggested_reorder",
            "Est. Restock Cost (₹)"
        ]].rename(columns={
            "product_id": "Product ID",
            "product_name": "Product Name",
            "category": "Category",
            "stock": "Current Stock",
            "target_stock": "Target Level",
            "suggested_reorder": "Suggested Reorder"
        })

        st.dataframe(
            catalog_view,
            use_container_width=True,
            hide_index=True
        )

        # --------------------------------------------------
        # CSV EXPORT
        # --------------------------------------------------
        export_df = catalog_df[[
            "product_id",
            "product_name",
            "category",
            "price",
            "stock",
            "stock_status",
            "target_stock",
            "suggested_reorder",
            "est_reorder_cost"
        ]].rename(columns={
            "product_id": "Product ID",
            "product_name": "Product Name",
            "category": "Category",
            "price": "Unit Price (INR)",
            "stock": "Current Stock",
            "stock_status": "Stock Status",
            "target_stock": "Target Stock Level",
            "suggested_reorder": "Suggested Reorder Qty",
            "est_reorder_cost": "Estimated Restock Cost (INR)"
        })

        csv_data = export_df.to_csv(index=False)

        st.download_button(
            label="📥 Download Inventory Operations Report (CSV)",
            data=csv_data,
            file_name="inventory_operations_report.csv",
            mime="text/csv",
            help="Export filtered inventory snapshot including suggested reorders and estimated costs"
        )
    else:
        st.warning("No products match the selected filter criteria.")

# --------------------------------------------------
# SIDEBAR FOOTER BRANDING
# --------------------------------------------------
render_sidebar_footer()