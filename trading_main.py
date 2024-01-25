import yfinance as yf
import pandas as pd
import pandas_datareader as pdr
import plotly.graph_objects as go
import datetime as dt
from pandas_datareader import data as pdrd
from datetime import timedelta


# Ticker Symbol and Date Range
symbols = ["AAPL", "AMD", "AMZN", "GOOG", "INTC", "ORCL", "TXN"]

st = dt.datetime(2023, 1, 2)
en = dt.datetime.today()

#stockdata = pdr.DataReader('AAPL', 'stooq',st,en)
#stockdata = yf.download(["AAPL", "AMD", "AMZN", "GOOG", "INTC", "ORCL", "TXN"], start="2024-01-02", end="2024-01-24", group_by='ticker', interval="5m")
#print(stockdata.head())

# Loop through symbols
"""
for x in range(len(symbols)):
    stockdaten = pdr.DataReader(symbols[x], 'stooq', st, en)
    print(type(stockdaten))
    # Reset index to make 'Date' a column
    stockdaten.reset_index(inplace=True)

    # Create candlestick chart
    graph = go.Figure(data=[go.Candlestick(x=stockdaten['Date'],
                                           open=stockdaten['Open'],
                                           high=stockdaten['High'],
                                           low=stockdaten['Low'],
                                           close=stockdaten['Close'])])

    # Update layout
    graph.update_layout(
        title=f"{symbols[x]} Stock Price Movement",
        xaxis_rangeslider_visible=False,
        xaxis_title="Date Range",
        yaxis_title="Price"
    )

    # Show the chart
    graph.show()
#stockdata = pdr.DataReader('AMD', 'stooq',st,en)
#stockdata = yf.download(["AAPL", "AMD", "AMZN", "GOOG", "INTC", "ORCL", "TXN"], start="2024-01-02", end="2024-01-24", group_by='ticker', interval="5m")
"""
class Candle:
    def __init__(self, date, open, high, low, close):
        self.date=date
        self.open=open
        self.high=high
        self.low=low
        self.close=close


# Fibonacci Retracement Level Calculation
dailyHigh = 0
dailyLow = 0
yesterday = dt.datetime.today() - timedelta(1)
for x in range(len(symbols)):
    stockdata = yf.download(symbols[x], yesterday, dt.datetime.now(), interval="5m")
    #ticker = stockdata[symbols[x]]
    #ticker = ticker.split("\n",3)[3]
    #candles = ticker.split(' ')
    dailyHigh = stockdata.High.values[0]
    dailyLow = stockdata.Low.values[0]
    for y in range(len(stockdata.High.values)):
        if(stockdata.High.values[y] > dailyHigh):
            dailyHigh = stockdata.High.values[y]
        if(stockdata.Low.values[y] < dailyLow):
            dailyLow = stockdata.Low.values[y]
    diff = dailyHigh-dailyLow
    print(f"Data for {symbols[x]}")
    print(f"100% zone: {dailyHigh:10.2f}")
    print("78.6% zone: {:10.2f}".format(dailyHigh - (diff*0.286)))
    print("61.8% zone: {:10.2f}".format(dailyHigh - (diff*0.382)))
    print("Discount/Premium intraday line: {:10.2f}".format(dailyHigh - (diff/2)))
    print("38.2 zone: {:10.2f}".format(dailyHigh - (diff*0.618)))
    print("28.6% zone: {:10.2f}".format(dailyHigh - (diff*0.786)))
    print(f"LOD: {dailyLow:10.2f}")
