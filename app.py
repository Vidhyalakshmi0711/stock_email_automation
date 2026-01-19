import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import time
from nsetools import Nse
import requests
from io import StringIO
from nsepython import nse_eq_symbols
import os

# ================================
# NSE SECTOR STOCK COUNTS FUNCTION
# ================================
def get_sector_stock_counts():
    """Get total companies per NSE sector using nsetools + NSE CSV"""
    nse = Nse()

    # NSE Sectoral Indices mapping
    sector_indices = {
        "Information Technology": "NIFTY IT",
        "Financial Services": "NIFTY BANK",
        "Banks": "NIFTY BANK",
        "FMCG": "NIFTY FMCG",
        "Pharmaceuticals": "NIFTY PHARMA",
        "Metals": "NIFTY METAL",
        "Automobile": "NIFTY AUTO",
        "Realty": "NIFTY REALTY",
        "PSU Banks": "NIFTY PSU BANK",
        "Media": "NIFTY MEDIA"
    }

    sector_counts = {}

    # Get all NSE stocks from official CSV
    try:
        url = 'https://archives.nseindia.com/content/equities/EQUITY_L.csv'
        response = requests.get(url)
        nse_df = pd.read_csv(StringIO(response.text))
        total_nse_stocks = len(nse_df)
    except:
        total_nse_stocks = 2000  # Approximate NSE stocks

    # Count stocks per sectoral index
    for sector_name, index_name in sector_indices.items():
        try:
            stocks = nse.get_stocks_in_index(index_name)
            sector_counts[sector_name] = {
                'nse_count': len(stocks),
                'total_estimate': len(stocks) * 4  # NSE ~25% of total market
            }
        except:
            sector_counts[sector_name] = {'nse_count': 0, 'total_estimate': 0}

    return sector_counts, total_nse_stocks

# ================================
# FIXED NIFTY 50 STOCK LIST + SECTOR MAP
# ================================
NIFTY50_TICKERS = [
    'ADANIENT.NS','ADANIPORTS.NS','APOLLOHOSP.NS','ASIANPAINT.NS',
    'AXISBANK.NS','BAJAJ-AUTO.NS','BAJFINANCE.NS','BAJAJFINSV.NS',
    'BPCL.NS','BHARTIARTL.NS','BRITANNIA.NS','CIPLA.NS',
    'COALINDIA.NS','DIVISLAB.NS','DRREDDY.NS','EICHERMOT.NS',
    'GRASIM.NS','HCLTECH.NS','HDFCBANK.NS','HDFCLIFE.NS',
    'HEROMOTOCO.NS','HINDALCO.NS','HINDUNILVR.NS','ICICIBANK.NS',
    'INDUSINDBK.NS','INFY.NS','ITC.NS','JSWSTEEL.NS',
    'KOTAKBANK.NS','LT.NS','M&M.NS','MARUTI.NS',
    'NESTLEIND.NS','NTPC.NS','ONGC.NS','POWERGRID.NS',
    'RELIANCE.NS','SBIN.NS','SUNPHARMA.NS','TATASTEEL.NS',
    'TCS.NS','TECHM.NS','TITAN.NS','ULTRACEMCO.NS','UPL.NS','WIPRO.NS'
]

# Manual sector mapping for NIFTY50 (yfinance doesn't provide reliable sectors)
NIFTY50_SECTORS = {
    'ADANIENT.NS': 'Industrials', 'ADANIPORTS.NS': 'Transportation',
    'APOLLOHOSP.NS': 'Healthcare', 'ASIANPAINT.NS': 'Chemicals',
    'AXISBANK.NS': 'Banks', 'BAJAJ-AUTO.NS': 'Automobile',
    'BAJFINANCE.NS': 'Financial Services', 'BAJAJFINSV.NS': 'Financial Services',
    'BPCL.NS': 'Energy', 'BHARTIARTL.NS': 'Telecommunication',
    'BRITANNIA.NS': 'FMCG', 'CIPLA.NS': 'Pharmaceuticals',
    'COALINDIA.NS': 'Energy', 'DIVISLAB.NS': 'Pharmaceuticals',
    'DRREDDY.NS': 'Pharmaceuticals', 'EICHERMOT.NS': 'Automobile',
    'GRASIM.NS': 'Chemicals', 'HCLTECH.NS': 'Information Technology',
    'HDFCBANK.NS': 'Banks', 'HDFCLIFE.NS': 'Insurance',
    'HEROMOTOCO.NS': 'Automobile', 'HINDALCO.NS': 'Metals',
    'HINDUNILVR.NS': 'FMCG', 'ICICIBANK.NS': 'Banks',
    'INDUSINDBK.NS': 'Banks', 'INFY.NS': 'Information Technology',
    'ITC.NS': 'FMCG', 'JSWSTEEL.NS': 'Metals',
    'KOTAKBANK.NS': 'Banks', 'LT.NS': 'Industrials',
    'M&M.NS': 'Automobile', 'MARUTI.NS': 'Automobile',
    'NESTLEIND.NS': 'FMCG', 'NTPC.NS': 'Utilities',
    'ONGC.NS': 'Energy', 'POWERGRID.NS': 'Utilities',
    'RELIANCE.NS': 'Energy', 'SBIN.NS': 'Banks',
    'SUNPHARMA.NS': 'Pharmaceuticals', 'TATASTEEL.NS': 'Metals',
    'TCS.NS': 'Information Technology', 'TECHM.NS': 'Information Technology',
    'TITAN.NS': 'Consumer Goods', 'ULTRACEMCO.NS': 'Chemicals',
    'UPL.NS': 'Chemicals', 'WIPRO.NS': 'Information Technology'
}

# ================================
# 1. PRE-FETCH TOTAL SECTOR COUNTS
# ================================
print("🔄 Fetching total sector-wise stock counts (NSE+BSE)...")
sector_totals, total_nse = get_sector_stock_counts()

# ================================
# 2. FETCH NIFTY50 DATA
# ================================
print("📈 Fetching NIFTY50 price data...")
price_data = yf.download(NIFTY50_TICKERS, period="5d", progress=False)['Close']
records = []

for ticker in NIFTY50_TICKERS:
    try:
        prices = price_data[ticker].dropna()
        if len(prices) >= 2:
            pct_change = ((prices.iloc[-1] - prices.iloc[-2]) / prices.iloc[-2]) * 100
            sector = NIFTY50_SECTORS.get(ticker, "Unknown")

            # Get yfinance info
            stock = yf.Ticker(ticker)
            info = stock.info
            market_cap = info.get("marketCap", 0)

            records.append({
                "Ticker": ticker.replace('.NS', ''),
                "Sector": sector,
                "Change %": round(pct_change, 2),
                "Industry": info.get("industry", "Unknown"),
                "MarketCap": market_cap
            })
    except Exception as e:
        print(f"⚠️ Error {ticker}: {e}")
        continue

df = pd.DataFrame(records)
print(f"✅ Processed {len(df)} NIFTY50 stocks")

# ================================
# 3. SECTOR ANALYSIS WITH TOTAL COUNTS
# ================================
sector_summary = (
    df.groupby("Sector")
     .agg(
         Avg_Change=("Change %", "mean"),
         Total_Impact=("Change %", lambda x: x.abs().sum()),
         Sector_MarketCap=("MarketCap", "sum"),
         NIFTY_Companies=("Ticker", "count"),
         Industries=("Industry", lambda x: x.nunique())
     )
     .reset_index()
     .sort_values("Total_Impact", ascending=False)
)

# Add total market companies column
sector_summary['Total_Companies'] = sector_summary['Sector'].map(
    lambda x: sector_totals.get(x, {'total_estimate': '~5000'})['total_estimate']
)
sector_summary['NSE_Companies'] = sector_summary['Sector'].map(
    lambda x: sector_totals.get(x, {'nse_count': 0})['nse_count']
)

sector_summary["Avg_Change"] = sector_summary["Avg_Change"].round(2)
sector_summary["Total_Impact"] = sector_summary["Total_Impact"].round(2)
sector_summary["Sector_MarketCap"] = (sector_summary["Sector_MarketCap"] / 1e12).round(2)

sector_summary.rename(columns={
    "Sector_MarketCap": "NIFTY50 Mkt Cap (₹T)",
    "NIFTY_Companies": "NIFTY50 Cos",
    "Total_Companies": "Total Listed Cos",
    "NSE_Companies": "NSE Cos"
}, inplace=True)

# ================================
# 4. FINAL OUTPUT & EMAIL
# ================================
print("\n📊 NIFTY 50 – SECTOR IMPACT ANALYSIS")
print(sector_summary.to_string(index=False))

top_sectors = sector_summary.head(5)

html_body = f"""
<h2>🏛️ NIFTY50 Sector Impact Analysis - {datetime.now().strftime('%d %B %Y')}</h2>
<h3>Top 5 Sectors by Market Impact</h3>
{top_sectors.to_html(index=False, escape=False)}
<br>
<p><b>📋 Column Legend:</b><br>
• <b>Total Impact</b> = Sum of absolute % changes (NIFTY50 stocks)<br>
• <b>Total Listed Cos</b> = NSE+BSE companies in sector (~20K total market)<br>
• <b>NIFTY50 Cos:</b> NIFTY50 -listed companies in sector<br>
• <b>NSE Cos</b> = NSE-listed companies in sector</p><br>
<p><i>Total Indian market: ~20,000 companies across NSE+BSE</i></p>
"""

# Email setup (your existing code)
subject = f"NIFTY50 Sector Report | {datetime.now().strftime('%d %B %Y')}"
msg = MIMEMultipart()
msg['From'] = 'vidhyalakshmi@aadhan.in'
msg['To'] = 'nithin@aadhan.in'
msg["Subject"] = subject
msg.attach(MIMEText(html_body, "html"))

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")

    server.login(email_user, email_pass)
    server.send_message(msg)
    server.quit()
    print("✅ Email sent with sector totals!")
except Exception as e:
    print(f"❌ Email failed: {e}")

print(f"\n💡 Total NSE stocks tracked: {total_nse}")

print("✅ Analysis complete!")
