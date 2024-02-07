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
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Ticker Symbol and Date Range
symbols = ["AAPL", "AMD", "AMZN", "ARM", "GOOGL", "INTC", "MSFT", "OXY", "SPY", "TSM", "TXN", "TSLA"]
# Initializing the color spectrum for the Fibonacci charts
colors = ['red','orange','green','cyan']

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
# Add text to the PDF using reportlab
def add_text_to_pdf(pdf_path, text):
    c = canvas.Canvas(pdf_path, pagesize=letter)
    textobject = c.beginText(100, 750)  # Specify text position
    textobject.setFont("Helvetica", 14)  # Specify font and size
    textobject.textLines(text)  # Add text content
    c.drawText(textobject)
    c.showPage()
    
# Loop through symbols
for x in range(len(symbols)):
    yearly_pdf_output_path = f"{symbols[x]}_Yearly_Information.pdf"
    image_output_path = "temp_plot.png"
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
    
    # If the Retail traders are selling, but the banks/institutions are buying, then:
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
    # If the change in value is a strong bullish candle, and the gaps confirm...
    elif(yearly_delta_percent > 0.01 and yearly_gap_value > 0):
        # ...but it is near the highest prices of the year, then it is bearish
        if(stockdaten.Close.values[0] <= (yearlyHigh * 0.99)):
            if(stockdaten.Close.values[9] < stockdaten.Close.values[0]):
                trend = 0
            elif(((stockdaten.Close.values[3] - stockdaten.Open.values[2]) + (stockdaten.Close.values[2] - stockdaten.Open.values[1]) + (stockdaten.Close.values[1] - stockdaten.Open.values[0])) > stockdaten.Close.values[0]*0.015):
                trend = 0
            elif(((stockdaten.Close.values[3] - stockdaten.Open.values[2]) + (stockdaten.Close.values[2] - stockdaten.Open.values[1]) + (stockdaten.Close.values[1] - stockdaten.Open.values[0])) < stockdaten.Close.values[0]*0.015):
                trend = 1
            else:
                trend = 1
        # ...but it is in a buying zone, then it is bullish
        elif(stockdaten.Close.values[0] >= ((yearlyFibPrices[0] - yearlyLow) * 0.5)+yearlyLow and stockdaten.Close.values[0] < yearlyFibPrices[1]):
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
    for i, price in enumerate(yearlyFibPrices):
        graph.add_hline(y=price, line_color=colors[i])
    graph.add_hline(y=yearlyHigh, line_color='pink')
    graph.add_hline(y=(yearlyHigh - (diffYearly/2)), line_color="yellow")
    graph.add_hline(y=yearlyLow,line_color='black')   



    # Update layout
    graph.update_layout(
        title=f"{symbols[x]} Stock Price Movement",
        xaxis_rangeslider_visible=False,
        xaxis_title="Date Range",
        yaxis_title="Price",
        
    )
    pio.write_image(graph, image_output_path)
    # Add the Analyses
    pdf_text = f"The trend for {symbols[x]} is {analyzeTrend(trend)}\n Institutional buying: {yearly_gap_value:10.2f} or {yearly_gap_percent*100:10.2f}%\n Retail buying: {yearly_delta_value:10.2f} or {yearly_delta_percent*100:10.2f}%\n Buying zones:\n Long- \nOptimal: {yearlyLow:10.2f} to {yearlyFibPrices[0]:10.2f}\n Or: {yearlyFibPrices[0]:10.2f} to {yearlyFibPrices[1]:10.2f}\n Short:\n Optimal: {yearlyHigh:10.2f} to {yearlyFibPrices[3]:10.2f}\n Or: {yearlyFibPrices[3]:10.2f} to {yearlyFibPrices[2]:10.2f}"

    # Add the chart to the PDF
    c = canvas.Canvas(yearly_pdf_output_path, pagesize="letter")
    c.setTitle(f"{symbols[x]} Yearly Analyses")
    c.drawImage(image_output_path,x=-20,y=250)
    
    # Add the analyses to the PDF
    textobject = c.beginText(50, 225)  # Specify text position
    textobject.setFont("Helvetica", 14)  # Specify font and size
    textobject.textLines(pdf_text)  # Add text content
    c.drawText(textobject)
    c.showPage()
    
    # Save and close the PDF
    c.save()

    yesterday = dt.datetime.today() - timedelta(1)
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
    index = len(trendData.Open.values)-1
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
        if(index<len(trendData.Open.values)-1):
            gap_value+=trendData.Close.values[index + 1]- trendData.Open.values[index]
        index-=1
    
    # diffTrend is the absolute value of the Fibonacci range for the examination period
    # used for calculating the Fibonacci retracement levels
    diffTrend=trendHigh-trendLow
    # Expansion being false indicates Compression
    # Expansion being true indicates that the price will go past the current examination bands
    expansion = False
    delta_value_percent = delta_value/trendData.Open.values[3]
    gap_value_percent = gap_value/trendData.Open.values[3]
    
    
    pastThree_gaps = (trendData.Close.values[4] - trendData.Open.values[3]) + (trendData.Close.values[3] - trendData.Open.values[2]) + (trendData.Close.values[2] - trendData.Open.values[1]) 
    pastThree_candles = (trendData.Close.values[3] - trendData.Open.values[3]) + (trendData.Close.values[2] - trendData.Open.values[2]) + (trendData.Close.values[1] - trendData.Open.values[1])
    todays_move = trendData.Close.values[0] - trendData.Open.values[0]
    yesterdays_move = trendData.Close.values[1] - trendData.Open.values[1]
    # If the price has moved positively...
    if(delta_value_percent > 0.001):
        # ...and it has moved less than 2% over the examination period with buying in the gaps, then it is bullish
        if(delta_value_percent < 0.02 and gap_value_percent >= 0):
            trend = 0
            # Unless it is near the high of the year
            if(trendData.Close.values[0] > (yearlyHigh * 0.99)):
                trend = 1
        # ...and it has moved less than 2% over the examination period with selling in the gaps, then it is bullish + expansive
        elif(delta_value_percent < 0.02 and gap_value_percent < 0):
            trend = 0
            expansion = True
            # Unless it is near the high of the year
            if(trendData.Close.values[0] > (yearlyHigh * 0.99)):
                trend = 1
        # ...and the past three overnight sessions were middling, but today's candle is strong... 
        elif(-0.01 <= pastThree_gaps <= 0.01 and (((todays_move)/trendData.Open.values[0])*100 > 0.02)):
            #... then it is bullish
            trend = 0
        # ...and the past three overnight sessions were strong buys, AND today's candle is strong...
        elif(pastThree_gaps > 0.01 and (((todays_move)/trendData.Open.values[0])*100 > 0.02)):
            #... then it is bullish and likely to expand to the upside
            trend = 0 
            expansion = True
        # ...and the past three overnight sessions were strongly sold, and the retail of today is not enough to push through...
        elif(-0.02 >= pastThree_gaps and 0.02>(((todays_move)/trendData.Open.values[0])*100 > 0.005)):
            #... then it is bearish
            trend = 1
        #... and the past three overnight sessions were strongly sold, but today's retail is strongly bought...
        elif(-0.02 >= pastThree_gaps and (((todays_move)/trendData.Open.values[0])*100 >= 0.02)):
            #...then it is bullish
            trend = 0
        #... and the past three overnight sessions were weakly sold, but today's retail is mainly selling/doji...
        elif(-0.02 < pastThree_gaps < -0.01 and -0.01<(((todays_move)/trendData.Open.values[0])*100 < 0)):
            #... then it is sideways
            trend = 2 
        #... and the past three overnight sessions were selling along with today's retail...
        elif(-0.02 < pastThree_gaps < -0.01 and (pastThree_candles/delta_value)*100 < -0.01):
            #... then it is bearish
            trend = 1
                       
        # ...and it has moved significantly...
        elif(delta_value_percent > 0.05):
            # ...but it is the high of year...
            if(trendData.High.values[0] == yearlyHigh):
                #... then it is likely to continue sideways unless acted upon by an outside force
                trend = 2
            # ...but it is within a percent of the high of the year
            elif(trendData.High.values[0] > (yearlyHigh*0.99)):
                #... then it is likely to continue to the downside
                trend = 1
            # ...but it is in a "buying zone" either on a yearly or weekly basis
            elif((trendData.Close.values[0] >= trendLow and trendData.Close.values[0] <= trendFibPrices[1]) or (trendData.Close.values[0] >= yearlyLow and trendData.Close.values[0] <= yearlyFibPrices[1])):
                #... then it is bullish
                trend = 0
            # ...but it is in a "selling zone"...
            elif((trendData.Close.values[0] >= trendFibPrices[2] and trendData.Close.values <= trendHigh) or (trendData.Close.values[0] >= yearlyFibPrices[2] and trendData.Close.values[0] <= yearlyHigh)):
                #... without significant support
                if(gap_value_percent < -0.04):
                    #... then it is bearish
                    trend = 1
                elif(-0.04 > gap_value_percent < 0.01):
                    trend = 0
                #... with significant support
                if(gap_value_percent >= 0.01 and (trendData.Close.values[0]-trendData.Open.values[0]) > 0):
                    #... then it is bullish
                    trend = 0
                #... it otherwise results in a doji/don't want to trade that
                else:
                    trend = 2                  
        # If today closed below yesterday
        elif((trendData.Close.values[0] - trendData.Close.values[1]) < 0):
            # then it is generally bearish
            trend = 1   
            # Unless today is a gap down close down (extra cases)
            if(todays_move < 0):
                # Case 1: the price closed below over half of yesterday's move, 
                #         indicating market indecision or the appearance of a "dark cover" pattern in the candles 
                if(abs(todays_move)/abs(yesterdays_move) > 0.5):
                    trend = 1
                # Case 2: the price closed above half of yesterday's move,
                #         indicating that today is probably a pullback...
                elif(abs(todays_move)/(yesterdays_move) < 0.5):
                    # ...if the gap down between 49.99% to 33.33% below yesterday's close, it is bullish
                    if((trendData.Open.values[0] - trendData.Close.values[1])/(trendData.Close.values[1]-trendData.Open.values[1]) >= (1.0/3.0)):
                        trend = 0
                    # ... if the gap down is less than 33.333(...)2% and 0%...
                    elif(abs(trendData.Open.values[0] - trendData.Close.values[1])/(trendData.Close.values[1]-trendData.Open.values[1]) < (1.0/3.0)):
                        # and today's move is more than half of yesterday's move, then it's bullish
                        if(abs(trendData.Close.values[0]-trendData.Open.values[0])/(yesterdays_move) > 0.5):
                            trend = 1
                        # and today's move accounts for less than half of 
                        elif(0.001 < abs(trendData.Close.values[0] - trendData.Open.values[0])/yesterdays_move < 0.5):
                            trend = 0
                        # it is otherwise sideways
                        else:
                            trend = 2
                # it is otherwise sideways
                else:
                    trend = 2
            # But if today is a positive move
            elif (todays_move > 0):
                yesterdayDown = False
                if(yesterdays_move < 0):
                    yesterdayDown = True
                elif(yesterdayDown):
                    # and it is larger than yesterday, then it is bullish + expansive
                    if(todays_move > abs(yesterdays_move)):
                        trend = 0
                        expansion = True
                    # and today's move accounts for over 80% of the movement yesterday (positive or negative) it is bullish
                    elif(todays_move/abs(yesterdays_move) >= 0.8):
                        trend = 0
                    # if it is between the ranges of yesterday and today, then it is bearish. Likely a dead-cat bounce
                    elif(0.4 < todays_move/abs(yesterdays_move) < 0.8):
                        trend = 1
        # it is otherwise sideways
        else:
            trend = 2 
    # If the price has moved negatively...
    elif(delta_value_percent < 0):
        # Case 1: no more than five percent of the stock's value
        if(-0.05 < delta_value_percent):
            # If it is less than one percent of the stock's value, it is sideways 
            if(delta_value_percent > -0.01):
                trend = 2
            # if it is more than one percent and less than 5, it's bearish 
            elif(-0.01 > delta_value_percent > 0.05):
                trend = 1
            # unless today's move is up (potentially)
            elif((todays_move)>0):
                # and it is up over half of the total negative value to date
                if((trendData.Close.values[0]-trendData.Open.values[0])/abs(delta_value) > 0.5):
                    # it's bullish
                    trend = 0
                # and if it is less than that...
                elif((trendData.Close.values[0] - trendData.Open.values[0])/abs(delta_value) < 0.5):
                    # Such as between 30-50%
                    if(0.3 < (trendData.Close.values[0] - trendData.Open.values[0])/abs(delta_value) < 0.5):
                        # and yesterday is up as well, means it is a reversal
                        if(yesterdays_move > 0):
                            trend = 0
                        # otherwise it is bearish
                        else:
                            trend = 1
                    # it is otherwise bearish
                    else:
                        trend = 1
            # It is otherwise sideways
            else:
                trend = 2
        # if the stock has fallen more than 5%
        if(delta_value_percent < -0.05):
            # and has gapped up and closed down
            if(gap_value_percent > 0.02):
                # it's bearish and in a hard way
                trend = 1
                expansion = True
            #if the past three candles are a "three black crows" pattern
            elif(abs(pastThree_candles/delta_value) >= 0.8):
                # it's bearish and in a hard way
                trend = 1 
                expansion = True
                # unless...
                # today closed up...
                if((trendData.Close.values[0] - trendData.Open.values[0]) > 0):
                    # and encompasses over fifty percent of the previous candle
                    if((trendData.Close.values[0] - trendData.Open.values[0])/abs(yesterdays_move) > 0.5):
                        # it's bullish
                        trend = 0
                    # and it is less than halfway up the previous candle
                    elif((trendData.Close.values[0] - trendData.Open.values[0])/abs(yesterdays_move) < 0.5):
                        # if the close is between 33.33-49.99%, then it is bullish
                        if((todays_move)/abs(trendData.Close.values[1]-trendData.Open.values[1]) >= (1.0/3.0)):
                            trend = 0
                        # if the gap is down and it closes below a third of the previous candle, the overall power of the sellers will win out
                        elif((trendData.Open.values[0] - trendData.Close.values[1]) < 0 and (todays_move)/abs(trendData.Close.values[1]-trendData.Open.values[1]) < (1.0/3.0)):
                            trend = 1
                        # it is otherwise sideways
                        else:
                            trend = 2
            # if the past three candles are close to overshadowed by today's candle
            elif(0.5 < abs(pastThree_candles/delta_value) < 0.8):
                # and it closes down, then it is bearish
                if((trendData.Close.values[0]-trendData.Open.values[0]) < 0):
                    trend = 1
                # and it closes up, then...
                elif(trendData.Close.values[0]-trendData.Open.values[0] > 0):
                    # if it breaks above the average of yesterday, it is bullish
                    if((trendData.Close.values[0] - trendData.Open.values[0])/abs(yesterdays_move) >= 0.5):
                        trend = 0
                    # if it stays below the average...
                    elif((trendData.Close.values[0] - trendData.Open.values[0])/abs(yesterdays_move) < 0.5):
                        # ... between 33.33% and 49.99%, it is bullish
                        if(abs(todays_move)/abs(yesterdays_move) >= (1.0/3.0)):
                            trend = 0
                        
                        elif(0.01 < abs(todays_move)/abs(yesterdays_move) < (1.0/3.0)):
                                trend = 1
                        else:
                            trend = 2
                else:
                    trend = 1
    # If the price has not moved (or is otherwise not a trade this program/strategy recommends), it is simply sideways/doji candle
    else:
        trend = 2    



    # Daily Reports and Analysis for the symbols

    
    

    # Daily Highs and Lows are calculated in realtime based on the newest 5min charts
    dailyHigh = 0
    dailyLow = 0

    # For each percentage point in fibLevels, a relative Fibonacci level is created for the trend values of the stock
    snex=0
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

    for i, price in enumerate(trendFibPrices):
        chart.add_hline(y=price, line_color=colors[i])
    chart.add_hline(y=trendHigh, line_color='pink')
    chart.add_hline(y=(trendHigh - (diffTrend/2)), line_color="yellow")
    chart.add_hline(y=trendLow,line_color='black')

    # Update Layout and print
    chart.update_layout(
        title=f"{symbols[x]} Daily 5 Minute Data with 7-day Price Action",
        xaxis_title="Time",
        yaxis_title="$",
        xaxis_rangeslider_visible=False
    )
    
    # Add to PDF
    dailyReport_path=f"{symbols[x]}_Daily_Information.pdf"
    c = canvas.Canvas(dailyReport_path, pagesize="letter")
    c.setTitle(f"{symbols[x]} Daily Report")
    chart.write_image(image_output_path)
    c.drawImage(image_output_path,x=-20,y=250)

    # Add the Analyses
    if(trend == 0):
        pdf_text = f"The trend for {symbols[x]} over the examination period is {analyzeTrend(trend)}. Consider waiting for the lowest entry in the zones before buying, or if you wish to buy at all.\n Institutional buying: {gap_value:10.2f} or {gap_value_percent*100:10.2f}%\n Retail buying: {delta_value:10.2f} or {delta_value_percent*100:10.2f}%\n Buying zones:\n Long- \nOptimal: {trendLow:10.2f} to {trendFibPrices[0]:10.2f}\n Or: {trendFibPrices[0]:10.2f} to {trendFibPrices[1]:10.2f}\n"
    elif(trend == 1):
        pdf_text = f"The trend for {symbols[x]} over the examination period is {analyzeTrend(trend)}. Consider waiting for the price to bounce to a higher level intraday before getting short, if you wish to get short or sell at all.\n Institutional buying: {gap_value:10.2f} or {gap_value_percent*100:10.2f}%\n Retail buying: {delta_value:10.2f} or {delta_value_percent*100:10.2f}%\n Buying zones:\nShort:\n Optimal: {trendHigh:10.2f} to {trendFibPrices[3]:10.2f}\n Or: {trendFibPrices[3]:10.2f} to {yearlyFibPrices[2]:10.2f}"
    else:
        pdf_text = f"The trend for {symbols[x]} over the examination period is {analyzeTrend(trend)}, consider vertical or call-credit/put-credit spreads, if you wish to get involved at all.\n Institutional buying: {gap_value:10.2f} or {gap_value_percent*100:10.2f}%\n Retail buying: {delta_value:10.2f} or {delta_value_percent*100:10.2f}%\n Buying zones:\n Long- \nOptimal: {trendLow:10.2f} to {trendFibPrices[0]:10.2f}\n Or: {trendFibPrices[0]:10.2f} to {trendFibPrices[1]:10.2f}\n Short:\n Optimal: {trendHigh:10.2f} to {trendFibPrices[3]:10.2f}\n Or: {trendFibPrices[3]:10.2f} to {yearlyFibPrices[2]:10.2f}"
    textobject = c.beginText(50, 225)  # Specify text position
    textobject.setFont("Helvetica", 14)  # Specify font and size
    textobject.textLines(pdf_text)  # Add text content
    c.drawText(textobject)

    # Save and close PDF
    c.save()





    


