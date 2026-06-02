import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import EcommerceDataLoader
from src.analyzer import SalesAnalyzer

# ─── Page configuration ──────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Analytics | Olist Brasil",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect fill='%230D1117' rx='20' width='100' height='100'/><text y='70' x='15' font-size='60' fill='%2358A6FF'>O</text></svg>",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-primary: #0D1117;
        --bg-secondary: #161B22;
        --bg-tertiary: #1C2333;
        --border: #30363D;
        --border-muted: #21262D;
        --text-primary: #E6EDF3;
        --text-secondary: #8B949E;
        --text-muted: #484F58;
        --accent-blue: #58A6FF;
        --accent-purple: #A78BFA;
        --accent-green: #3FB950;
        --accent-amber: #D29922;
    }

    html, body, .stApp, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    /* ── Header ── */
    .dashboard-header {
        padding: 1.5rem 0 1.25rem 0;
        border-bottom: 1px solid var(--border-muted);
        margin-bottom: 1.75rem;
    }
    .dashboard-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.025em;
        margin: 0;
        line-height: 1.3;
    }
    .dashboard-subtitle {
        font-size: 0.8rem;
        color: var(--text-muted);
        font-weight: 400;
        margin-top: 0.3rem;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    /* ── Metric cards ── */
    [data-testid="stMetric"] {
        background: var(--bg-secondary);
        border: 1px solid var(--border-muted);
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        transition: border-color 0.15s ease, background 0.15s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: var(--border);
        background: var(--bg-tertiary);
    }
    [data-testid="stMetricLabel"] p {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-secondary) !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Inter', sans-serif !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        color: var(--text-primary) !important;
    }

    /* ── Section headers ── */
    .section-header {
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text-primary);
        letter-spacing: -0.01em;
        margin: 1.25rem 0 0.75rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--border-muted);
    }

    /* ── Dataframe ── */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    /* ── Dividers ── */
    hr { border-color: var(--border-muted) !important; margin: 1.25rem 0 !important; }

    /* ── Plotly charts ── */
    .stPlotlyChart { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ─── Chart constants ─────────────────────────────────────────────
_GRID = dict(gridcolor="#21262D", zerolinecolor="#21262D")

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#8B949E", size=12),
    margin=dict(l=0, r=0, t=36, b=0),
    coloraxis_showscale=False,
    hoverlabel=dict(
        bgcolor="#1C2333",
        bordercolor="#30363D",
        font=dict(family="Inter, sans-serif", color="#E6EDF3", size=13),
    ),
)

BLUE_SCALE = [
    [0.0, "#0D2847"], [0.25, "#163D6B"], [0.5, "#1F5A97"],
    [0.75, "#3679CA"], [1.0, "#58A6FF"],
]

SEGMENT_COLORS = {
    "Champions":       "#D29922",
    "Loyal Customers": "#A78BFA",
    "Potential":       "#58A6FF",
    "Hibernating":     "#3FB950",
}


# ─── Data loading ─────────────────────────────────────────────────
def get_analyzer():
    loader = EcommerceDataLoader()
    return SalesAnalyzer(loader)

@st.cache_data
def get_summary_metrics():
    analyzer = get_analyzer()
    metrics = analyzer.summary_metrics()
    analyzer.loader.close()
    return metrics

@st.cache_data
def get_monthly_revenue():
    analyzer = get_analyzer()
    df = analyzer.monthly_revenue()
    analyzer.loader.close()
    return df

@st.cache_data
def get_top_categories():
    analyzer = get_analyzer()
    df = analyzer.top_categories()
    analyzer.loader.close()
    return df

@st.cache_data
def get_rfm_segments():
    analyzer = get_analyzer()
    df = analyzer.rfm_segments()
    analyzer.loader.close()
    return df



# ─── Header ───────────────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
    <p class="dashboard-title">E-Commerce Analytics</p>
    <p class="dashboard-subtitle">Olist Brasil &middot; 2016 – 2018 &middot; Sales Intelligence</p>
</div>
""", unsafe_allow_html=True)


# ─── Top-level metrics ────────────────────────────────────────────
metrics = get_summary_metrics()

c1, c2, c3, c4 = st.columns(4, gap="medium")
c1.metric("Total Orders",    f"{int(metrics['total_orders']):,}")
c2.metric("Total Revenue",   f"R$ {metrics['total_revenue']:,.0f}")
c3.metric("Total Customers", f"{int(metrics['total_customers']):,}")
c4.metric("Avg Rating",      f"{metrics['avg_rating']:.2f} / 5.00")


# ─── Revenue trend ────────────────────────────────────────────────
st.markdown('<p class="section-header">Revenue Trend</p>', unsafe_allow_html=True)

revenue_df = get_monthly_revenue()

fig_rev = go.Figure()
fig_rev.add_trace(go.Scatter(
    x=revenue_df["month"], y=revenue_df["revenue"],
    mode="lines+markers",
    line=dict(color="#58A6FF", width=2.5, shape="spline"),
    marker=dict(size=5, color="#58A6FF"),
    fill="tozeroy",
    fillcolor="rgba(88, 166, 255, 0.06)",
    hovertemplate="<b>%{x}</b><br>Revenue: R$ %{y:,.0f}<extra></extra>",
))
fig_rev.update_layout(
    **CHART_LAYOUT, height=340, showlegend=False,
    xaxis_title=None, yaxis_title="Revenue (R$)",
    xaxis=_GRID, yaxis={**_GRID, "tickformat": ",.0f"},
)
st.plotly_chart(fig_rev)


# ─── Two-column: categories + segments ───────────────────────────
left, right = st.columns(2, gap="medium")

with left:
    st.markdown('<p class="section-header">Top 10 Categories</p>', unsafe_allow_html=True)
    cat_df = get_top_categories()

    fig_cat = go.Figure(go.Bar(
        x=cat_df["total_revenue"], y=cat_df["category"],
        orientation="h",
        marker=dict(
            color=cat_df["total_revenue"],
            colorscale=BLUE_SCALE,
            line=dict(width=0),
            cornerradius=3,
        ),
        hovertemplate="<b>%{y}</b><br>Revenue: R$ %{x:,.0f}<extra></extra>",
    ))
    fig_cat.update_layout(
        **CHART_LAYOUT, height=400,
        xaxis_title="Revenue (R$)", yaxis_title=None,
        yaxis=dict(categoryorder="total ascending", gridcolor="rgba(0,0,0,0)"),
        xaxis={**_GRID, "tickformat": ",.0f"},
    )
    st.plotly_chart(fig_cat)

with right:
    st.markdown('<p class="section-header">Customer Segments (RFM)</p>', unsafe_allow_html=True)
    rfm_df = get_rfm_segments()
    seg_counts = rfm_df["segment"].value_counts().reset_index()
    seg_counts.columns = ["segment", "count"]

    fig_seg = go.Figure(go.Pie(
        labels=seg_counts["segment"], values=seg_counts["count"],
        hole=0.58,
        marker=dict(
            colors=[SEGMENT_COLORS.get(s, "#58A6FF") for s in seg_counts["segment"]],
            line=dict(color="#0D1117", width=2.5),
        ),
        textposition="inside",
        textinfo="percent",
        textfont=dict(size=13, color="#E6EDF3", family="Inter, sans-serif"),
        hovertemplate="<b>%{label}</b><br>Customers: %{value:,}<br>Share: %{percent}<extra></extra>",
    ))
    fig_seg.update_layout(
        **CHART_LAYOUT, height=400,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.12,
            xanchor="center", x=0.5,
            font=dict(size=12, color="#8B949E"),
        ),
    )
    st.plotly_chart(fig_seg)


# ─── Order volume ─────────────────────────────────────────────────
st.markdown('<p class="section-header">Monthly Order Volume</p>', unsafe_allow_html=True)

fig_vol = go.Figure(go.Bar(
    x=revenue_df["month"], y=revenue_df["total_orders"],
    marker=dict(
        color=revenue_df["total_orders"],
        colorscale=BLUE_SCALE,
        line=dict(width=0),
        cornerradius=3,
    ),
    hovertemplate="<b>%{x}</b><br>Orders: %{y:,}<extra></extra>",
))
fig_vol.update_layout(
    **CHART_LAYOUT, height=260, showlegend=False,
    xaxis_title=None, yaxis_title="Orders",
    xaxis=_GRID, yaxis={**_GRID, "tickformat": ","},
)
st.plotly_chart(fig_vol)


# ─── Segment table ────────────────────────────────────────────────
st.markdown('<p class="section-header">Segment Breakdown</p>', unsafe_allow_html=True)

summary = rfm_df.groupby("segment").agg(
    Customer_Count=("customer_id", "count"),
    Avg_Recency=("recency_days", "mean"),
    Avg_Frequency=("frequency", "mean"),
    Avg_Monetary=("monetary", "mean"),
).round(1).reset_index()

summary = summary.rename(columns={
    "segment": "Segment",
    "Customer_Count": "Customers",
    "Avg_Recency": "Avg Recency (days)",
    "Avg_Frequency": "Avg Frequency",
    "Avg_Monetary": "Avg Monetary (R$)",
})

st.dataframe(
    summary, hide_index=True,
    column_config={
        "Customers": st.column_config.NumberColumn(format="%d"),
        "Avg Recency (days)": st.column_config.NumberColumn(format="%.0f"),
        "Avg Frequency": st.column_config.NumberColumn(format="%.1f"),
        "Avg Monetary (R$)": st.column_config.NumberColumn(format="R$ %.2f"),
    },
)


# ─── Footer ───────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:2rem 0 1rem; border-top:1px solid #21262D; margin-top:2rem;">
    <span style="font-size:0.72rem; color:#484F58; letter-spacing:0.03em;">
        Vugar Mirzoyev
    </span>
</div>
""", unsafe_allow_html=True)