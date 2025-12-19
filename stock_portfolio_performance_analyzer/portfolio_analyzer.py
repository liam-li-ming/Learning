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

        all_dates = sorted(all_dates)

        portfolio_values = pd.Series(index = all_dates, dtype = float)

        # Calculate portfolio value in each date
        for date in all_dates:
            total_value = 0.0

            for ticker, holding in self.portfolio.items():
                if ticker not in self.holdings_data:
                    continue

                df = self.holdings_data[ticker]

                purchase_date = pd.to_datetime(holding["purchase_date"]).tz_localize(date.tz)
                # To avoid using data before purchase date
                if date < purchase_date:
                    continue
                # Retrieve price on the date or the closest previous date
                if date in df.index:
                    price = df.loc[date, "Close"]
                else: 
                    available_prices = df.loc[:date, 'Close']
                    if not available_prices.empty:
                        price = available_prices.iloc[-1]
                    else:
                        continue

                # Add the value of the holding to total value
                value = holding["shares"] * price
                total_value = total_value + value

            portfolio_values[date] = total_value
        # Filter out NaN values
        self.portfolio_history = portfolio_values.dropna()
        print(f"Portfolio history value calculated ({len(self.portfolio_history)} days)")

    def calculate_metrics(self):
        """
        Calculate all profolio performance metrics
        """

        if self.portfolio_history is None or self.portfolio_history.empty:
            print("No portfolio history available.")
            return
        
        portfolio_returns = self.calculator.calculate_returns(self.portfolio_history)

        initial_value = self.portfolio_history.iloc[0]
        final_value = self.portfolio_history.iloc[-1]

        # Get the number of days and years
        days = (self.portfolio_history.index[-1] - self.portfolio_history.index[0]).days
        years = days / 365.25

        # Calculate total and annualized return
        total_return = self.calculator.calculate_total_return(initial_value, final_value)
        annualized_return = self.calculator.calculate_annualized_return(total_return, years)

        # Calculate volatility, Sharpe ratio, Sortino ratio
        volatility = self.calculator.calculate_volatility(portfolio_returns)
        sharpe_ratio = self.calculator.calculate_sharpe_ratio(portfolio_returns)
        sortino_ratio = self.calculator.calculate_sortino_ratio(portfolio_returns)

        # Drawdown calculations and downside risk
        max_drawdown, peak_date, bottom_date = self.calculator.calculate_max_drawdown(self.portfolio_history)

        # Win ratio calculation
        win_ratio = self.calculator.calculate_win_ratio(portfolio_returns)

        if self.benchmark_data is not None and not self.benchmark_data.empty:
            benchmark_returns = self.calculator.calculate_returns(self.benchmark_data['Close'])
            beta = self.calculator.calculate_beta(portfolio_returns, benchmark_returns)

            # Benchmark return and annualized return
            benchmark_total_return = self.calculator.calculate_total_return(
                self.benchmark_data['Close'].iloc[0],
                self.benchmark_data['Close'].iloc[-1]
            )
            benchmark_annualized_return = self.calculator.calculate_annualized_return(
                benchmark_total_return,
                years
            )
            # Alpha of the portfolio
            alpha = self.calculator.calculate_alpha(
                annualized_return,
                beta,
                benchmark_annualized_return
            )
        else: 
            alpha = None
            beta = None
            benchmark_annualized_return = None
        
        # Store all metrics
        self.metrics = {
            'initial_value': initial_value,
            'final_value': final_value,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'max_dd_peak_date': peak_date,
            'max_dd_trough_date': bottom_date,
            'win_rate': win_ratio,
            'beta': beta,
            'alpha': alpha,
            'benchmark_return': benchmark_annualized_return,
            'days': days,
            'years': years
        }
        print("Metrics calculation complete.")

    def calculate_each_holding_performance(self):
        """Calculate performance metrics for each holding"""

        holdings_performance = { }

        for ticker, holding in self.portfolio.items():
            if ticker not in self.holdings_data or ticker not in self.current_prices:
                continue

            # Gather purchase info
            shares = holding["shares"]
            purchase_price = holding["purchase_price"]
            purchase_date = holding["purchase_date"]
            # Get current price
            current_price = self.current_prices[ticker]

            # Calculate returns
            purchase_value = shares * purchase_price
            current_value = shares * current_price
            total_return = current_value / purchase_value - 1

            # Holding period
            holding_days = (datetime.now() - pd.to_datetime(purchase_date)).days
            holding_years = holding_days / 365.25

            # Calculate annualized return
            if holding_years > 0:
                # Calculate CAGR
                annualized_return = (1 + total_return) ** (1 / holding_years) - 1
            else:
                annualized_return = 0.0

            # Store the holding performance
            holdings_performance[ticker] = {
                'shares': shares,
                'purchase_price': purchase_price,
                'current_price': current_price,
                'invested': purchase_value,
                'current_value': current_value,
                'gain_loss': current_value - purchase_value,
                'total_return': total_return,
                'annualized_return': annualized_return,
                'days_held': holding_days,
                'weight': current_value / self.metrics['final_value'] if 'final_value' in self.metrics else 0
            }
        return holdings_performance
    
    def print_performance_summary(self): 
        """ *** Print a summary of portfolio performance metrics *** """
        if not self.metrics:
            print("No metrics calculated.")
            return

        # Portfolio overview
        print(f"\n{'PORTFOLIO OVERVIEW':-^50}")
        print(f"Initial Value:        ${self.metrics['initial_value']:>15,.4f}")
        print(f"Current Value:        ${self.metrics['final_value']:>15,.4f}")
        print(f"Gain/Loss:            ${self.metrics['final_value'] - self.metrics['initial_value']:>15,.4f}")
        print(f"Time Period:          {self.metrics['days']:>15} days ({self.metrics['years']:.4f} years)")

        # Returns
        print(f"\n{'RETURNS':-^50}")
        print(f"Total Return:         {self.metrics['total_return']:>15.4%}")
        print(f"Annualized Return:    {self.metrics['annualized_return']:>15.4%}")

        if self.metrics['benchmark_return'] is not None:
            print(f"Benchmark Return:     {self.metrics['benchmark_return']:>15.4%}")
            excess_return = self.metrics['annualized_return'] - self.metrics['benchmark_return']
            print(f"Excess Return:        {excess_return:>15.4%}")

        # Risk metrics
        print(f"\n{'RISK METRICS':-^50}")
        print(f"Volatility:           {self.metrics['volatility']:>15.4%}")
        print(f"Sharpe Ratio:         {self.metrics['sharpe_ratio']:>15.4f}")
        print(f"Sortino Ratio:        {self.metrics['sortino_ratio']:>15.4f}")
        print(f"Max Drawdown:         {self.metrics['max_drawdown']:>15.4%}")
        print(f"  Peak Date:          {self.metrics['max_dd_peak_date'].strftime('%Y-%m-%d'):>15}")
        print(f"  Trough Date:        {self.metrics['max_dd_trough_date'].strftime('%Y-%m-%d'):>15}")
        print(f"Win Rate:             {self.metrics['win_rate']:>15.4%}")

        if self.metrics['beta'] is not None:
            print(f"\n{'MARKET SENSITIVITY':-^50}")
            print(f"Beta:                 {self.metrics['beta']:>15.4f}")
            if self.metrics['alpha'] is not None:
                print(f"Alpha:                {self.metrics['alpha']:>15.4%}")
        
        # Individual holdings
        print(f"\n{'INDIVIDUAL HOLDINGS':-^50}")
        holdings_perf = self.calculate_each_holding_performance()
        
        for ticker, perf in sorted(holdings_perf.items(), 
                                   key=lambda x: x[1]['current_value'], 
                                   reverse=True):
            print(f"\n{ticker} - {self.stock_info.get(ticker, {}).get('name', ticker)}")
            print(f"  Shares:             {perf['shares']:>15,.0f}")
            print(f"  Purchase Price:     ${perf['purchase_price']:>15,.4f}")
            print(f"  Current Price:      ${perf['current_price']:>15,.4f}")
            print(f"  Invested:           ${perf['invested']:>15,.4f}")
            print(f"  Current Value:      ${perf['current_value']:>15,.4f}")
            print(f"  Gain/Loss:          ${perf['gain_loss']:>15,.4f}")
            print(f"  Total Return:       {perf['total_return']:>15.4%}")
            print(f"  Portfolio Weight:   {perf['weight']:>15.4%}")

    def run_analysis(self):
        """Run complete portfolio analysis"""
        self.fetch_all_data()
        self.calculate_portfolio_value_history()
        self.calculate_metrics()
        self.print_performance_summary()

if __name__ == "__main__":
    # Sample portfolio
    portfolio = {
        'AAPL': {
            'shares': 10,
            'purchase_price': 150.0,
            'purchase_date': '2023-01-01'
        },
        'GOOGL': {
            'shares': 5,
            'purchase_price': 100.0,
            'purchase_date': '2023-01-01'
        },
        'MSFT': {
            'shares': 80,
            'purchase_price': 250.0,
            'purchase_date': '2023-01-01'
        }
    }

    analyzer = PortfolioAnalyzer(portfolio)
    analyzer.run_analysis()