import os
import requests
import pandas as pd

ALPHA_VANTAGE_API_KEY = "3XBLX90HGTEW98C3"


def get_stock_data(symbol, interval="1min"):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&apikey={ALPHA_VANTAGE_API_KEY}"
    response = requests.get(url)
    data = response.json()

    # Check for errors in the response
    if "Time Series (1min)" not in data:
        print("Error in API response:", data.get("Note") or data.get("Error Message") or data)
        return None

    df2 = pd.DataFrame(data['Time Series (1min)']).T
    df2.columns = ['open', 'high', 'low', 'close', 'volume']
    return df2


# Fetch data
df = get_stock_data("AAPL")  # Use a valid stock ticker
if df is not None:
    # Ensure the 'data' directory exists
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/aapl_stock_data.csv")
    print("Data saved successfully.")
else:
    print("Failed to fetch stock data.")
