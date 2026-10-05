import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
from utils.db import run_query
from utils.ui import (
    init_theme,
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
    page_title="Retail Business Intelligence",
    page_icon="assets/logo.png" if os.path.exists("assets/logo.png") else "📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme & apply CSS
active_theme = render_theme_toggle()
apply_custom_css(active_theme)
theme_cfg = THEME_CONFIGS[active_theme]

# --------------------------------------------------
# CACHED DATA ACCESS LAYER
# --------------------------------------------------
@st.cache_data(ttl=60)
def get_filter_bounds():
    """Fetch available years, min/max sales dates, and categories dynamically."""
    bounds_df = run_query("""
        SELECT 
            COALESCE(MIN(sale_date), CURRENT_DATE) AS min_date,
            COALESCE(MAX(sale_date), CURRENT_DATE) AS max_date
        FROM sales;
    """)
    years_df = run_query("""
        SELECT DISTINCT EXTRACT(YEAR FROM sale_date)::INTEGER AS yr
        FROM sales
        ORDER BY yr DESC;
    """)
    cats_df = run_query("""
        SELECT DISTINCT category
        FROM products
        ORDER BY category;
    """)

    min_d = bounds_df.iloc[0]["min_date"]
    max_d = bounds_df.iloc[0]["max_date"]
    years = [int(r["yr"]) for _, r in years_df.iterrows() if pd.notnull(r["yr"])]
    cats = cats_df["category"].tolist() if not cats_df.empty else []
    return min_d, max_d, years, cats

@st.cache_data(ttl=60)
def get_kpis_and_comparison(start_date: date, end_date: date, category: str):
    """Fetch core KPIs and historical comparison for the prior period."""
    cur_sql = """
        SELECT
            COALESCE(SUM(s.total_amount), 0) AS revenue,
            COUNT(DISTINCT s.sale_id) AS orders,
            COUNT(DISTINCT s.customer_id) AS active_customers
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        WHERE s.sale_date >= :start_date AND s.sale_date <= :end_date
          AND (:cat = 'All' OR p.category = :cat);
    """
    cur_df = run_query(cur_sql, {"start_date": start_date, "end_date": end_date, "cat": category})
    cur_rev = float(cur_df.iloc[0]["revenue"])
    cur_ord = int(cur_df.iloc[0]["orders"])
    cur_cust = int(cur_df.iloc[0]["active_customers"])
    cur_aov = (cur_rev / cur_ord) if cur_ord > 0 else 0.0

    # Prior Period Calculation
    duration_days = (end_date - start_date).days + 1
    prior_end = start_date - timedelta(days=1)
    prior_start = prior_end - timedelta(days=duration_days - 1)

    prior_df = run_query(cur_sql, {"start_date": prior_start, "end_date": prior_end, "cat": category})
    prior_rev = float(prior_df.iloc[0]["revenue"])
    prior_ord = int(prior_df.iloc[0]["orders"])
    prior_cust = int(prior_df.iloc[0]["active_customers"])
    prior_aov = (prior_rev / prior_ord) if prior_ord > 0 else 0.0

    # Calculate Deltas
    def calc_delta(cur, prior, is_currency=False):
        if prior == 0:
            return "Comparison unavailable", "neutral"
        pct = ((cur - prior) / prior) * 100
        if pct > 0:
            return f"↑ {pct:.1f}% vs previous period", "up"
        elif pct < 0:
            return f"↓ {abs(pct):.1f}% vs previous period", "down"
        return "0.0% vs previous period", "neutral"

    rev_delta, rev_dtype = calc_delta(cur_rev, prior_rev, True)
    ord_delta, ord_dtype = calc_delta(cur_ord, prior_ord)
    aov_delta, aov_dtype = calc_delta(cur_aov, prior_aov, True)
    cust_delta, cust_dtype = calc_delta(cur_cust, prior_cust)

    return {
        "revenue": cur_rev, "orders": cur_ord, "aov": cur_aov, "customers": cur_cust,
        "rev_delta": rev_delta, "rev_dtype": rev_dtype,
        "ord_delta": ord_delta, "ord_dtype": ord_dtype,
        "aov_delta": aov_delta, "aov_dtype": aov_dtype,
        "cust_delta": cust_delta, "cust_dtype": cust_dtype,
        "prior_orders": prior_ord
    }

@st.cache_data(ttl=60)
def get_revenue_trend(start_date: date, end_date: date, category: str):
    """Aggregate revenue across time using appropriate date granularity."""
    days = (end_date - start_date).days + 1
    if days > 70:
        # Monthly aggregation
        sql = """
            SELECT 
                DATE_TRUNC('month', s.sale_date)::DATE AS period_date,
                TRIM(TO_CHAR(s.sale_date, 'Mon YYYY')) AS period_label,
                COALESCE(SUM(s.total_amount), 0) AS revenue,
                COUNT(s.sale_id) AS orders
            FROM sales s
            JOIN products p ON s.product_id = p.product_id
            WHERE s.sale_date >= :start_date AND s.sale_date <= :end_date
              AND (:cat = 'All' OR p.category = :cat)
            GROUP BY DATE_TRUNC('month', s.sale_date)::DATE, TRIM(TO_CHAR(s.sale_date, 'Mon YYYY'))
            ORDER BY period_date;
        """
    else:
        # Daily aggregation
        sql = """
            SELECT 
                s.sale_date AS period_date,
                TO_CHAR(s.sale_date, 'DD Mon') AS period_label,
                COALESCE(SUM(s.total_amount), 0) AS revenue,
                COUNT(s.sale_id) AS orders
            FROM sales s
            JOIN products p ON s.product_id = p.product_id
            WHERE s.sale_date >= :start_date AND s.sale_date <= :end_date
              AND (:cat = 'All' OR p.category = :cat)
            GROUP BY s.sale_date, TO_CHAR(s.sale_date, 'DD Mon')
            ORDER BY s.sale_date;
        """
    return run_query(sql, {"start_date": start_date, "end_date": end_date, "cat": category})

@st.cache_data(ttl=60)
def get_category_breakdown(start_date: date, end_date: date, category: str):
    """Fetch revenue, units, and order share per category."""
    sql = """
        SELECT 
            p.category,
            COALESCE(SUM(s.total_amount), 0) AS revenue,
            COALESCE(SUM(s.quantity), 0) AS units_sold,
            COUNT(s.sale_id) AS order_count
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        WHERE s.sale_date >= :start_date AND s.sale_date <= :end_date
          AND (:cat = 'All' OR p.category = :cat)
        GROUP BY p.category
        ORDER BY revenue DESC;
    """
    return run_query(sql, {"start_date": start_date, "end_date": end_date, "cat": category})

@st.cache_data(ttl=60)
def get_top_products(start_date: date, end_date: date, category: str, limit: int = 5):
    """Rank top products by revenue within the selected filter."""
    sql = """
        SELECT 
            p.product_name,
            p.category,
            COALESCE(SUM(s.total_amount), 0) AS revenue,
            COALESCE(SUM(s.quantity), 0) AS units_sold
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        WHERE s.sale_date >= :start_date AND s.sale_date <= :end_date
          AND (:cat = 'All' OR p.category = :cat)
        GROUP BY p.product_name, p.category
        ORDER BY revenue DESC
        LIMIT :lim;
    """
    return run_query(sql, {"start_date": start_date, "end_date": end_date, "cat": category, "lim": limit})

@st.cache_data(ttl=60)
def get_customer_summary(start_date: date, end_date: date, category: str):
    """Fetch active customer count, average rating, and top spenders."""
    rating_sql = """
        SELECT ROUND(COALESCE(AVG(c.rate), 0)::NUMERIC, 2) AS avg_rating
        FROM customers c
        WHERE c.customer_id IN (
            SELECT DISTINCT s.customer_id
            FROM sales s
            JOIN products p ON s.product_id = p.product_id
            WHERE s.sale_date >= :start_date AND s.sale_date <= :end_date
              AND (:cat = 'All' OR p.category = :cat)
        );
    """
    top_cust_sql = """
        SELECT 
            c.customer_name,
            COALESCE(SUM(s.total_amount), 0) AS total_spent,
            COUNT(s.sale_id) AS orders,
            c.rate AS rating
        FROM sales s
        JOIN customers c ON s.customer_id = c.customer_id
        JOIN products p ON s.product_id = p.product_id
        WHERE s.sale_date >= :start_date AND s.sale_date <= :end_date
          AND (:cat = 'All' OR p.category = :cat)
        GROUP BY c.customer_name, c.rate
        ORDER BY total_spent DESC
        LIMIT 5;
    """
    rating_df = run_query(rating_sql, {"start_date": start_date, "end_date": end_date, "cat": category})
    top_df = run_query(top_cust_sql, {"start_date": start_date, "end_date": end_date, "cat": category})
    avg_rate = float(rating_df.iloc[0]["avg_rating"]) if not rating_df.empty else 0.0
    return avg_rate, top_df

@st.cache_data(ttl=60)
def get_inventory_alerts():
    """Fetch stock categorization and list of urgent replenishment candidates."""
    counts_sql = """
        SELECT 
            COUNT(*) FILTER (WHERE stock = 0) AS out_of_stock,
            COUNT(*) FILTER (WHERE stock > 0 AND stock <= 10) AS low_stock,
            COUNT(*) FILTER (WHERE stock > 10) AS in_stock,
            COUNT(*) AS total_products
        FROM products;
    """
    urgent_sql = """
        SELECT 
            product_name,
            category,
            stock
        FROM products
        WHERE stock <= 10
        ORDER BY stock ASC, product_name ASC
        LIMIT 6;
    """
    counts_df = run_query(counts_sql)
    urgent_df = run_query(urgent_sql)
    return counts_df.iloc[0].to_dict(), urgent_df

# --------------------------------------------------
# HEADER SECTION
# --------------------------------------------------
col_h1, col_h2 = st.columns([0.78, 0.22])

with col_h1:
    st.markdown(
        """
        <div class="exec-header">
            <div>
                <h1 class="exec-title">Retail Business Intelligence</h1>
                <p class="exec-subtitle">Executive overview of sales, customers and inventory</p>
            </div>
            <div class="exec-badge">
                <span class="status-dot"></span> Data updated from local PostgreSQL
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_h2:
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=95)

# --------------------------------------------------
# FILTER BAR SECTION
# --------------------------------------------------
min_db_date, max_db_date, available_years, available_cats = get_filter_bounds()

# Default to latest year
default_year = available_years[0] if available_years else date.today().year
year_options = ["All Years"] + [str(y) for y in available_years]

st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
f_col1, f_col2, f_col3, f_col4 = st.columns([0.22, 0.26, 0.26, 0.26])

with f_col1:
    selected_year_str = st.selectbox(
        "Year",
        options=year_options,
        index=1 if len(year_options) > 1 else 0,
        help="Select reporting year"
    )

# Compute initial range based on year selection
if selected_year_str != "All Years":
    sel_yr = int(selected_year_str)
    year_start = max(date(sel_yr, 1, 1), min_db_date)
    year_end = min(date(sel_yr, 12, 31), max_db_date)
else:
    year_start = min_db_date
    year_end = max_db_date

with f_col2:
    filter_start = st.date_input(
        "Start Date",
        value=year_start,
        min_value=min_db_date,
        max_value=max_db_date
    )

with f_col3:
    filter_end = st.date_input(
        "End Date",
        value=year_end,
        min_value=min_db_date,
        max_value=max_db_date
    )

with f_col4:
    selected_cat = st.selectbox(
        "Product Category",
        options=["All"] + available_cats,
        index=0,
        help="Filter dashboard metrics by product category"
    )
st.markdown('</div>', unsafe_allow_html=True)

# Guard against invalid date order
if filter_start > filter_end:
    st.error("Error: Start Date must be prior to or equal to End Date.")
    st.stop()

# --------------------------------------------------
# DATA FETCHING
# --------------------------------------------------
kpi_data = get_kpis_and_comparison(filter_start, filter_end, selected_cat)
trend_df = get_revenue_trend(filter_start, filter_end, selected_cat)
cat_df = get_category_breakdown(filter_start, filter_end, selected_cat)
top_prod_df = get_top_products(filter_start, filter_end, selected_cat, limit=5)
avg_rating, top_cust_df = get_customer_summary(filter_start, filter_end, selected_cat)
inv_counts, urgent_inv_df = get_inventory_alerts()

# --------------------------------------------------
# PART 2 & 3: KPI SECTION & PERIOD COMPARISON
# --------------------------------------------------
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    render_kpi_card(
        label="Total Revenue",
        value=f"₹{kpi_data['revenue']:,.0f}",
        delta=kpi_data["rev_delta"],
        delta_type=kpi_data["rev_dtype"]
    )

with kpi_col2:
    render_kpi_card(
        label="Total Orders",
        value=f"{kpi_data['orders']:,}",
        delta=kpi_data["ord_delta"],
        delta_type=kpi_data["ord_dtype"]
    )

with kpi_col3:
    render_kpi_card(
        label="Average Order Value",
        value=f"₹{kpi_data['aov']:,.0f}",
        delta=kpi_data["aov_delta"],
        delta_type=kpi_data["aov_dtype"]
    )

with kpi_col4:
    render_kpi_card(
        label="Active Customers",
        value=f"{kpi_data['customers']:,}",
        delta=kpi_data["cust_delta"],
        delta_type=kpi_data["cust_dtype"]
    )

st.write("")

# --------------------------------------------------
# PART 4: MAIN SALES TREND
# --------------------------------------------------
if not trend_df.empty:
    fig_trend = go.Figure()

    # Smooth area fill under the line
    fig_trend.add_trace(go.Scatter(
        x=trend_df["period_label"],
        y=trend_df["revenue"],
        mode="lines+markers",
        name="Revenue",
        line=dict(color=theme_cfg["accent_primary"], width=2.5),
        marker=dict(size=6, color=theme_cfg["accent_secondary"]),
        fill="tozeroy",
        fillcolor="rgba(37, 99, 235, 0.08)" if active_theme == "Light" else "rgba(56, 189, 248, 0.12)",
        hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<br>Orders: %{customdata:,}<extra></extra>",
        customdata=trend_df["orders"]
    ))

    fig_trend.update_layout(
        title=dict(
            text="Revenue Trend",
            font=dict(size=15, color=theme_cfg["text_primary"])
        ),
        xaxis_title=None,
        yaxis_title="Revenue (₹)"
    )
    style_plotly_chart(fig_trend, theme=active_theme, height=330)
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.info("No sales data available for the selected date range and category.")

# --------------------------------------------------
# PART 5 & 6: CATEGORY PERFORMANCE & TOP PRODUCTS
# --------------------------------------------------
col_mid1, col_mid2 = st.columns(2)

with col_mid1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📊 Revenue by Category</div>', unsafe_allow_html=True)

    if not cat_df.empty:
        # Calculate Share of Total
        total_cat_rev = cat_df["revenue"].sum()
        cat_df["share_pct"] = (cat_df["revenue"] / total_cat_rev * 100) if total_cat_rev > 0 else 0

        fig_cat = px.bar(
            cat_df,
            x="revenue",
            y="category",
            orientation="h",
            text=cat_df["revenue"].apply(lambda v: f"₹{v:,.0f}"),
            color="revenue",
            color_continuous_scale=["#93c5fd", "#1e40af"] if active_theme == "Light" else ["#38bdf8", "#0284c7"]
        )
        fig_cat.update_layout(
            yaxis=dict(categoryorder="total ascending", title=None),
            xaxis=dict(title="Revenue (₹)", showgrid=True),
            coloraxis_showscale=False
        )
        style_plotly_chart(fig_cat, theme=active_theme, height=230)
        st.plotly_chart(fig_cat, use_container_width=True)

        # Compact summary breakdown table
        table_df = cat_df[["category", "revenue", "share_pct"]].copy()
        table_df.columns = ["Category", "Revenue", "% of Total"]
        table_df["Revenue"] = table_df["Revenue"].apply(lambda x: f"₹{x:,.0f}")
        table_df["% of Total"] = table_df["% of Total"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(table_df, use_container_width=True, hide_index=True)
    else:
        st.info("No category revenue available for this filter.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_mid2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">🏆 Top 5 Products by Revenue</div>', unsafe_allow_html=True)

    if not top_prod_df.empty:
        fig_top = px.bar(
            top_prod_df,
            x="revenue",
            y="product_name",
            orientation="h",
            text=top_prod_df["revenue"].apply(lambda v: f"₹{v:,.0f}"),
            color="revenue",
            color_continuous_scale=["#99f6e4", "#0d9488"] if active_theme == "Light" else ["#2dd4bf", "#0f766e"]
        )
        fig_top.update_layout(
            yaxis=dict(categoryorder="total ascending", title=None),
            xaxis=dict(title="Revenue (₹)", showgrid=True),
            coloraxis_showscale=False
        )
        style_plotly_chart(fig_top, theme=active_theme, height=230)
        st.plotly_chart(fig_top, use_container_width=True)

        # Compact Product Table
        prod_table = top_prod_df[["product_name", "category", "revenue", "units_sold"]].copy()
        prod_table.columns = ["Product", "Category", "Revenue", "Units Sold"]
        prod_table["Revenue"] = prod_table["Revenue"].apply(lambda x: f"₹{x:,.0f}")
        prod_table["Units Sold"] = prod_table["Units Sold"].apply(lambda x: f"{x:,}")
        st.dataframe(prod_table, use_container_width=True, hide_index=True)
    else:
        st.info("No product sales data in this filter.")
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# PART 7 & 8: CUSTOMER SNAPSHOT & INVENTORY ALERTS
# --------------------------------------------------
col_bot1, col_bot2 = st.columns(2)

with col_bot1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">👥 Customer Snapshot</div>', unsafe_allow_html=True)

    sub_c1, sub_c2 = st.columns(2)
    with sub_c1:
        st.metric("Active Customers in Period", f"{kpi_data['customers']:,}")
    with sub_c2:
        st.metric("Average Customer Satisfaction", f"{avg_rating:.2f} / 5.0" if avg_rating > 0 else "N/A")

    if not top_cust_df.empty:
        st.markdown("<p style='font-size: 0.85rem; font-weight: 600; margin: 10px 0 4px 0;'>Top Customers by Spending</p>", unsafe_allow_html=True)
        cust_display = top_cust_df.copy()
        cust_display.columns = ["Customer Name", "Total Spent", "Orders", "Rating"]
        cust_display["Total Spent"] = cust_display["Total Spent"].apply(lambda x: f"₹{x:,.0f}")
        cust_display["Rating"] = cust_display["Rating"].apply(lambda x: f"⭐ {float(x):.1f}")
        st.dataframe(cust_display, use_container_width=True, hide_index=True)
    else:
        st.info("No customer transaction data in current filter.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_bot2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">⚠️ Inventory Alerts</div>', unsafe_allow_html=True)

    # 3 Badges
    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1:
        st.markdown(
            f'<div class="stock-pill stock-out">🔴 Out of Stock: {inv_counts["out_of_stock"]}</div>',
            unsafe_allow_html=True
        )
    with b_col2:
        st.markdown(
            f'<div class="stock-pill stock-low">🟠 Low Stock: {inv_counts["low_stock"]}</div>',
            unsafe_allow_html=True
        )
    with b_col3:
        st.markdown(
            f'<div class="stock-pill stock-ok">🟢 In Stock: {inv_counts["in_stock"]}</div>',
            unsafe_allow_html=True
        )

    st.markdown("<p style='font-size: 0.85rem; font-weight: 600; margin: 14px 0 4px 0;'>Urgent Restocking Required</p>", unsafe_allow_html=True)
    if not urgent_inv_df.empty:
        urg_display = urgent_inv_df.copy()
        urg_display.columns = ["Product", "Category", "Stock Left"]
        urg_display["Status"] = urg_display["Stock Left"].apply(
            lambda s: "Out of Stock" if s == 0 else f"Low ({s} units)"
        )
        st.dataframe(urg_display[["Product", "Category", "Stock Left", "Status"]], use_container_width=True, hide_index=True)
    else:
        st.success("All products have healthy inventory levels (&gt; 10 units).")
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# PART 9: BUSINESS INSIGHTS (FACTUAL & DYNAMIC)
# --------------------------------------------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-header">💡 Executive Business Insights</div>', unsafe_allow_html=True)

insights = []

# Insight 1: Category leader
if not cat_df.empty:
    top_cat = cat_df.iloc[0]["category"]
    top_cat_rev = cat_df.iloc[0]["revenue"]
    top_cat_share = cat_df.iloc[0]["share_pct"]
    insights.append(f"**Category Leadership:** **{top_cat}** was the leading category, contributing **₹{top_cat_rev:,.0f}** ({top_cat_share:.1f}% of total sales) during this period.")

# Insight 2: Top product
if not top_prod_df.empty:
    top_p_name = top_prod_df.iloc[0]["product_name"]
    top_p_rev = top_prod_df.iloc[0]["revenue"]
    top_p_units = top_prod_df.iloc[0]["units_sold"]
    insights.append(f"**Top Performing SKU:** **{top_p_name}** achieved highest revenue of **₹{top_p_rev:,.0f}** across **{top_p_units:,}** units sold.")

# Insight 3: Inventory alert
total_replenish = inv_counts["out_of_stock"] + inv_counts["low_stock"]
if total_replenish > 0:
    insights.append(f"**Inventory Alert:** **{total_replenish} products** currently require replenishment (**{inv_counts['out_of_stock']} out of stock**, **{inv_counts['low_stock']} low stock**).")
else:
    insights.append("**Inventory Status:** Inventory levels are optimal across all product categories.")

# Insight 4: Period trend
if kpi_data["prior_orders"] > 0:
    insights.append(f"**Sales Momentum:** Total revenue is **{kpi_data['rev_delta']}** with average order value at **₹{kpi_data['aov']:,.0f}**.")
else:
    insights.append(f"**Transaction Volume:** Realized **{kpi_data['orders']:,} orders** with an average basket value of **₹{kpi_data['aov']:,.0f}** across **{kpi_data['customers']:,} active customers**.")

ins_col1, ins_col2 = st.columns(2)
for i, ins in enumerate(insights):
    target_col = ins_col1 if (i % 2 == 0) else ins_col2
    with target_col:
        st.info(ins)

st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# PART 12: SIDEBAR BRANDING FOOTER
# --------------------------------------------------
render_sidebar_footer()