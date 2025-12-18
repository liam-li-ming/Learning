import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data_fetcher import DataFetcher
from metrics_calculator import MetricsCalculator

class PortfolioAnalyzer:
    """
    Main portfolio analyzer class
    
    Portfolio format:
    {
        'VOO': {
            'shares': 10,
            'purchase_price': 150.0,
            'purchase_date': '2023-01-01'
        },
        'QQQ': {
            'shares': 5,
            'purchase_price': 100.0,
            'purchase_date': '2023-01-01'
        }
    }
    """

    def __init__(self, portfolio, benchmark = "^IXIC"):
        """
        Args:
            portfolio (dict): Portfolio dictionary
            benchmark (str): Benchmark ticker symbol (default: NASDAQ)
        """
        self.portfolio = portfolio
        self.benchmark = benchmark
        self.fetcher = DataFetcher()
        self.calculator = MetricsCalculator()

        self.holdings_data = {} # Historical data for each holding
        self.current_prices = {} # Current prices for each holding
        self.stock_info = {} # Stock information

        self.portfolio_history = None # Portfolio historical value
        self.benchmark_data = None # Benchmark historical data

        self.metrics = {} # Calculated metrics

    def fetch_all_data(self):
        """ Fetch all data for portfolio and benchmark """
        print("Fetching data...")

        # Find the first purchase date
        earliest_date = min([holding["purchase_date"] for holding in self.portfolio.values()])
        current_date = datetime.now().strftime("%Y-%m-%d")
        print(f"\nDate range: {earliest_date} to {current_date}")

        # Fetch data for each holding in the portfolio
        for ticker, holding in self.portfolio.items():
            print(f"\n Reading {ticker}...")
            
            # Fetch historical data
            df = self.fetcher.fetch_stock_data(
                ticker, 
                start_date = holding["purchase_date"], 
                end_date = current_date
                )

            if not df.empty: 
                self.holdings_data[ticker] = df
                # Fetch current price
                current_price = self.fetcher.get_current_price(ticker)
                self.current_prices[ticker] = current_price

                # Fetch stock info
                info = self.fetcher.get_stock_info(ticker)
                self.stock_info[ticker] = info

                print(f" Fetched {len(df)} days ")
                print(f" Current price: ${current_price:.4f}")
                print(f" Company: {info['name']}")
            else:
                print(f" No data for {ticker}")

        # Fetch benchmark data
        print(f"\n Reading benchmark {self.benchmark}...")
        self.benchmark_data = self.fetcher.fetch_stock_data(
            self.benchmark, 
            start_date = earliest_date,
            end_date = current_date
        )

        # Check the benchmark data
        if not self.benchmark_data.empty:
            print(f" Fetched {len(self.benchmark_data)} days for benchmark")
        else:
            print(f" No data for benchmark {self.benchmark}")
        print("\nData fetching complete.")

    def calculate_portfolio_value_history(self):
        """ Calculate the historical value of the portfolio """

        # Build a date range
        all_dates = set()
        for df in self.holdings_data.values():
            all_dates.update(df.index)

        all_dates = sorted(all_dates, reverse = True)

        portfolio_values = pd.Series(index = all_dates, dtype = float)

        # Calculate portfolio value in each date
        for date in all_dates:
            total_value = 0.0

            for ticker, holding in self.portfolio.items():
                if ticker not in self.holdings_data:
                    continue

                df = self.holdings_data[ticker]

                purchase_date = pd.to_datetime(holding["purchase_date"])
                # To avoid using data before purchase date
                if date < purchase_date:
                    continue
                # Retrieve price on the date or the closest previous date
                if date in df.index:
                    price = df.loc[date, "Close"]
                else: 
                    available_prices = df.loc[:date, 'Close']

                # Add the value of the holding to total value
                value = holding["shares"] * price
                total_value = total_value + value

            portfolio_values[date] = total_value
        # Filter out NaN values
        self.portfolio_history = portfolio_values.dropna()
        print(f"Portfolio history value calculated ({len(self.portfolio_history)} days)")

    def calculate_metrics(self):
        