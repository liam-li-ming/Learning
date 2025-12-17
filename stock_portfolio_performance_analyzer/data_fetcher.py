import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

class DataFetcher:
    """
    Fetch stock market data from Yahoo Finance
    """

    def __init__(self):
        self.cache = {} 

    def fetch_stock_data(self, ticker, start_date = None, end_date = None):
        """
        Fetch historical stock data for a single ticker symbol.

        Args:
            ticker (str): Stock ticker symbol.
            start_date (str): Start date in "YYYY-MM-DD" format. 
            end_date (str): End date in "YYYY-MM-DD" format.

        Returns:
            pd.DataFrame: DataFrame containing historical price data.
        """

        try: 
            cache_key = f"{ticker}_{start_date}_{end_date}"
            if cache_key in self.cache:
                print(f"Using cached data for {ticker}")
                return self.cache[cache_key]
            print(f"→ Fetching data for {ticker} from Yahoo Finance...") 

            # Assign ticker object
            stock = yf.Ticker(ticker)

            # Set default start and end dates if not provided
            if start_date is None:
                start_date = (datetime.now() - timedelta(days = 365)).strftime("%Y-%m-%d")
            if end_date is None:
                end_date = datetime.now().strftime("%Y-%m-%d")

            # Fetch historical data
            df = stock.history(start = start_date, end = end_date)
            if df.empty: 
                print(f"No data found for {ticker}. Please check the ticker symbol.")
                return pd.DataFrame()
            self.cache[cache_key] = df

            return df
        
        except Exception as e:
            print(f"Error fetching data for {ticker}: {str(e)}")
            return pd.DataFrame()
        
    def get_current_price(self, ticker):
        """
        Get the current/last stock price for a ticker symbol
        Args:
            ticker (str): Stock ticker symbol
        Returns:
            float: Current price
        """

        try:
            stock = yf.Ticker(ticker)
            stock_info = stock.info

            
            price_fields = ['currentPrice', 'regularMarketPrice', 'previousClose']

            # Filter out None values and return the first available price
            for field in price_fields:
                if field in stock_info and stock_info[field] is not None:
                    return float(stock_info[field])
                
            hist = stock.history(period = "1d")
            if not hist.empty:
                return float(hist['Close'].iloc[-1])
                
            print(f"Could not get price for {ticker}")
            return None
        
        except Exception as e:
            print(f"Error fetching current price for {ticker}: {str(e)}")
            return None
        
    def get_stock_info(self, ticker):
        """
        Get basic stock information
        Args:
            ticker (str): Stock ticker symbol
        Returns:
            dictionary: Stock information
        """

        try: 
            stock = yf.Ticker(ticker)
            basic_info = stock.info

            return {
                'name': basic_info.get('longName', ticker),
                'sector': basic_info.get('sector', 'Unknown'),
                'industry': basic_info.get('industry', 'Unknown'),
                'currency': basic_info.get('currency', 'Unknown')
            }
        
        except Exception as e:
            print(f"Error getting info for {ticker}: {str(e)}")
            return {
                'name': ticker,
                'sector': 'Unknown',
                'industry': 'Unknown',
                'currency': 'Unknown'
            }
        
    def fetch_market_data(self, symbol, start_date = None, end_date = None):
        """
        Fetch historical market index data.

        Args:
            ticker (str): Market index ticker symbol. Default is "^IXIC" (NASDAQ).
            start_date (str): Start date in "YYYY-MM-DD" format.
            end_date (str): End date in "YYYY-MM-DD" format.

        Returns:
            pd.DataFrame: DataFrame containing historical market index data.
        """

        return self.fetch_stock_data(symbol, start_date, end_date)
    