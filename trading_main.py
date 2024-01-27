#import dash
import yfinance as yf
import pandas as pd
import pandas_datareader as pdr
import plotly.graph_objects as go
import datetime as dt
from pandas_datareader import data as pdrd
from datetime import timedelta
import plotly.offline as plo
import plotly.io as pio
pio.renderers.default = 'browser'
import kaleido
#from dash import 

# Ticker Symbol and Date Range
symbols = ["AAPL", "AMD", "AMZN", "GOOGL", "INTC", "ORCL", "TXN"]

st = dt.datetime(2023, 1, 2)
en = dt.datetime.today()

#stockdata = pdr.DataReader('AAPL', 'stooq',st,en)
#stockdata = yf.download(["AAPL", "AMD", "AMZN", "GOOG", "INTC", "ORCL", "TXN"], start="2024-01-02", end="2024-01-24", group_by='ticker', interval="5m")
#print(stockdata.head())

# Loop through symbols
"""
# Save for Yearly Statements
for x in range(len(symbols)):
    yearlyHigh = 0
    stockdaten = pdr.DataReader(symbols[x], 'stooq', st, en)
    yearlyLow=stockdaten.High.values[x]
    for y in range(len(stockdaten)):
        if(stockdaten.High.values[y] > yearlyHigh):
            yearlyHigh = float(stockdaten.High.values[y])
        elif(stockdaten.Low.values[y] < yearlyLow):
            yearlyLow = float(stockdaten.Low.values[y])
    diffYearly = yearlyHigh-yearlyLow
    # Reset index to make 'Date' a column
    stockdaten.reset_index(inplace=True)

    # Create candlestick chart
    graph = go.Figure(data=[go.Candlestick(x=stockdaten['Date'],
                                           open=stockdaten['Open'],
                                           high=stockdaten['High'],
                                           low=stockdaten['Low'],
                                           close=stockdaten['Close'])])

    # Calulate Yearly Fibonacci Levels
    fibLevels = [0.236, 0.382, 0.618, 0.764]
    yearlyFibPrices=[0,0,0,0]
    snex=0
    while(snex < 4):
        yearlyFibPrices[snex] = yearlyLow + (diffYearly * fibLevels[snex])
        snex+=1
    # Add them to the graph
    graph.add_shape(type="line", y0=yearlyLow, fillcolor="green", y1=yearlyLow, x0=st,x1=en)
    graph.add_shape(type="line",y0=yearlyFibPrices[0], fillcolor="#34eb77", y1=yearlyFibPrices[0], x0=st,x1=en)
    graph.add_shape(type="line",y0=yearlyFibPrices[1], fillcolor="#07f2ff", y1=yearlyFibPrices[1], x0=st,x1=en)
    graph.add_shape(type="line",y0=yearlyHigh-(diffYearly/2), fillcolor="#e834eb", y1=(yearlyHigh-(diffYearly/2)), x0=st,x1=en)
    graph.add_shape(type="line",y0=yearlyFibPrices[2], fillcolor="#eb9834", y1=yearlyFibPrices[2], x0=st,x1=en)
    graph.add_shape(type="line",y0=yearlyFibPrices[3], fillcolor="#eb5b34", y1=yearlyFibPrices[3], x0=st,x1=en)
    graph.add_shape(type="line",y0=yearlyHigh, fillcolor="#b80018", y1=yearlyHigh, x0=st,x1=en)
    

    # Update layout
    graph.update_layout(
        title=f"{symbols[x]} Stock Price Movement",
        xaxis_rangeslider_visible=False,
        xaxis_title="Date Range",
        yaxis_title="Price",
    )
    # Show the chart
    plo.plot(graph)
    """
#stockdata = pdr.DataReader('AMD', 'stooq',st,en)
#stockdata = yf.download(["AAPL", "AMD", "AMZN", "GOOG", "INTC", "ORCL", "TXN"], start="2024-01-02", end="2024-01-24", group_by='ticker', interval="5m")

class Candle:
    def __init__(self, date, open, high, low, close):
        self.date=date
        self.open=open
        self.high=high
        self.low=low
        self.close=close


# Fibonacci Retracement Level Calculation

# trend is expressed 0-2 for 0 = bullish, 1 = bearish, and 2 = sideways
trend = 0
def analyzeTrend(val):
    if(val == 0):
        return "Bullish"
    elif(val == 1):
        return "Bearish"
    else:
        return "Neutral/Sideways"
# Daily Highs and Lows are calculated in realtime based on the newest 5min charts
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
    """
    print(f"Data for {symbols[x]}")
    print(f"100% zone: {dailyHigh:10.2f}")
    print("78.6% zone: {:10.2f}".format(dailyHigh - (diff*0.236)))
    print("61.8% zone: {:10.2f}".format(dailyHigh - (diff*0.382)))
    print("Discount/Premium intraday line: {:10.2f}".format(dailyHigh - (diff/2)))
    print("38.2 zone: {:10.2f}".format(dailyHigh - (diff*0.618)))
    print("23.6% zone: {:10.2f}".format(dailyHigh - (diff*0.786)))
    print(f"LOD: {dailyLow:10.2f}")
    """
    # Calulate Fibonacci Levels
    fibLevels = [0.236, 0.382, 0.618, 0.764]
    trendFibPrices=[0,0,0,0]

    # Trend Analysis
    start_trend = dt.datetime.today() - timedelta(3)
    trendData = pdr.DataReader(symbols[x],'stooq',start_trend,dt.datetime.today())

    index = 3
    delta_value=0
    gap_value=0
    trendHigh=0
    trendLow=trendData.Low.values[0]
    while index >= 0:
        if(trendData.Low.values[index] < trendLow):
            trendLow = float(trendData.Low.values[index])
        elif(trendData.High.values[index] > trendHigh):
            trendHigh = trendData.High.values[index]
        delta_value+=trendData.Close.values[index] - trendData.Open.values[index]
        if(index<3):
            gap_value+=trendData.Open.values[index] - trendData.Open.values[index + 1]
        index-=1
    #print(f"Change in value for {symbols[x]} stock the last few days: {delta_value:10.2f}$ or {((delta_value/trendData.Open.values[3])*100):10.4f}%")
    #print(f"Gap up/down values over the examination period: {gap_value:10.2f} or {((gap_value/trendData.Close.values[0])*100):10.4f}%")
    
    diffTrend=trendHigh-trendLow
    snex=0
    expansion = False
    
    # If the change in value is a strong bearish candle, and the gaps confirm, then it is bearish
    if(delta_value < -0.2 and gap_value < 0):
        trend = 1
    # If the change in value is a strong bullish candle, and the gaps confirm, then it is bullish
    elif(delta_value > 0.2 and gap_value > 0):
        trend=0
    # If the change in value is neutral/doji candle, and the gaps are neutral or lower, then it is sideways
    elif(-0.2<delta_value<0.2 and (gap_value/trendData.Close.values[0]) < 0.01):
        trend=2
    # If the change in value is bearish, but institutional sentiment is up, then it is bullish
    elif(delta_value < -0.2 and gap_value > 0):
        trend=0
    # If the change in value is bullish, but institutional sentiment is down, then it is bearish
    elif(delta_value > 0.2 and gap_value < 0):
        trend=1
    # If all else fails, it is sideways therefore
    else:
        trend=2
    
    snex=0
    while(snex < 4):
        trendFibPrices[snex] = trendLow + (diffTrend * fibLevels[snex])
        snex+=1

    #chartdata = pdr.DataReader(symbols[x],'yahoo',)
    chartdata = yf.download(symbols[x],yesterday,dt.datetime.today(),interval="5m")
    chartdata.reset_index(inplace=True)
    fiveMinTimes=["9:30","9:35","9:40", "9:45", "9:50", "9:55", "10:00", "10:05","10:10","10:15", "10:20", "10:25", "10:30", "10:35",
                  "10:40","10:45","10:50", "10:55", "11:00", "11:05", "11:10","11:15","11:20","11:25", "11:30", "11:35", "11:45", "11:50",
                  "11:55","12:00","12:05", "12:10", "12:15", "12:20", "12:25","12:30","12:35", "12:40","12:45","12:50", "12:55", "1:00", 
                  "1:05", "1:10", "1:15","1:20","1:25", "1:30", "1:35", "1:40", "1:45", "1:50","1:55","2:00", "2:05", "2:10", "2:15", "2:20",
                  "2:25","2:30","2:35", "2:40", "2:45", "2:50", "2:55", "3:00", "3:05", "3:10","3:15","3:20", "3:25", "3:30", "3:35", "3:40",
                  "3:45","3:50","3:55", "4:00"]
    chart = go.Figure(data=[go.Candlestick(x=fiveMinTimes,
                                            open=chartdata.Open.values,
                                           high=chartdata.High.values,
                                           low=chartdata.Low.values,
                                           close=chartdata.Close.values)])

    if(trend == 0):
        chart.add_hline(y=trendLow)
        chart.add_hline(y=trendFibPrices[0])
        chart.add_hline(y=trendFibPrices[1])
        chart.add_hline(y=(trendHigh - (diffTrend/2)))
        chart.add_hline(y=trendFibPrices[2])
        chart.add_hline(y=trendFibPrices[3])
        chart.add_hline(y=trendHigh)
    elif(trend == 1):
        chart.add_hline(y=(trendData.Open[1] + trendData.Close.values[2])/2)
        chart.add_hline(y=trendFibPrices[0])
        chart.add_hline(y=trendFibPrices[1])
        chart.add_hline(y=(trendHigh - (diffTrend/2)))
        chart.add_hline(y=trendFibPrices[2])
        chart.add_hline(y=trendFibPrices[3])
        chart.add_hline(y=trendHigh)
        chart.add_hline(y=trendLow - (diffTrend*.2))
    chart.update_layout(
        title=f"{symbols[x]} Four Day Price Action",
        xaxis_title="Time",
        yaxis_title="Stock Value",
    )
    plo.plot(chart)

