#!/usr/bin/env python
# coding: utf-8

# In[2]:


import yfinance as yf
import numpy as np 
import pandas as pd
import datetime
from IPython.display import HTML
from bs4 import BeautifulSoup
import requests


# In[3]:


# Getting NSE Holidays for year 2023 from Zerodha Website
response = requests.get("https://zerodha.com/z-connect/traders-zone/holidays/market-holiday-calendar-2023-nse-bse-and-mcx")
soup = BeautifulSoup(response.content, 'html.parser')
x = soup.find_all("table")[0]
holidays = []
number = 0
for row in x.find_all('tr'):
    for cell in row.find_all('td'):
        number += 1
        if (number > 4) and number%3 == 2:
            dt = pd.Timestamp(str(cell.contents[0]))
            date = pd.to_datetime(dt).date()
            holidays.append((str(date)))


# In[4]:


df = pd.read_csv("https://www1.nseindia.com/content/indices/ind_nifty50list.csv") # Read Nifty50 Stocks

#Adding Trading View Chart Links For Each Stock
df['Chart'] = df['Symbol'].apply(lambda x: f'<a href="https://in.tradingview.com/chart/quBr0210/?symbol=NSE%3A{x}" target="_blank">{x}</a>')

 # Add .NS with Symbol name to get data from Yahoo Finance
Symbol = []
for symbol in df['Symbol']:
    name = "".join([symbol, ".NS"])
    Symbol.append(name)
df['Symbol'] = Symbol

# Lists to add more info
price = []
volume = []
volume_avg = []
price_avg = []
volume_max = []
date_vol_max = []
close_vol = []
candle_vol = []
high_close = []

# Function to get info from yfinance
def get_Data(mydata, days):
    for index, symbol in mydata.iterrows():
        name = yf.Ticker(symbol['Symbol'])
        data = name.history(days).reset_index()
        data['Date'] = pd.to_datetime(data['Date']).dt.date
        today = pd.to_datetime("today").strftime("%Y-%m-%d")
        weekday = pd.Timestamp(today).day_name()
        total_volume = data['Volume'].sum()
        total_price = data['Close'].sum()
        weekend = ['Saturday', 'Sunday']
        holidays = ['2023-01-26', '2023-03-07', '2023-03-30', '2023-04-04', '2023-04-07', '2023-04-14', '2023-05-01', '2023-06-28',
 '2023-08-15', '2023-09-19', '2023-10-02', '2023-10-24', '2023-11-14', '2023-11-27', '2023-12-25']
        count = data['Volume'].count()
        
        # Market is closed on Weekends and Holidays.
        if weekday not in weekend and today not in holidays:
            for index, row in data.iterrows():
                if str(row['Date']) == str(today):
                    close = round(row['Close'],2)
                    traded = row['Volume']
                    average_volume = round((total_volume - traded) / (count - 1))
                    average_price = round((total_price - close) / (count - 1), 2)
                    price.append(close)
                    volume.append(traded)
                    volume_avg.append(average_volume)
                    price_avg.append(average_price)                    
            maximum_volume = int(data['volume'].max())
            date_vmax = str(data.loc[lambda x: x['Volume'] == maximum_volume].reset_index()['Date'])[4:15]
            close_vmax = round(float(data[data['Volume'] == maximum_volume]['close']), 2)
            candle_point = round(float(data[data['Volume'] == maximum_volume]['Close']) - float(data[data['Volume'] == maximum_volume]['Low']), 2)
            hc = round(float(data[data['Volume'] == maximum_volume]['High']) - float(data[data['Volume'] == maximum_volume]['Close']), 2)
            volume_max.append(maximum_volume)
            date_vol_max.append(date_vmax)
            
        else:
            close = float(data['Close'].tail(1))
            traded = int(data['Volume'].tail(1))
            average_volume = int(round((total_volume - traded) / (count - 1)))
            average_price = round((total_price - close) / (count - 1), 2)
            maximum_volume = int(data['Volume'].max())
            date_vmax = str(data.loc[lambda x: x['Volume'] == maximum_volume].reset_index()['Date'])[4:15]
            close_vmax = round(float(data[data['Volume'] == maximum_volume]['Close']), 2)
            candle_point = round(float(data[data['Volume'] == maximum_volume]['Close']) - float(data[data['Volume'] == maximum_volume]['Low']), 2)
            hc = round(float(data[data['Volume'] == maximum_volume]['High']) - float(data[data['Volume'] == maximum_volume]['Close']), 2)
            price.append(close)
            volume.append(traded)
            volume_avg.append(average_volume)
            price_avg.append(average_price)
            volume_max.append(maximum_volume)
            date_vol_max.append(date_vmax)

# Add information to dataset
get_Data(df, "31d")
df['Price'] = price
df['Volume'] = volume
df['Volume_Avg'] = volume_avg
df['Price_Avg'] = price_avg
df['Volume_Max'] = volume_max
df['Date_Vol_Max'] = date_vol_max


# In[6]:


df.style

