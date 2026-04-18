# 📈 Real-Time Stock Market Dashboard

An interactive stock market dashboard built with Python, Streamlit, and Plotly. Track live stock prices, visualize trends, and analyze financial indicators.

## ✨ Features

- ✅ Real-time stock price data (via Alpha Vantage API)
- ✅ Candlestick, Line & Area chart types
- ✅ Volume bar chart (color-coded green/red)
- ✅ 7-day and 20-day Moving Averages
- ✅ Compare multiple stocks side by side
- ✅ Key statistics (High, Low, Volatility, Period Return)
- ✅ Download stock data as CSV
- ✅ Demo mode with simulated data (works without API key)
- ✅ Dark themed professional UI

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python + Streamlit | Web app framework |
| Plotly | Interactive charts |
| Pandas | Data manipulation |
| Requests | API calls |
| Alpha Vantage API | Stock market data |

## 📁 Project Structure

```
stock-dashboard/
├── app.py               # Main Streamlit application
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

## 🚀 Setup & Run

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/stock-dashboard.git
cd stock-dashboard
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Get a free API key
- Visit [alphavantage.co](https://www.alphavantage.co/support/#api-key)
- Get your free API key
- Replace `API_KEY = "demo"` in `app.py` with your key

### 4. Run the app
```bash
streamlit run app.py
```

### 5. Open your browser
```
http://localhost:8501
```

## 📊 Supported Stocks

Apple (AAPL), Microsoft (MSFT), Google (GOOGL), Amazon (AMZN), Tesla (TSLA), Meta (META), Netflix (NFLX), NVIDIA (NVDA)

## 📸 Dashboard Sections

| Section | Description |
|---|---|
| Key Metrics | Current price, open, high, low, volume |
| Price Chart | Candlestick / Line / Area chart |
| Volume Chart | Daily trading volume |
| Moving Averages | 7-day and 20-day MA overlays |
| Statistics | Period high/low, volatility, return % |
| Raw Data Table | Full data with CSV download |

---

Built as part of the Codec Technologies Internship Projects.
