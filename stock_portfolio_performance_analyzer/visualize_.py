import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy import stats
import pandas as pd
import numpy as np
from datetime import datetime
import os

class PortfolioVisualization: 
    """Create visualizations for protfolio performance"""

    def __init__(self, output_directory = 'output/charts'):
        """
        Args:
            output_directory (str): Directory to save visualization charts
        """
        # Get the directory where this file is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Create output path relative to the script directory
        self.output_directory = os.path.join(script_dir, output_directory)
        os.makedirs(self.output_directory, exist_ok = True) 

        self.figures = {}

    def plot_portfolio_value(self, portfolio_history, benchmark_data = None, 
                             benchmark_label = 'S&P 500', save = True):
        """
        Plot portfolio value over time

        Args:
            portfolio_history (pd.Series): Portfolio value over time
            benchmark_data (pd.DataFrame): Benchmark data (optional)
            benchmark_name (str): Name of benchmark
            save (bool): Whether to save the figure

        Returns:
            matplotlib.figure.Figure: The figure object
        """

        fig, ax = plt.subplots(figsize = (12, 6))
        # Plot portfolio value in Blue colour
        ax.plot(portfolio_history.index, portfolio_history.values, 
                linewidth = 2, label = 'Portfolio', color = '#2E86AB')

        if benchmark_data is not None and not benchmark_data.empty:
            # Normalize benchmark to start at the same value as portfolio
            benchmark_normalized = benchmark_data['Close'] / benchmark_data['Close'].iloc[0] * portfolio_history.iloc[0]
            
            ax.plot(benchmark_data.index, benchmark_normalized.values,
                   linewidth = 2, label = benchmark_label, 
                   color = '#A23B72', alpha = 0.7, linestyle = '--')
        
        # Set titles and labels
        ax.set_title('Portfolio Value Over Time', fontsize = 16, fontweight = 'bold', pad = 20)
        ax.set_xlabel('Date', fontsize = 12)
        ax.set_ylabel('Portfolio Value ($)', fontsize = 12)
        ax.legend(fontsize = 11, loc = 'upper left')
        ax.grid(True, alpha = 0.3)

        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Rotate x-axis labels
        plt.xticks(rotation = 45, ha = 'right')
        
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_directory, 'portfolio_value.png')
            plt.savefig(filepath, dpi = 800, bbox_inches = 'tight')
            print(f"Saved: {filepath}")
        
        self.figures['portfolio_value'] = fig
        return fig
    
    def plot_returns_distribution(self, returns, save=True):
        """
        Plot distribution of returns
        
        Args:
            returns (pd.Series): Daily returns
            save (bool): Whether to save the figure
            
        Returns:
            matplotlib.figure.Figure: The figure object
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Histogram
        ax1.hist(returns, bins = 50, alpha = 0.7, color = '#2E86AB', edgecolor = 'black')

        ax1.axvline(returns.mean(), color = '#A23B72', linestyle = '--', 
                   linewidth = 2, label = f'Mean: {returns.mean():.4f}')
        
        ax1.axvline(returns.median(), color = '#F18F01', linestyle = '--', 
                   linewidth = 2, label = f'Median: {returns.median():.4f}')
        
        # Set titles and labels
        ax1.set_title('Distribution of Daily Returns', fontsize = 14, fontweight = 'bold')
        ax1.set_xlabel('Daily Return', fontsize = 11)
        ax1.set_ylabel('Frequency', fontsize = 11)
        ax1.legend(fontsize = 10)
        ax1.grid(True, alpha = 0.3)
        
        # Q-Q plot (check for normality)
        stats.probplot(returns.dropna(), dist = "norm", plot = ax2)
        ax2.set_title('Q-Q Plot (Normality Check)', fontsize = 14, fontweight = 'bold')
        ax2.grid(True, alpha = 0.3)
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_directory, 'returns_distribution.png')
            plt.savefig(filepath, dpi = 800, bbox_inches = 'tight')
            print(f"Saved: {filepath}")
        
        self.figures['returns_distribution'] = fig
        return fig

    def plot_drawdown(self, portfolio_history, save = True):
        """
        Plot downdown over time
        
        Args:
            portfolio_history (pd.Series): Portfolio value over time
            save (bool): Whether to save the figure

        Returns:
            matplotlib.figure.Figure: The figure object
        """

        fig, ax = plt.subplots(figsize = (12, 6))

        cumulative = portfolio_history / portfolio_history.iloc[0]
        running_max = cumulative.expanding().max()
        drawdown = cumulative / running_max - 1

        ax.fill_between(drawdown.index, drawdown.values, 0, 
                        alpha = 0.3, color = '#C73E1D', label = 'Drawdown')
        ax.plot(drawdown.index, drawdown.values,
                linewidth = 2, color = '#C73E1D')
        
        # Point out the maximum drawdown
        max_dd_date = drawdown.idxmin()
        max_dd_value = drawdown.min()

        ax.scatter(max_dd_date, max_dd_value, color = '#A23B72', 
                  s = 100, zorder = 5, label = f'Max DD: {max_dd_value:.2%}')
        
        ax.annotate(f'{max_dd_value:.2%}', 
                   xy = (max_dd_date, max_dd_value),
                   xytext = (10, -10), textcoords = 'offset points',
                   fontsize = 10, fontweight = 'bold',
                   bbox = dict(boxstyle = 'round,pad=0.5', facecolor = 'yellow', alpha = 0.7))
        
        # Set titles and labels
        ax.set_title('Portfolio Drawdown Over Time', fontsize = 16, fontweight = 'bold', pad = 20)
        ax.set_xlabel('Date', fontsize = 12)
        ax.set_ylabel('Drawdown', fontsize = 12)
        ax.legend(fontsize = 11)
        ax.grid(True, alpha = 0.3)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1%}'))
        plt.xticks(rotation = 45, ha = 'right')
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_directory, 'drawdown.png')
            plt.savefig(filepath, dpi = 800, bbox_inches = 'tight')
            print(f"Saved: {filepath}")
        
        self.figures['drawdown'] = fig
        return fig
    
    def plot_allocation(self, holdings_performance, save = True):
        """
        Plot current portfolio allocation
        
        Args:
            holdings_performance (dict): Individual holdings performance
            save (bool): Whether to save the figure
            
        Returns:
            matplotlib.figure.Figure: The figure object
        """

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (14, 7))

        tickers = list(holdings_performance.keys())
        values = [holdings_performance[t]['current_value'] for t in tickers]

        # Pie chart for allocation
        wedges, texts, autotexts = ax1.pie(values, labels = tickers, autopct = '%1.1f%%',
                                            colors = plt.cm.Set3(range(len(tickers))), startangle = 90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')
        ax1.set_title('Portfolio Allocation', fontsize = 14, fontweight = 'bold')

        # Bar chart with values
        ax2.barh(tickers, values, color = plt.cm.Set3(range(len(tickers))))
        ax2.set_xlabel('Current Value ($)', fontsize = 11)
        ax2.set_title('Holdings by Value', fontsize = 14, fontweight = 'bold')
        ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        ax2.grid(True, alpha = 0.3, axis = 'x')
        
        plt.tight_layout()

        if save:
            filepath = os.path.join(self.output_directory, 'allocation.png')
            plt.savefig(filepath, dpi = 800, bbox_inches = 'tight')
            print(f"Saved: {filepath}")
        
        self.figures['allocation'] = fig
        return fig
    
    def plot_individual_performance(self, holdings_performance, save = True):
        """
        Plot individual holdings performance comparison
        
        Args:
            holdings_performance (dict): Individual holdings performance
            save (bool): Whether to save the figure
            
        Returns:
            matplotlib.figure.Figure: The figure object
        """
        fig, ax = plt.subplots(figsize = (12, 6))

        tickers = list(holdings_performance.keys())
        returns = [holdings_performance[t]['total_return'] * 100 for t in tickers]

        # Positive returns in green, negative in red
        colors = ['#06A77D' if r >= 0 else '#C73E1D' for r in returns]

        bars = ax.bar(tickers, returns, color = colors, edgecolor = 'black', linewidth = 1.5)

        # Display a zero line for reference
        ax.axhline(y = 0, color = 'black', linewidth = 0.8, linestyle = '--') 

        # Set titles and labels
        ax.set_title('Individual Holdings Performance', fontsize = 16, fontweight = 'bold', pad = 20)
        ax.set_xlabel('Ticker', fontsize = 12)
        ax.set_ylabel('Total Return (%)', fontsize = 12)
        ax.grid(True, alpha = 0.3, axis = 'y')
        
        plt.tight_layout()

        if save:
            filepath = os.path.join(self.output_directory, 'individual_performance.png')
            plt.savefig(filepath, dpi = 800, bbox_inches = 'tight')
            print(f"Saved: {filepath}")
        
        self.figures['individual_performance'] = fig
        return fig
    
    def plot_risk_return_scatter(self, holdings_data, holdings_performance, save = True):
        """
        Plot risk-return scatter for individual holdings
        
        Args:
            holdings_data (dict): Historical data for each holding
            holdings_performance (dict): Performance metrics
            save (bool): Whether to save the figure
            
        Returns:
            matplotlib.figure.Figure: The figure object
        """

        fig, ax = plt.subplots(figsize = (10, 8))

        # Prepare risk and return for each holding
        for ticker in holdings_data.keys():
            if ticker not in holdings_performance:
                continue

            prices = holdings_data[ticker]['Close']
            returns = prices.pct_change().dropna()

            # Calculate annualized return and volatility
            annualized_return = holdings_performance[ticker]['annualized_return'] * 100
            trading_days = 252
            volatility = returns.std() * np.sqrt(trading_days) * 100  # Annualized volatility, assuming 252 trading days

            # Size based on portfolio weight
            size = holdings_performance[ticker]['weight'] * 1000

            ax.scatter(volatility, annualized_return, s = size, alpha = 0.6, 
                      edgecolors = 'black', linewidth = 1.5)
            
            ax.annotate(ticker, (volatility, annualized_return),
                       fontsize = 11, fontweight = 'bold',
                       xytext = (5, 5), textcoords = 'offset points')

        # Add quadrant lines
        ax.axhline(y = 0, color = 'gray', linestyle = '--', linewidth = 1, alpha = 0.5)
        ax.axvline(x = ax.get_xlim()[0] + (ax.get_xlim()[1] - ax.get_xlim()[0])/2,
                   color = 'gray', linestyle = '--', linewidth = 1, alpha = 0.5)

        # Set titles and labels
        ax.set_title('Risk-Return Profile of Holdings', fontsize = 16, fontweight = 'bold', pad = 20)
        ax.set_xlabel('Volatility (Annualized %)', fontsize = 12)
        ax.set_ylabel('Return (Annualized %)', fontsize = 12)
        ax.grid(True, alpha = 0.3)

        # Add legend for bubble size
        legend_elements = [Line2D([0], [0], marker = 'o', color = 'w',
                                markerfacecolor = 'gray', markersize = ms,

                                alpha = 0.6, label = f'{w}% of portfolio')
                                for ms, w in [(8, 10), (12, 20), (16, 30)]]

        ax.legend(handles = legend_elements, loc = 'best', fontsize = 10,
                  title = 'Portfolio Weight', title_fontsize = 11)
        plt.tight_layout()

        if save:
            filepath = os.path.join(self.output_directory, 'risk_return.png')
            plt.savefig(filepath, dpi = 800, bbox_inches = 'tight')
            print(f"Saved: {filepath}")

        self.figures['risk_return'] = fig
        return fig

    def plot_rolling_returns(self, portfolio_history, window = 30, save = True):
        """
        Plot rolling returns
        
        Args:
            portfolio_history (pd.Series): Portfolio value over time
            window (int): Rolling window in days
            save (bool): Whether to save the figure
            
        Returns:
            matplotlib.figure.Figure: The figure object
        """
        fig, ax = plt.subplots(figsize = (12, 6))

        returns = portfolio_history.pct_change().dropna()
        rolling_returns = returns.rolling(window = window).mean() * 100  # Convert to percentage

        # Plot rolling returns with positive and negative areas
        ax.plot(rolling_returns.index, rolling_returns.values, linewidth = 2, color = '#2E86AB')
        ax.axhline(y = 0, color = 'black', linestyle = '-', linewidth = 0.8)
        ax.fill_between(rolling_returns.index, rolling_returns.values, 0,
                        where = (rolling_returns.values >= 0), 
                        alpha = 0.3, color = '#06A77D', label = 'Positive')
        ax.fill_between(rolling_returns.index, rolling_returns.values, 0,
                        where = (rolling_returns.values < 0), 
                        alpha = 0.3, color = '#C73E1D', label = 'Negative')

        # Set titles and labels
        ax.set_title(f'{window}-Day Rolling Returns', fontsize = 16, fontweight = 'bold', pad = 20)
        ax.set_xlabel('Date', fontsize = 12)
        ax.set_ylabel('Rolling Return (%)', fontsize = 12)
        ax.legend(fontsize = 11)
        ax.grid(True, alpha = 0.3)
        plt.xticks(rotation = 45, ha = 'right')
        plt.tight_layout()

        if save:
            filepath = os.path.join(self.output_directory, 'rolling_returns.png')
            plt.savefig(filepath, dpi = 800, bbox_inches = 'tight')
            print(f"Saved: {filepath}")
        
        self.figures['rolling_returns'] = fig
        return fig
    
    def create_all_charts(self, analyzer):
        """
        Create all charts at once
        
        Args:
            analyzer (PortfolioAnalyzer): Portfolio analyzer object
        """
        
        # Retrieve data from analyzer
        portfolio_history = analyzer.portfolio_history
        benchmark_data = analyzer.benchmark_data
        holdings_performance = analyzer.calculate_each_holding_performance()
        
        # Calculate returns
        returns = portfolio_history.pct_change().dropna()
        
        # Create all charts
        self.plot_portfolio_value(portfolio_history, benchmark_data)
        self.plot_returns_distribution(returns)
        self.plot_drawdown(portfolio_history)
        self.plot_allocation(holdings_performance)
        self.plot_individual_performance(holdings_performance)
        self.plot_risk_return_scatter(analyzer.holdings_data, holdings_performance)
        self.plot_rolling_returns(portfolio_history)
        
        print(f"\n All charts created and saved to: {self.output_directory}")
    
    def show_all(self):
        """Display all created figures"""
        plt.show()
    
    def close_all(self):
        """Close all figure windows"""
        plt.close('all')
