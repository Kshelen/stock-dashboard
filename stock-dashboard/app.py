import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
from datetime import datetime, timedelta
import time

# ─── Page Config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Stock Market Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background-color: #0a0a0f;
        color: #e2e8f0;
    }

    .metric-card {
        background: #111118;
        border: 1px solid #1e1e2e;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }

    .metric-label {
        font-family: 'Space Mono', monospace;
        font-size: 10px;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 8px;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #e2e8f0;
    }

    .metric-change-positive {
        font-size: 14px;
        color: #6ee7b7;
        font-weight: 500;
    }

    .metric-change-negative {
        font-size: 14px;
        color: #f87171;
        font-weight: 500;
    }

    .section-title {
        font-family: 'Space Mono', monospace;
        font-size: 11px;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #64748b;
        margin: 24px 0 12px 0;
    }

    .badge {
        display: inline-block;
        background: rgba(110,231,183,0.1);
        border: 1px solid rgba(110,231,183,0.2);
        color: #6ee7b7;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-family: 'Space Mono', monospace;
    }

    .stSelectbox > div > div {
        background: #111118;
        border: 1px solid #1e1e2e;
        color: #e2e8f0;
    }

    div[data-testid="metric-container"] {
        background: #111118;
        border: 1px solid #1e1e2e;
        border-radius: 12px;
        padding: 16px 20px;
    }

    .stSidebar {
        background: #111118;
    }

    h1, h2, h3 { color: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)

# ─── Alpha Vantage API ────────────────────────────────────────────────────────
# Using free demo key — for real use, get a free key at alphavantage.co

API_KEY = "demo"  # Replace with your free key from alphavantage.co
BASE_URL = "https://www.alphavantage.co/query"

# Popular stocks list
STOCKS = {
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Google (GOOGL)": "GOOGL",
    "Amazon (AMZN)": "AMZN",
    "Tesla (TSLA)": "TSLA",
    "Meta (META)": "META",
    "Netflix (NFLX)": "NFLX",
    "NVIDIA (NVDA)": "NVDA",
}

# ─── Data Fetching ────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_stock_data(symbol):
    """Fetch daily stock data from Alpha Vantage"""
    try:
        url = f"{BASE_URL}?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}&outputsize=compact"
        response = requests.get(url, timeout=10)
        data = response.json()

        if "Time Series (Daily)" not in data:
            return None, None

        ts = data["Time Series (Daily)"]
        df = pd.DataFrame(ts).T
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.columns = ["Open", "High", "Low", "Close", "Volume"]
        df = df.astype(float)
        df = df.tail(60)  # Last 60 days

        meta = data.get("Meta Data", {})
        return df, meta

    except Exception as e:
        return None, None

@st.cache_data(ttl=300)
def fetch_quote(symbol):
    """Fetch latest quote"""
    try:
        url = f"{BASE_URL}?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        quote = data.get("Global Quote", {})
        return quote
    except:
        return {}

def generate_demo_data(symbol):
    """Generate realistic demo data when API limit is reached"""
    import numpy as np
    np.random.seed(hash(symbol) % 100)

    base_prices = {
        "AAPL": 175, "MSFT": 415, "GOOGL": 165, "AMZN": 185,
        "TSLA": 175, "META": 505, "NFLX": 625, "NVDA": 875
    }
    base = base_prices.get(symbol, 150)

    dates = pd.date_range(end=datetime.today(), periods=60, freq='B')
    prices = [base]
    for _ in range(59):
        change = np.random.normal(0, 0.015)
        prices.append(prices[-1] * (1 + change))

    df = pd.DataFrame({
        "Open":   [p * (1 - abs(np.random.normal(0, 0.003))) for p in prices],
        "High":   [p * (1 + abs(np.random.normal(0, 0.008))) for p in prices],
        "Low":    [p * (1 - abs(np.random.normal(0, 0.008))) for p in prices],
        "Close":  prices,
        "Volume": [np.random.randint(20_000_000, 80_000_000) for _ in prices]
    }, index=dates)

    return df

# ─── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 📈 Stock Dashboard")
    st.markdown("---")

    selected_label = st.selectbox("Select Stock", list(STOCKS.keys()))
    symbol = STOCKS[selected_label]

    chart_type = st.radio("Chart Type", ["Candlestick", "Line Chart", "Area Chart"])
    period = st.slider("Days to Show", min_value=10, max_value=60, value=30)

    st.markdown("---")
    st.markdown("### 📊 Compare Stocks")
    compare = st.multiselect(
        "Add stocks to compare",
        [v for k, v in STOCKS.items() if v != symbol],
        default=[]
    )

    st.markdown("---")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("""
    <div style='font-size:11px; color:#64748b; margin-top:16px;'>
    Data from Alpha Vantage API<br>
    Demo mode uses simulated data
    </div>
    """, unsafe_allow_html=True)

# ─── Main Content ─────────────────────────────────────────────────────────────

st.markdown(f"# 📈 {selected_label}")
st.markdown(f'<span class="badge">● LIVE DEMO</span> &nbsp; Last updated: {datetime.now().strftime("%b %d, %Y %H:%M")}', unsafe_allow_html=True)
st.markdown("---")

# Fetch data
df, meta = fetch_stock_data(symbol)

# Use demo data if API limit reached
if df is None:
    df = generate_demo_data(symbol)
    st.info("ℹ️ Using simulated demo data. Get a free API key at alphavantage.co and replace `API_KEY` in app.py for live data.")

df = df.tail(period)

# ─── Key Metrics ─────────────────────────────────────────────────────────────

latest = df.iloc[-1]
prev   = df.iloc[-2]
change = latest["Close"] - prev["Close"]
pct    = (change / prev["Close"]) * 100
color  = "#6ee7b7" if change >= 0 else "#f87171"
arrow  = "▲" if change >= 0 else "▼"

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Current Price", f"${latest['Close']:.2f}", f"{arrow} {abs(change):.2f} ({abs(pct):.2f}%)")
with col2:
    st.metric("Open", f"${latest['Open']:.2f}")
with col3:
    st.metric("High", f"${latest['High']:.2f}")
with col4:
    st.metric("Low", f"${latest['Low']:.2f}")
with col5:
    vol = latest['Volume']
    vol_str = f"{vol/1_000_000:.1f}M" if vol > 1_000_000 else f"{vol/1_000:.0f}K"
    st.metric("Volume", vol_str)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Main Chart ───────────────────────────────────────────────────────────────

st.markdown('<div class="section-title">Price Chart</div>', unsafe_allow_html=True)

fig = go.Figure()

if chart_type == "Candlestick":
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"],   close=df["Close"],
        name=symbol,
        increasing_line_color="#6ee7b7",
        decreasing_line_color="#f87171",
    ))
elif chart_type == "Line Chart":
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"],
        mode="lines", name=symbol,
        line=dict(color="#6ee7b7", width=2)
    ))
else:  # Area
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"],
        fill="tozeroy", name=symbol,
        line=dict(color="#6ee7b7", width=2),
        fillcolor="rgba(110,231,183,0.1)"
    ))

# Add comparison stocks
for comp_sym in compare:
    comp_df = generate_demo_data(comp_sym)
    comp_df = comp_df.tail(period)
    fig.add_trace(go.Scatter(
        x=comp_df.index, y=comp_df["Close"],
        mode="lines", name=comp_sym,
        line=dict(width=1.5, dash="dot")
    ))

fig.update_layout(
    paper_bgcolor="#0a0a0f",
    plot_bgcolor="#0a0a0f",
    font=dict(color="#e2e8f0", family="DM Sans"),
    xaxis=dict(gridcolor="#1e1e2e", showgrid=True, zeroline=False),
    yaxis=dict(gridcolor="#1e1e2e", showgrid=True, zeroline=False, tickprefix="$"),
    legend=dict(bgcolor="#111118", bordercolor="#1e1e2e"),
    height=420,
    margin=dict(l=0, r=0, t=10, b=0),
    xaxis_rangeslider_visible=False,
)

st.plotly_chart(fig, use_container_width=True)

# ─── Volume Chart ─────────────────────────────────────────────────────────────

st.markdown('<div class="section-title">Volume</div>', unsafe_allow_html=True)

vol_colors = ["#6ee7b7" if df["Close"].iloc[i] >= df["Open"].iloc[i] else "#f87171"
              for i in range(len(df))]

vol_fig = go.Figure(go.Bar(
    x=df.index, y=df["Volume"],
    marker_color=vol_colors, name="Volume"
))
vol_fig.update_layout(
    paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f",
    font=dict(color="#e2e8f0"),
    xaxis=dict(gridcolor="#1e1e2e"),
    yaxis=dict(gridcolor="#1e1e2e"),
    height=180,
    margin=dict(l=0, r=0, t=0, b=0),
    showlegend=False
)
st.plotly_chart(vol_fig, use_container_width=True)

# ─── Moving Averages + Stats ──────────────────────────────────────────────────

col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown('<div class="section-title">Moving Averages</div>', unsafe_allow_html=True)

    ma_fig = go.Figure()
    ma_fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Price",
        line=dict(color="#e2e8f0", width=1.5)))

    if len(df) >= 7:
        df["MA7"]  = df["Close"].rolling(7).mean()
        ma_fig.add_trace(go.Scatter(x=df.index, y=df["MA7"], name="7-day MA",
            line=dict(color="#6ee7b7", width=1.5, dash="dot")))

    if len(df) >= 20:
        df["MA20"] = df["Close"].rolling(20).mean()
        ma_fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], name="20-day MA",
            line=dict(color="#818cf8", width=1.5, dash="dot")))

    ma_fig.update_layout(
        paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f",
        font=dict(color="#e2e8f0"),
        xaxis=dict(gridcolor="#1e1e2e"),
        yaxis=dict(gridcolor="#1e1e2e", tickprefix="$"),
        legend=dict(bgcolor="#111118", bordercolor="#1e1e2e"),
        height=280, margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(ma_fig, use_container_width=True)

with col_right:
    st.markdown('<div class="section-title">Statistics</div>', unsafe_allow_html=True)

    period_high = df["High"].max()
    period_low  = df["Low"].min()
    avg_vol     = df["Volume"].mean()
    volatility  = df["Close"].pct_change().std() * 100
    total_ret   = ((df["Close"].iloc[-1] - df["Close"].iloc[0]) / df["Close"].iloc[0]) * 100

    stats = {
        f"{period}-Day High": f"${period_high:.2f}",
        f"{period}-Day Low":  f"${period_low:.2f}",
        "Avg Volume":         f"{avg_vol/1_000_000:.1f}M",
        "Volatility":         f"{volatility:.2f}%",
        "Period Return":      f"{'▲' if total_ret >= 0 else '▼'} {abs(total_ret):.2f}%",
    }

    for label, value in stats.items():
        color = "#6ee7b7" if ("▲" in str(value)) else ("#f87171" if "▼" in str(value) else "#e2e8f0")
        st.markdown(f"""
        <div style='display:flex; justify-content:space-between; padding:12px 0;
             border-bottom:1px solid #1e1e2e;'>
            <span style='color:#64748b; font-size:13px;'>{label}</span>
            <span style='color:{color}; font-weight:600; font-size:13px;'>{value}</span>
        </div>
        """, unsafe_allow_html=True)

# ─── Raw Data Table ───────────────────────────────────────────────────────────

st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📋 View Raw Data Table"):
    display_df = df[["Open","High","Low","Close","Volume"]].copy()
    display_df.index = display_df.index.strftime("%Y-%m-%d")
    display_df = display_df.sort_index(ascending=False)
    display_df["Change"] = display_df["Close"].diff(-1).apply(lambda x: f"{'▲' if x < 0 else '▼'} {abs(x):.2f}" if pd.notna(x) else "-")
    st.dataframe(display_df.style.format({
        "Open": "${:.2f}", "High": "${:.2f}",
        "Low": "${:.2f}", "Close": "${:.2f}",
        "Volume": "{:,.0f}"
    }), use_container_width=True)

    csv = display_df.to_csv()
    st.download_button("⬇️ Download as CSV", csv, f"{symbol}_data.csv", "text/csv")

# ─── Footer ───────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#64748b; font-size:12px; font-family: Space Mono, monospace;'>
    STOCK MARKET DASHBOARD &nbsp;·&nbsp; Built with Streamlit + Plotly &nbsp;·&nbsp; Data: Alpha Vantage
</div>
""", unsafe_allow_html=True)
