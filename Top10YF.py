import os
import pandas as pd
from tiingo import TiingoClient
from datetime import datetime, timedelta

# Setup Tiingo
config = {
    'session': True,
    'api_key': 'TIINGO_API_KEY'
}
client = TiingoClient(config)

# Improved AI Top 10 list
tickers = [
    'NVDA',   # Nvidia
    'MSFT',   # Microsoft
    'GOOGL',  # Google
    'META',   # Meta
    'AMD',    # AMD
    'TSM',    # Taiwan Semi
    'AVGO',   # Broadcom
    'PLTR',   # Palantir
    'AMZN',   # Amazon
    'SMCI',   # Super Micro Computer
]

today = datetime.today()
start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
end_date = today.strftime('%Y-%m-%d')

# Output path
os.makedirs("data", exist_ok=True)
output_file = "data/ai_stock_data.csv"

all_data = []

for ticker in tickers:
    try:
        df = client.get_dataframe(
            ticker,
            frequency='daily',
            startDate=start_date,
            endDate=end_date
        )

        df['Ticker'] = ticker
        df['% Change (1d)'] = df['close'].pct_change(1) * 100
        df['% Change (5d)'] = df['close'].pct_change(5) * 100
        df['Rolling Volatility'] = df['close'].rolling(window=5).std()

        df.reset_index(inplace=True)
        all_data.append(df[['date', 'Ticker', 'close', 'high', 'low', 'volume',
                            '% Change (1d)', '% Change (5d)', 'Rolling Volatility']])
        
    except Exception as e:
        print(f"{ticker} failed: {e}")

# Combine
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    final_df.columns = ['Date', 'Ticker', 'Close', 'High', 'Low', 'Volume',
                        '% Change (1d)', '% Change (5d)', 'Rolling Volatility']
    final_df['Date'] = pd.to_datetime(final_df['Date'])

    # Only save if new data is different
    if not os.path.exists(output_file) or not final_df.equals(pd.read_csv(output_file, parse_dates=["Date"])):
        final_df.to_csv(output_file, index=False)
        print("✅ Data updated and saved.")
    else:
        print("⚠️ No changes detected. File not overwritten.")
else:
    print("❌ No data fetched.")
