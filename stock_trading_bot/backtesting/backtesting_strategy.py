from zipline.api import order, record, symbol, set_commission, set_slippage
from zipline.finance.commission import PerShare
from zipline.finance.slippage import FixedSlippage


def initialize(context):
    # Define the stock to trade
    context.asset = symbol("AAPL")

    # Parameters for strategy
    context.short_window = 10  # Short moving average window
    context.long_window = 50  # Long moving average window
    context.rsi_window = 14  # RSI window

    # Risk management
    context.stop_loss_pct = 0.05  # 5% stop-loss
    context.take_profit_pct = 0.10  # 10% take-profit
    context.entry_price = None

    # Set commission and slippage
    set_commission(PerShare(cost=0.001, min_trade_cost=1.0))  # $0.001 per share
    set_slippage(FixedSlippage(spread=0.02))  # $0.02 slippage per share


def handle_data(context, data):
    # Calculate moving averages
    short_mavg = data.history(context.asset, 'price', context.short_window, '1d').mean()
    long_mavg = data.history(context.asset, 'price', context.long_window, '1d').mean()

    # Calculate RSI
    prices = data.history(context.asset, 'price', context.rsi_window + 1, '1d')
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).mean()
    loss = (-delta.where(delta < 0, 0)).mean()
    rs = gain / loss if loss != 0 else 0
    rsi = 100 - (100 / (1 + rs))

    # Get current price
    current_price = data.current(context.asset, 'price')

    # Trading logic
    if short_mavg > long_mavg and rsi < 30:
        # Buy signal: Uptrend + oversold condition
        order(context.asset, 10)
        context.entry_price = current_price
    elif short_mavg < long_mavg or (rsi > 70 and current_price > context.entry_price * (1 + context.take_profit_pct)):
        # Sell signal: Downtrend or overbought with take-profit
        order(context.asset, -10)
        context.entry_price = None

    # Stop-loss logic
    if context.entry_price and current_price < context.entry_price * (1 - context.stop_loss_pct):
        order(context.asset, -10)  # Exit trade
        context.entry_price = None

    # Record metrics for analysis
    record(price=current_price, short_mavg=short_mavg, long_mavg=long_mavg, rsi=rsi)


def analyze(context, perf):
    import matplotlib.pyplot as plt

    # Plot portfolio value
    perf["portfolio_value"].plot(figsize=(12, 6), title="Portfolio Value Over Time")
    plt.ylabel("Portfolio Value ($)")
    plt.show()
