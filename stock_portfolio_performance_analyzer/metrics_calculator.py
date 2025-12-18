import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats

class MetricsCalculator: 
    """ Calculate portfolio performance metrics """

    def __init__(self):
        self.risk_free_rate = 0.03 # Example risk-free rate (3%)

    def calculate_returns(self, prices): 
        """
        Calculate daily returns from historical price data

        Args:
            prices (pd.Series): Historical price series
        Returns:
            pd.Series: Daily returns
        """
        return prices.pct_change().dropna()
    
    def calculate_total_return(self, initial_value, final_value):
        """
        Calculate total return

        Args:
            initial_value (float): Initial portfolio value
            final_value (float): Final portfolio value

        Returns:
            float: Total return
        """
        return final_value / initial_value - 1
    
    def calculate_annualized_return(self, total_return, years):
        """
        Calculate annualized return
        CAGR: Compound Annual Growth Rate
        CAGR = (Ending Value / Beginning Value)^(1 / Number of Years) - 1

        Args:
            total_return (float): Total return
            years (float): Number of years

        Returns:
            float: Annualized return
        """
        return (1 + total_return) ** (1 / years) - 1
    
    def calculate_volatility(self, returns, trading_days = 252, annualize = True):
        """
        Calculate volatility (standard deviation of returns)

        Args:
            returns (pd.Series): Daily returns
            annualize (bool): Whether to annualize the volatility

        Returns:
            float: Volatility
        """
        vol = returns.std()

        if annualize == True:
            vol = vol * np.sqrt(trading_days) # Assuming 252 trading days in a year
        return vol
    
    def calculate_sharpe_ratio(self, returns, trading_days = 252, risk_free_rate = None):
        """
        Calculate Sharpe Ratio
        Sharpe Ratio = (Rp - Rf) / sigma(p)

        Args:
            returns (pd.Series): Daily returns (in percentage)
            risk_free_rate (float): Annualized Risk-free Rate

        Returns:
            float: Sharpe Ratio
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        daily_Rf = risk_free_rate / trading_days
        excess_returns = returns - daily_Rf

        if excess_returns.std() == 0:
            return 0.0
        
        sharpe = excess_returns.mean() / excess_returns.std()
        sharpe_ratio = sharpe * np.sqrt(trading_days)

        return sharpe_ratio
    
    def calculate_sortino_ratio(self, returns, trading_days = 252, risk_free_rate = None):
        """
        Calculate Sortino Ratio
        Sortino Ratio = (Rp - Rf) / sigma(downside)


        Args:
            returns (pd.Series): Daily returns (in percentage)
            risk_free_rate (float): Annualized Risk-free Rate

        Returns:
            float: Sortino Ratio
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate

        daily_Rf = risk_free_rate / trading_days
        excess_returns = returns - daily_Rf

        # Filter the downside returns (Only negative returns)
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std()

        if downside_std == 0:
            return 0.0
        
        sortino = excess_returns.mean() / downside_std
        sortino_ratio = sortino * np.sqrt(trading_days)

        return sortino_ratio
    
    def calculate_max_drawdown(self, prices):
        """
        Calculate Maximum Drawdown (in the worst scenario)

        Args:
            prices (pd.Series): Historical price series

        Returns:
            float: Maximum Drawdown
        """

        # Calculate the running total return by compounding periodic returns
        cumulative = (1 + self.calculate_returns(prices)).cumprod()

        running_max = cumulative.expanding().max()

        drawdown = cumulative / running_max - 1

        max_drawdown = drawdown.min()

        bottom_date = drawdown.idxmin()
        peak_date = running_max[:bottom_date].idxmax()

        return max_drawdown, peak_date, bottom_date
    
    def calculate_beta(self, portfolio_returns, market_returns):
        """
        Calculate Beta of the portfolio against the market
        Beta = Cov(Rp, Rm) / Var(Rm)

        Args:
            portfolio_returns (pd.Series): Portfolio daily returns
            market_returns (pd.Series): Market daily returns
        Returns:
            float: Beta
        """
        aligned_data = pd.concat([portfolio_returns, market_returns], axis = 1).dropna()
        aligned_data.columns = ['portfolio', 'market']

        # Calculate covariance and variance
        covariance = aligned_data['portfolio'].cov(aligned_data['market'])
        market_variance = aligned_data['market'].var()

        if market_variance == 0:
            return 0.0
        
        beta = covariance / market_variance
        return beta
    
    def calculate_alpha(self, portfolio_return, beta, market_return, risk_free_rate = None):
        """
        Calculate Alpha of the portfolio
        E(r) = Rp - [ Rf + Beta * (Rm - Rf) ]

        Args:
            portfolio_return (float): Annualized portfolio return
            beta (float): Beta of the portfolio
            market_return (float): Annualized market return
            risk_free_rate (float): Annualized Risk-free Rate

        Returns:
            float: Alpha
        """

        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        # E(r) = Rp - [ Rf + Beta * (Rm - Rf) ]
        expected_return = risk_free_rate + beta * (market_return - risk_free_rate)
        alpha = portfolio_return - expected_return

        return alpha
    
    def calculate_win_ratio(self, returns):
        """
        Calculate the win ratio (percentage of positive return days)
        Calculate how much profit is generated for every dollar lost. 
        Args:
            returns (pd.Series): Daily returns
        Returns:
            float: Win Ratio
        """

        positive_return_days = (returns > 0).sum()
        total_days = len(returns)

        if total_days == 0:
            return 0.0
        
        win_ratio = positive_return_days / total_days
        return win_ratio
    
    def calculate_profit_to_loss_ratio(self, returns):
        """
        Calculate Profit to Loss Ratio
        
        Args:
            returns (pd.Series): Daily returns
        Returns:
            float: Profit-to-Loss Ratio
        """
        total_return = (1 + returns).prod() - 1

        loss = returns[returns < 0].abs().sum()

        # If the loss is zero, the ratio is infinite, indicating there is no risk.  
        if loss == 0:
            return float('inf')

        profit_to_loss_ratio = total_return / loss
        return profit_to_loss_ratio
    
if __name__ == "__main__":
    # Create sample data
    dates = pd.date_range('2023-01-01', '2024-01-01', freq='D')
    prices = pd.Series(100 * (1 + np.random.randn(len(dates)).cumsum() * 0.01), index=dates)
    
    calc = MetricsCalculator()
    
    # Test calculations
    returns = calc.calculate_returns(prices)
    print(f"Total Return: {calc.calculate_total_return(prices.iloc[0], prices.iloc[-1]):.2%}")
    print(f"Annualized Return: {calc.calculate_annualized_return(calc.calculate_total_return(prices.iloc[0], prices.iloc[-1]), 1):.2%}")
    print(f"Volatility: {calc.calculate_volatility(returns):.2%}")
    print(f"Sharpe Ratio: {calc.calculate_sharpe_ratio(returns):.2f}")
    print(f"Max Drawdown: {calc.calculate_max_drawdown(prices)[0]:.2%}")
    print(f"Win Rate: {calc.calculate_win_ratio(returns):.2%}")