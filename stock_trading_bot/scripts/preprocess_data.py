import pandas as pd
import numpy as np

# Function to calculate RSI
def calculate_rsi(df, column='close', period=14):
    delta = df[column].diff()  # Calculate price changes
    gain = np.where(delta > 0, delta, 0)  # Keep only positive gains
    loss = np.where(delta < 0, -delta, 0)  # Keep only negative losses

    # Calculate average gains and losses
    avg_gain = pd.Series(gain).rolling(window=period, min_periods=1).mean()
    avg_loss = pd.Series(loss).rolling(window=period, min_periods=1).mean()

    # Compute RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

# Function to calculate MACD
def calculate_macd(df, column='close', fast_period=12, slow_period=26, signal_period=9):
    # Calculate the EMAs
    fast_ema = df[column].ewm(span=fast_period, adjust=False).mean()
    slow_ema = df[column].ewm(span=slow_period, adjust=False).mean()

    # Compute MACD and Signal Line
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

    return macd_line, signal_line

# Example: Applying to a DataFrame
# Load your data
df = pd.read_csv("data/aapl_stock_data.csv")

# Calculate RSI
df['RSI'] = calculate_rsi(df, column='close', period=14)

# Calculate MACD and Signal
df['MACD'], df['Signal'] = calculate_macd(df, column='close')

# Save the updated DataFrame
df.to_csv("data/aapl_stock_data_with_indicators.csv", index=False)

print("RSI and MACD calculations added successfully!")
