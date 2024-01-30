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
symbols = ["AAPL", "AMD", "AMZN", "ARM", "BITB", "GOOGL", "INTC", "MARA", "MSFT", "ORCL", "OXY", "SPY", "TSM", "TXN", "TSLA"]

st = dt.datetime(2023, 1, 2)
en = dt.datetime.today()

class Candle:
    def __init__(self, date, open, high, low, close):
        self.date=date
        self.open=open
        self.high=high
        self.low=low
        self.close=close
class Order:
    def __init__(self, date, time, position, symbol):
        self.date=date
        self.time = time
        self.position=position
        self.symbol=symbol
    def order_report(date,time,price,symbol):
        orderData={'Date': date, 'Time':time, 'Price':price, 'Symbol':symbol}
        orderReport = pd.DataFrame(data=orderData, index=[0])
        print(orderReport.head())


# trend is expressed 0-2 for 0 = bullish, 1 = bearish, and 2 = sideways
trend = 0
def analyzeTrend(val):
    if(val == 0):
        return "Bullish"
    elif(val == 1):
        return "Bearish"
    else:
        return "Neutral/Sideways"


# Loop through symbols

# Save for Yearly Statements

for x in range(len(symbols)):
    yearlyHigh = 0
    stockdaten = pdr.DataReader(symbols[x], 'stooq', st, en)
    yearlyLow=stockdaten.High.values[x]
    # Analyze Trend
    yearlyTrend = 0
    # Starting with the oldest data in the dataset
    yearlyIndex = len(stockdaten.Open.values)-1
    # delta_value is the change in value from open -> close across the examination period
    yearly_delta_value=0
    # gap_value is the change in value from close -> open across the examination period
    yearly_gap_value=0

    ## Gap Value shows institutional sentiment, 
    ## Delta Value shows retail sentiment
    for y in range(len(stockdaten)):
        if(stockdaten.High.values[y] > yearlyHigh):
            yearlyHigh = float(stockdaten.High.values[y])
        elif(stockdaten.Low.values[y] < yearlyLow):
            yearlyLow = float(stockdaten.Low.values[y])
        if(y<len(stockdaten.Open.values)-1):
            yearly_gap_value+=stockdaten.Close.values[y+1] - stockdaten.Open.values[y]
            yearly_delta_value+=stockdaten.Close.values[y]-stockdaten.Open.values[y]
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
    
    # Expansion being false indicates Compression
    # Expansion being true indicates that the price will go past the current examination bands
    expansion = False
    yearly_delta_percent = yearly_delta_value/(stockdaten.Open.values[len(stockdaten.Open.values)-1])
    yearly_gap_percent = yearly_gap_value/(stockdaten.Open.values[len(stockdaten.Open.values)-1])
    
    if(yearly_delta_value<-0.5 and yearly_gap_percent>0.2):
        # If the trend is downwards, with several gap up movements, 
        # but the price of the yearly difference in value between the open of the year and now is in a buying zone
        # then it is bullish
        if((yearly_delta_value + stockdaten.Open.values[len(stockdaten.Open.values)-1]) > yearlyFibPrices[0]):
            trend = 0
            expansion=True
        # If there are several gap up movements that result in selling, it is then bearish
        # Such as institutions covering their shorts with a higher entry price by buying pre- or post-market
        elif((yearly_delta_value + stockdaten.Open.values[len(stockdaten.Open.values)-1]) < yearlyFibPrices[0]):
            trend = 1
    # If there are several gap down movements that result in buying,then it is bullish, and is likely to expand to the upside
    if(yearly_delta_percent>1 and yearly_gap_percent<-0.2):
        trend = 0
        expansion=True
    # If the change in value is a strong bearish candle, and the gaps confirm, then it is bearish
    if(yearly_delta_percent < -0.05 and yearly_gap_percent < 0):
        trend = 1
    # If the change in value is a strong bullish candle, and the gaps confirm, then it is bullish
    elif(yearly_delta_percent > 0.01 and yearly_gap_value > 0):
        trend = 0
    # If the change in value is neutral/doji candle, and the gaps are neutral or lower, then it is sideways
    elif(-0.2<yearly_delta_value<0.2 and yearly_gap_percent < 0.01):
        trend = 2
    # If the change in value is bearish, but institutional sentiment is up, then it is bullish, and is likely to expand to the upside
    elif(yearly_delta_percent < -0.1 and yearly_gap_value > 0):
        trend = 0
        expansion=True
    # If the change in value is bullish, but institutional sentiment is down, then it is bearish, and is likely to expand to the downside
    elif(yearly_delta_percent > 0.10 and yearly_gap_value < 0):
        trend = 1
        expansion=True
    # If all else fails, it is sideways therefore
    else:
        trend = 2
    
    # Add them to the graph
    graph.add_hline(y=yearlyLow)
    graph.add_hline(y=yearlyFibPrices[0])
    graph.add_hline(y=yearlyFibPrices[1])
    graph.add_hline(y=(yearlyHigh - (diffYearly/2)))
    graph.add_hline(y=yearlyFibPrices[2])
    graph.add_hline(y=yearlyFibPrices[3])
    graph.add_hline(y=yearlyHigh)    



    # Update layout
    graph.update_layout(
        title=f"{symbols[x]} Stock Price Movement",
        xaxis_rangeslider_visible=False,
        xaxis_title="Date Range",
        yaxis_title="Price",
        annotations=[
            go.layout.Annotation(
                text=f"Over the examination period:<br>The trend for {symbols[x]} is {analyzeTrend(trend)}<br>Institutional buying: {yearly_gap_value:10.2f} or {yearly_gap_percent*100:10.2f}%<br>Retail buying: {yearly_delta_value:10.2f} or {yearly_delta_percent*100:10.2f}%<br>Buying zones: <br>Long- {yearlyFibPrices[0]:10.2f} to {yearlyFibPrices[1]:10.2f} and<br>Short- {yearlyFibPrices[3]:10.2f}   to    {yearlyFibPrices[2]:10.2f}",
                align='left',
                showarrow=False,
                xref='paper',
                x=0.47,
                y=yearlyHigh+(yearlyHigh*0.01)+0.5,
                font=(dict(size=12)),
                bordercolor='yellow',
                borderwidth=2
            )
        ],
    )
    # Show the chart
    plo.plot(graph)
    

yesterday = dt.datetime.today() - timedelta(1)


# Daily Highs and Lows are calculated in realtime based on the newest 5min charts
dailyHigh = 0
dailyLow = 0

# Daily Reports and Analysis for the symbols
for x in range(len(symbols)):
    stockdata = yf.download(symbols[x], yesterday, dt.datetime.now(), interval="5m")
    dailyHigh = stockdata.High.values[0]
    dailyLow = stockdata.Low.values[0]
    for y in range(len(stockdata.High.values)):
        if(stockdata.High.values[y] > dailyHigh):
            dailyHigh = stockdata.High.values[y]
        if(stockdata.Low.values[y] < dailyLow):
            dailyLow = stockdata.Low.values[y]
    diff = dailyHigh-dailyLow

    # Calulate Fibonacci Levels
    fibLevels = [0.236, 0.382, 0.618, 0.764]
    trendFibPrices=[0,0,0,0]

    # Trend Analysis
    start_trend = dt.datetime.today() - timedelta(7)
    trendData = pdr.DataReader(symbols[x],'stooq',start_trend,dt.datetime.today())

    # Starting with the oldest data in the dataset
    index = 3
    # delta_value is the change in value from open -> close across the examination period
    delta_value=0
    # gap_value is the change in value from close -> open across the examination period
    gap_value=0

    ## Gap Value shows institutional sentiment, 
    ## Delta Value shows retail sentiment

    # initialize the Fibonacci 100% and 0% levels
    trendHigh=0
    trendLow=trendData.Low.values[0]
    
    # Sort through the data (oldest to newest) to find the high of the trend, 
    # the low of the trend, and the Institutional Sentiment (gap_value) and Retail Sentiment (delta_value)
    while index >= 0:
        if(trendData.Low.values[index] < trendLow):
            trendLow = float(trendData.Low.values[index])
        elif(trendData.High.values[index] > trendHigh):
            trendHigh = trendData.High.values[index]
        delta_value+=trendData.Close.values[index] - trendData.Open.values[index]
        if(index<3):
            gap_value+=trendData.Close.values[index + 1]- trendData.Open.values[index]
            delta_value+=trendData.Close.values[index] - trendData.Open.values[index]
        index-=1
    
    # diffTrend is the absolute value of the Fibonacci range for the examination period
    # used for calculating the Fibonacci retracement levels
    diffTrend=trendHigh-trendLow
    # Expansion being false indicates Compression
    # Expansion being true indicates that the price will go past the current examination bands
    expansion = False
    
    # If there are several gap up days that result in selling, it is then bearish, and is likely to expand to the downside
    if(delta_value<-0.2 and gap_value>0.2):
        trend = 1
        expansion=True
    # If there are several gap down days that result in buying,then it is bullish, and is likely to expand to the upside
    if(delta_value>0.2 and gap_value<-0.2):
        trend = 0
        expansion=True
    # If the change in value is a strong bearish candle, and the gaps confirm, then it is bearish
    if(delta_value < -0.2 and gap_value < 0):
        trend = 1
    # If the change in value is a strong bullish candle, and the gaps confirm, then it is bullish
    elif(delta_value > 0.2 and gap_value > 0):
        trend = 0
    # If the change in value is neutral/doji candle, and the gaps are neutral or lower, then it is sideways
    elif(-0.2<delta_value<0.2 and (gap_value/trendData.Close.values[0]) < 0.01):
        trend = 2
    # If the change in value is bearish, but institutional sentiment is up, then it is bullish, and is likely to expand to the upside
    elif(delta_value < -0.2 and gap_value > 0):
        trend = 0
        expansion=True
    # If the change in value is bullish, but institutional sentiment is down, then it is bearish, and is likely to expand to the upside
    elif(delta_value > 0.2 and gap_value < 0):
        trend = 1
        expansion=True
    # If all else fails, it is sideways therefore
    else:
        trend = 2
    
    # snex is a temp variable
    snex=0
    # For each percentage point in fibLevels, a relative Fibonacci level is created for the trend values of the stock
    while(snex < 4):
        trendFibPrices[snex] = trendLow + (diffTrend * fibLevels[snex])
        snex+=1
    
    today=dt.datetime.today()
    today_open=today.replace(hour=9,minute=30)
    today_close=today.replace(hour=16,minute=00)
    chartdata = yf.download(symbols[x],today_open,today_close,interval="5m")
    chartdata.reset_index(inplace=True)
    # Feeding the chart clean 5 minute times
    fiveMinTimes=["9:30","9:35","9:40", "9:45", "9:50", "9:55", "10:00", "10:05","10:10","10:15", "10:20", "10:25", "10:30", "10:35",
                  "10:40","10:45","10:50", "10:55", "11:00", "11:05", "11:10","11:15","11:20","11:25", "11:30", "11:35", "11:45", "11:50",
                  "11:55","12:00","12:05", "12:10", "12:15", "12:20", "12:25","12:30","12:35", "12:40","12:45","12:50", "12:55", "1:00", 
                  "1:05", "1:10", "1:15","1:20","1:25", "1:30", "1:35", "1:40", "1:45", "1:50","1:55","2:00", "2:05", "2:10", "2:15", "2:20",
                  "2:25","2:30","2:35", "2:40", "2:45", "2:50", "2:55", "3:00", "3:05", "3:10","3:15","3:20", "3:25", "3:30", "3:35", "3:40",
                  "3:45","3:50","3:55", "4:00"]
    # Make the chart with the clean time intervals and all of the values of the candlesticks
    chart = go.Figure(data=[go.Candlestick(x=fiveMinTimes,
                                            open=chartdata.Open.values,
                                           high=chartdata.High.values,
                                           low=chartdata.Low.values,
                                           close=chartdata.Close.values)])

    # If the trend is bullish or bearish, the graphing is different to better express Fibonacci levels
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

    # Update Layout and print
    chart.update_layout(
        title=f"{symbols[x]} Daily 5 Minute Data with 4-day Price Action",
        xaxis_title="Time",
        yaxis_title="$",
        annotations=[
            go.layout.Annotation(
                text=f"Over the examination period:<br>The trend for {symbols[x]} is {analyzeTrend(trend)}<br>Institutional buying: {gap_value:10.2f} or {(gap_value/trendData.Close.values[0])*100:10.2f}%<br>Retail buying: {delta_value:10.2f} or {(delta_value/trendData.Close.values[0])*100:10.2f}%<br>Buying zones: <br>Long- {trendFibPrices[0]:10.2f} to {trendFibPrices[1]:10.2f} and<br>Short- {trendFibPrices[3]:10.2f}   to    {trendFibPrices[2]:10.2f}",
                align='left',
                showarrow=False,
                xref='paper',
                x=0.47,
                y=trendHigh+(trendHigh*0.01)+0.5,
                font=(dict(size=12)),
                bordercolor='yellow',
                borderwidth=2
            )
        ],
    )
    plo.plot(chart)

