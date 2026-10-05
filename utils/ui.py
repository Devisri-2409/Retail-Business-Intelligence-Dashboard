"""
UI and Styling Utilities for Retail Business Intelligence Dashboard
Supports Professional Light and Dark Themes, consistent Plotly styling,
and Power BI / Tableau-grade executive cards.
"""

import streamlit as st
import plotly.graph_objects as go

THEME_CONFIGS = {
    "Light": {
        "bg_color": "#f8fafc",
        "card_bg": "#ffffff",
        "card_border": "#e2e8f0",
        "card_shadow": "0 1px 3px rgba(0, 0, 0, 0.05)",
        "text_primary": "#0f172a",
        "text_secondary": "#64748b",
        "text_muted": "#94a3b8",
        "accent_primary": "#1e40af",    # Deep royal blue
        "accent_secondary": "#0284c7",  # Sky blue
        "accent_teal": "#0d9488",
        "chart_template": "plotly_white",
        "chart_bg": "#ffffff",
        "chart_paper": "#ffffff",
        "grid_color": "#f1f5f9",
        "delta_up_bg": "#ecfdf5",
        "delta_up_text": "#047857",
        "delta_down_bg": "#fef2f2",
        "delta_down_text": "#b91c1c",
        "delta_neutral_bg": "#f1f5f9",
        "delta_neutral_text": "#475569",
        "palette": ["#1e40af", "#0284c7", "#0d9488", "#d97706", "#7c3aed", "#db2777"]
    },
    "Dark": {
        "bg_color": "#0b0f19",
        "card_bg": "#1e293b",
        "card_border": "#334155",
        "card_shadow": "0 2px 6px rgba(0, 0, 0, 0.4)",
        "text_primary": "#f8fafc",
        "text_secondary": "#94a3b8",
        "text_muted": "#64748b",
        "accent_primary": "#38bdf8",    # Bright sky
        "accent_secondary": "#60a5fa",
        "accent_teal": "#2dd4bf",
        "chart_template": "plotly_dark",
        "chart_bg": "#1e293b",
        "chart_paper": "#1e293b",
        "grid_color": "#334155",
        "delta_up_bg": "rgba(16, 185, 129, 0.18)",
        "delta_up_text": "#34d399",
        "delta_down_bg": "rgba(239, 68, 68, 0.18)",
        "delta_down_text": "#f87171",
        "delta_neutral_bg": "rgba(148, 163, 184, 0.15)",
        "delta_neutral_text": "#94a3b8",
        "palette": ["#38bdf8", "#2dd4bf", "#fbbf24", "#a78bfa", "#f472b6", "#34d399"]
    }
}

def init_theme() -> str:
    """Initialize theme in session state and return the current active theme."""
    if "app_theme" not in st.session_state:
        st.session_state["app_theme"] = "Light"
    return st.session_state["app_theme"]

def render_theme_toggle() -> str:
    """Render a clean theme selector in the sidebar."""
    current_theme = init_theme()
    selected_theme = st.sidebar.radio(
        "Theme Mode",
        options=["Light", "Dark"],
        index=0 if current_theme == "Light" else 1,
        horizontal=True,
        help="Switch between Executive Light and Dark BI themes"
    )
    if selected_theme != current_theme:
        st.session_state["app_theme"] = selected_theme
        st.rerun()
    return selected_theme

def apply_custom_css(theme: str = "Light"):
    """Inject polished executive CSS styles matching the selected theme."""
    cfg = THEME_CONFIGS.get(theme, THEME_CONFIGS["Light"])

    css = f"""
    <style>
        /* Main Container Styling */
        .block-container {{
            padding-top: 1.5rem !important;
            padding-bottom: 2.5rem !important;
            max-width: 1300px;
        }}

        /* Executive Header */
        .exec-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 0.75rem;
            margin-bottom: 1rem;
            border-bottom: 1px solid {cfg['card_border']};
        }}
        .exec-title {{
            font-size: 1.75rem;
            font-weight: 700;
            color: {cfg['text_primary']};
            letter-spacing: -0.025em;
            margin: 0;
            line-height: 1.2;
        }}
        .exec-subtitle {{
            font-size: 0.95rem;
            color: {cfg['text_secondary']};
            margin-top: 0.25rem;
            margin-bottom: 0;
        }}
        .exec-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.78rem;
            font-weight: 500;
            background-color: {cfg['delta_neutral_bg']};
            color: {cfg['text_secondary']};
            border: 1px solid {cfg['card_border']};
        }}
        .status-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background-color: #10b981;
        }}

        /* Filter Container */
        .filter-panel {{
            background: {cfg['card_bg']};
            border: 1px solid {cfg['card_border']};
            border-radius: 10px;
            padding: 14px 18px 8px 18px;
            margin-bottom: 1.25rem;
            box-shadow: {cfg['card_shadow']};
        }}

        /* Metric Cards */
        .kpi-card {{
            background: {cfg['card_bg']};
            border: 1px solid {cfg['card_border']};
            border-radius: 10px;
            padding: 16px 18px;
            box-shadow: {cfg['card_shadow']};
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .kpi-card:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        .kpi-label {{
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: {cfg['text_secondary']};
            margin-bottom: 6px;
        }}
        .kpi-value {{
            font-size: 1.85rem;
            font-weight: 700;
            color: {cfg['text_primary']};
            line-height: 1.15;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }}
        .kpi-delta {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 0.78rem;
            font-weight: 600;
            padding: 2px 7px;
            border-radius: 6px;
            width: fit-content;
        }}
        .delta-up {{
            background-color: {cfg['delta_up_bg']};
            color: {cfg['delta_up_text']};
        }}
        .delta-down {{
            background-color: {cfg['delta_down_bg']};
            color: {cfg['delta_down_text']};
        }}
        .delta-neutral {{
            background-color: {cfg['delta_neutral_bg']};
            color: {cfg['delta_neutral_text']};
        }}

        /* Card Section Containers */
        .section-card {{
            background: {cfg['card_bg']};
            border: 1px solid {cfg['card_border']};
            border-radius: 10px;
            padding: 18px;
            margin-bottom: 1.25rem;
            box-shadow: {cfg['card_shadow']};
        }}
        .section-header {{
            font-size: 1.05rem;
            font-weight: 600;
            color: {cfg['text_primary']};
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* Stock Pill Indicators */
        .stock-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 600;
        }}
        .stock-out {{
            background-color: {cfg['delta_down_bg']};
            color: {cfg['delta_down_text']};
        }}
        .stock-low {{
            background-color: {cfg['delta_up_bg'] if theme=='Dark' else '#fffbeb'};
            color: {cfg['delta_up_text'] if theme=='Dark' else '#b45309'};
        }}
        .stock-ok {{
            background-color: {cfg['delta_up_bg']};
            color: {cfg['delta_up_text']};
        }}

        /* Sidebar Footer */
        .sidebar-footer {{
            padding: 1rem 0;
            margin-top: 2rem;
            border-top: 1px solid {cfg['card_border']};
            font-size: 0.75rem;
            color: {cfg['text_muted']};
            line-height: 1.4;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_kpi_card(label: str, value: str, delta: str = None, delta_type: str = "neutral"):
    """Render a styled executive KPI card."""
    delta_class = "delta-neutral"
    if delta_type == "up":
        delta_class = "delta-up"
    elif delta_type == "down":
        delta_class = "delta-down"

    delta_html = f'<div class="kpi-delta {delta_class}">{delta}</div>' if delta else ''

    html = f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def style_plotly_chart(fig: go.Figure, theme: str = "Light", height: int = 340) -> go.Figure:
    """Apply consistent Power BI / Tableau grade visual styling to a Plotly figure."""
    cfg = THEME_CONFIGS.get(theme, THEME_CONFIGS["Light"])

    fig.update_layout(
        template=cfg["chart_template"],
        paper_bgcolor=cfg["chart_paper"],
        plot_bgcolor=cfg["chart_bg"],
        font=dict(
            family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            color=cfg["text_primary"],
            size=12
        ),
        margin=dict(l=40, r=20, t=45, b=40),
        height=height,
        hoverlabel=dict(
            bgcolor=cfg["card_bg"],
            font_size=12,
            font_family="Inter, sans-serif",
            bordercolor=cfg["card_border"]
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor=cfg["grid_color"],
            linecolor=cfg["card_border"],
            tickcolor=cfg["card_border"],
            title_font=dict(size=12, color=cfg["text_secondary"]),
            tickfont=dict(size=11, color=cfg["text_secondary"])
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=cfg["grid_color"],
            linecolor=cfg["card_border"],
            tickcolor=cfg["card_border"],
            title_font=dict(size=12, color=cfg["text_secondary"]),
            tickfont=dict(size=11, color=cfg["text_secondary"])
        )
    )
    return fig

def render_sidebar_footer():
    """Render a clean sidebar footer branding."""
    st.sidebar.markdown(
        """
        <div class="sidebar-footer">
            <strong>Retail BI Executive</strong><br>
            Powered by PostgreSQL + Streamlit
        </div>
        """,
        unsafe_allow_html=True
    )
