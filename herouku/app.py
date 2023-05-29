import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime, timedelta
from newsapi import NewsApiClient

# Define the News API client
newsapi = NewsApiClient(api_key='30f892ddb31d43709e5a7a77833f824a')

# Define the layout using Streamlit components
st.title('Stonks20.com')
stock_symbol = st.text_input('Enter the stock symbol:', 'AAPL')
date_range = st.date_input('Select the dates:', [(datetime.today() - timedelta(days=365)).date(), datetime.today().date()])
submit_button = st.button('Submit')

# Fetch stock data and update the graphs
if submit_button:
    try:
        start_date, end_date = date_range
        stock_data = yf.download(stock_symbol, start=start_date, end=end_date)

        # Create a Candlestick chart
        candlestick_fig = go.Figure(data=[go.Candlestick(x=stock_data.index,
                                                         open=stock_data['Open'],
                                                         high=stock_data['High'],
                                                         low=stock_data['Low'],
                                                         close=stock_data['Close'])])
        candlestick_fig.update_layout(
            title=f'{stock_symbol} Stock Price',
            xaxis_title='Date',
            yaxis_title='Price',
            autosize=True
        )
        st.plotly_chart(candlestick_fig)

        # Create a Volume chart
        volume_fig = go.Figure(data=[go.Bar(x=stock_data.index,
                                            y=stock_data['Volume'])])
        volume_fig.update_layout(
            title='Volume',
            xaxis_title='Date',
            yaxis_title='Volume',
            autosize=True
        )
        st.plotly_chart(volume_fig)

        # Create a Moving Average chart
        moving_average_fig = go.Figure(data=[
            go.Scatter(x=stock_data.index, y=stock_data['Close'], name='Price'),
            go.Scatter(x=stock_data.index, y=stock_data['Close'].rolling(window=50).mean(), name='50-day MA'),
            go.Scatter(x=stock_data.index, y=stock_data['Close'].rolling(window=200).mean(), name='200-day MA')
        ])
        moving_average_fig.update_layout(
            title='Moving Averages',
            xaxis_title='Date',
            yaxis_title='Price',
            autosize=True
        )
        st.plotly_chart(moving_average_fig)

        # Create an RSI chart
        delta = stock_data['Close'].diff()
        gain = delta.mask(delta < 0, 0)
        loss = -delta.mask(delta > 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        rsi_fig = go.Figure(data=[go.Scatter(x=stock_data.index, y=rsi, name='RSI', line=dict(color='blue'))])
        rsi_fig.update_layout(
            title='Relative Strength Index (RSI)',
            xaxis_title='Date',
            yaxis_title='RSI',
            autosize=True
        )
        st.plotly_chart(rsi_fig)

    except Exception as e:
        st.error(f'Error: {str(e)}')

# Display news articles
news_articles = newsapi.get_everything(q=stock_symbol, language='en', sort_by='publishedAt')['articles']
if news_articles:
    st.subheader('News')
    for article in news_articles:
        st.markdown(f"## {article['title']}")
        st.markdown(article['description'])
        st.markdown(f"[Read More]({article['url']})")
else:
    st.warning('No news articles found for the given stock symbol.')