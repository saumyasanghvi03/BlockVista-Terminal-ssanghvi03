# app.py
import streamlit as st
import pandas as pd
from kiteconnect import KiteConnect
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
import os

# Load secrets from Streamlit Cloud
API_KEY = st.secrets.get("API_KEY")
ACCESS_TOKEN = st.secrets.get("ACCESS_TOKEN")

# Validate secrets
if not API_KEY or not ACCESS_TOKEN:
    st.error("API_KEY or ACCESS_TOKEN not found in Streamlit secrets. Please configure in Streamlit Cloud settings.")
    st.stop()

# Load sectors.csv
sectors_df = None
if os.path.exists("sectors.csv"):
    sectors_df = pd.read_csv("sectors.csv")

# PWA meta tags
st.markdown("""
<link rel="manifest" href="/manifest.json">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
<meta name="apple-mobile-web-app-title" content="BlockVista">
<link rel="apple-touch-icon" href="https://img.icons8.com/color/180/000000/india.png">
""", unsafe_allow_html=True)

# Custom CSS
css = """
body {
    font-family: 'Arial', sans-serif;
}
h1, h2, h3 {
    color: #FF4B4B;
}
.stButton>button {
    background-color: #3776AB;
    color: white;
    border-radius: 5px;
}
.stMetric {
    background-color: #f0f2f6;
    padding: 10px;
    border-radius: 5px;
}
.stSidebar {
    background-color: #f8f9fa;
}
"""
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Page config
st.set_page_config(
    page_title="BlockVista Terminal™",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Utility functions
@st.cache_data
def get_instruments(kite):
    instruments = kite.instruments()
    return pd.DataFrame(instruments)

def symbol_to_token(kite, symbol, exchange="NSE"):
    instruments = get_instruments(kite)
    try:
        token = instruments[
            (instruments.tradingsymbol == symbol) & 
            (instruments.exchange == exchange)
        ]['instrument_token'].iloc[0]
        return int(token)
    except:
        return None

# Technical indicators using numpy
def calculate_sma(data, period=20):
    return pd.Series(data).rolling(window=period).mean()

def calculate_ema(data, period=20):
    return pd.Series(data).ewm(span=period, adjust=False).mean()

def calculate_rsi(data, period=14):
    delta = pd.Series(data).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rs = rs.replace([np.inf, -np.inf], np.nan).fillna(0)
    return 100 - (100 / (1 + rs))

# Initialize KiteConnect
@st.cache_resource
def init_kite():
    kite = KiteConnect(api_key=API_KEY)
    kite.set_access_token(ACCESS_TOKEN)
    return kite

# Sidebar
st.sidebar.title("BlockVista Terminal™")
st.sidebar.markdown("🇮🇳 Empowering Indian Traders")
st.sidebar.image("https://img.icons8.com/color/48/000000/india.png")

kite = None
try:
    kite = init_kite()
    st.sidebar.success("Connected to Zerodha Kite")
except Exception as e:
    st.sidebar.error(f"Connection failed: {e}")
    st.stop()

# Language selection
lang = st.sidebar.selectbox("Language", ["English", "Hindi"])
if lang == "Hindi":
    st.sidebar.markdown("🚀 ब्लॉकविस्टा टर्मिनल: भारतीय ट्रेडर्स के लिए")

# Navigation
page = st.sidebar.selectbox(
    "Navigate",
    ["Live Quotes", "Historical Data", "Portfolio Tracker", "Market Screener", "Options Analytics"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 Saumya & Kanishk | FinX Institute")
st.sidebar.markdown("[Contribute on GitHub](https://github.com/your-repo/blockvista-terminal)")

# Main content
if page == "Live Quotes":
    st.header("🕐 Live Quotes")
    st.markdown("Monitor real-time market data with customizable watchlist.")
    
    col1, col2 = st.columns([3,1])
    with col1:
        watchlist = st.text_area("Enter symbols (comma-separated, e.g., RELIANCE,TCS)", "RELIANCE,TCS")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Fetch Quotes"):
            symbols = [s.strip().upper() for s in watchlist.split(",")]
            quotes = []
            for symbol in symbols:
                token = symbol_to_token(kite, symbol)
                if token:
                    try:
                        quote = kite.quote(token)
                        q = quote[str(token)]
                        q['symbol'] = symbol
                        quotes.append(q)
                    except Exception as e:
                        st.error(f"Error fetching {symbol}: {e}")
            
            if quotes:
                df = pd.DataFrame(quotes)
                st.dataframe(df[['symbol', 'last_price', 'change', 'volume', 'oi']], use_container_width=True)
                
                cols = st.columns(4)
                for i, row in enumerate(df.itertuples()):
                    with cols[i % 4]:
                        delta_color = "normal" if row.change >= 0 else "inverse"
                        st.metric(row.symbol, f"₹{row.last_price:.2f}", f"{row.change:.2f}%", delta_color=delta_color)

    with st.expander("Market Depth"):
        selected_symbol = st.selectbox("Select Symbol for Depth", symbols if 'symbols' in locals() else [])
        if selected_symbol:
            token = symbol_to_token(kite, selected_symbol)
            if token:
                depth = kite.quote(token)[str(token)].get('depth', {})
                st.subheader("Buy Orders")
                st.dataframe(pd.DataFrame(depth.get('buy', [])))
                st.subheader("Sell Orders")
                st.dataframe(pd.DataFrame(depth.get('sell', [])))

elif page == "Historical Data":
    st.header("📊 Historical Data & Technicals")
    st.markdown("Analyze past market trends with advanced charting and indicators.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        symbol = st.text_input("Symbol (e.g., RELIANCE)", "RELIANCE")
    with col2:
        interval = st.selectbox("Interval", ["minute", "5minute", "day", "week"])
    with col3:
        periods = st.multiselect("Technical Indicators", ["SMA (20)", "EMA (20)", "RSI (14)"])
    
    col4, col5 = st.columns(2)
    with col4:
        from_date = st.date_input("From", datetime.now() - timedelta(days=30))
    with col5:
        to_date = st.date_input("To", datetime.now())
    
    if st.button("Fetch & Chart"):
        token = symbol_to_token(kite, symbol)
        if token:
            try:
                hist_data = kite.historical_data(
                    instrument_token=token,
                    from_date=from_date,
                    to_date=to_date,
                    interval=interval
                )
                df = pd.DataFrame(hist_data)
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                    
                    fig = px.line(df, x='date', y='close', title=f"{symbol} Historical Price", height=600)
                    fig.update_layout(xaxis_title="Date", yaxis_title="Price", hovermode="x unified")
                    
                    close = df['close']
                    for period in periods:
                        if "SMA" in period:
                            sma = calculate_sma(close)
                            df['SMA'] = sma
                            fig.add_scatter(x=df['date'], y=df['SMA'], name="SMA 20", line=dict(color='orange'))
                        if "EMA" in period:
                            ema = calculate_ema(close)
                            df['EMA'] = ema
                            fig.add_scatter(x=df['date'], y=df['EMA'], name="EMA 20", line=dict(color='green'))
                        if "RSI" in period:
                            rsi = calculate_rsi(close)
                            df['RSI'] = rsi
                            rsi_fig = px.line(df, x='date', y='RSI', title="RSI (14)", height=300)
                            rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
                            rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
                            st.plotly_chart(rsi_fig, use_container_width=True)
                    
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")

    with st.expander("Download Data"):
        if 'df' in locals():
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", csv, f"{symbol}_historical.csv", "text/csv")

elif page == "Portfolio Tracker":
    st.header("💼 Portfolio Tracker")
    st.markdown("Track your holdings, calculate real-time P&L, and visualize allocation.")
    
    uploaded_file = st.file_uploader("Upload Holdings CSV (Symbol,Qty,AvgPrice)", type="csv")
    holdings = None
    if uploaded_file:
        holdings = pd.read_csv(uploaded_file)
        st.dataframe(holdings, use_container_width=True)
    
    if holdings is not None:
        total_pl = 0
        current_values = []
        for _, row in holdings.iterrows():
            symbol = row['Symbol']
            token = symbol_to_token(kite, symbol)
            if token:
                try:
                    quote = kite.quote(token)
                    current_price = quote[str(token)]['last_price']
                    pl = (current_price - row['AvgPrice']) * row['Qty']
                    total_pl += pl
                    current_values.append({
                        'Symbol': symbol,
                        'Current Price': current_price,
                        'P&L': pl
                    })
                except:
                    st.error(f"Error fetching price for {symbol}")
        
        if current_values:
            pl_df = pd.DataFrame(current_values)
            st.dataframe(pl_df, use_container_width=True)
            st.metric("Total P&L", f"₹{total_pl:.2f}", delta_color="normal" if total_pl >= 0 else "inverse")
            
            # Pie chart for allocation
            pl_df['Value'] = pl_df['Current Price'] * holdings['Qty']
            fig = px.pie(pl_df, values='Value', names='Symbol', title="Portfolio Allocation", hole=0.3)
            st.plotly_chart(fig, use_container_width=True)

elif page == "Market Screener":
    st.header("🔍 Market Screener")
    st.markdown("Screen stocks based on criteria, sectors, and performance metrics.")
    
    col1, col2 = st.columns(2)
    with col1:
        criteria = st.multiselect("Filter Criteria", ["High Volume", "Top Gainers", "Top Losers"])
    with col2:
        min_volume = st.number_input("Min Volume", 0, 10000000, 100000)
        if sectors_df is not None:
            sectors = st.multiselect("Sectors", sectors_df['Sector'].unique())
    
    if st.button("Screen Market"):
        instruments = get_instruments(kite)
        nse_stocks = instruments[(instruments.exchange == "NSE") & (instruments.segment == "NSE")]
        results = []
        
        for _, row in nse_stocks.iterrows():
            token = row['instrument_token']
            symbol = row['tradingsymbol']
            sector = sectors_df[sectors_df['Symbol'] == symbol]['Sector'].iloc[0] if sectors_df is not None and symbol in sectors_df['Symbol'].values else None
            
            if sectors and sector not in sectors:
                continue
            
            try:
                quote = kite.quote(token)
                q = quote[str(token)]
                q['symbol'] = symbol
                q['sector'] = sector
                
                match = True
                if "High Volume" in criteria and q.get('volume', 0) < min_volume:
                    match = False
                if "Top Gainers" in criteria and q.get('change', 0) <= 0:
                    match = False
                if "Top Losers" in criteria and q.get('change', 0) >= 0:
                    match = False
                
                if match:
                    results.append(q)
            except:
                continue
        
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df[['symbol', 'sector', 'last_price', 'change', 'volume']], use_container_width=True)
            
            # Bar chart for top changes
            top_gainers = df[df['change'] > 0].sort_values('change', ascending=False).head(10)
            fig = px.bar(top_gainers, x='symbol', y='change', title="Top Gainers", color='change')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No stocks match the criteria.")

elif page == "Options Analytics":
    st.header("🔗 Options Analytics")
    st.markdown("Analyze options chains, Greeks, and implied volatility.")
    
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input("Underlying Symbol (e.g., NIFTY)", "NIFTY")
    with col2:
        expiry = st.date_input("Expiry Date", datetime.now() + timedelta(days=7))
    
    if st.button("Fetch Options Chain"):
        instruments = get_instruments(kite)
        options = instruments[
            (instruments.tradingsymbol.str.startswith(symbol)) &
            (instruments.expiry == expiry) &
            (instruments.instrument_type.isin(["CE", "PE"]))
        ]
        
        if not options.empty:
            st.dataframe(options[['tradingsymbol', 'strike', 'instrument_type', 'expiry']], use_container_width=True)
            
            # Placeholder for Greeks
            st.subheader("Greeks & IV (Placeholder)")
            st.info("Advanced Greeks calculations: Delta, Gamma, Theta, Vega, Rho. Coming soon!")
            
            # Chain visualization
            ce = options[options.instrument_type == "CE"].sort_values('strike')
            pe = options[options.instrument_type == "PE"].sort_values('strike')
            fig = px.line(ce, x='strike', y='lot_size', title="Call Options", labels={'lot_size': 'Lot Size'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No options found for the selected criteria.")
