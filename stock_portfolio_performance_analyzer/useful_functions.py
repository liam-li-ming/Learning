import pandas as pd


def load_portfolio_from_csv(filepath):
    """
    Load portfolio from CSV file
    
    CSV format:
    ticker,shares,purchase_price,purchase_date
    AAPL,10,150.0,2023-01-01
    GOOGL,5,100.0,2023-01-01
    
    Args:
        filepath (str): Path to CSV file
        
    Returns:
        dict: Portfolio dictionary or None if error
    """
    try:
        df = pd.read_csv(filepath)
        
        # Validate columns
        required_cols = ['ticker', 'shares', 'purchase_price', 'purchase_date']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"CSV must contain columns: {required_cols}")
        
        # Convert to portfolio dictionary
        portfolio = {}
        for _, row in df.iterrows():
            portfolio[row['ticker']] = {
                'shares': float(row['shares']),
                'purchase_price': float(row['purchase_price']),
                'purchase_date': row['purchase_date']
            }
        
        print(f"✓ Loaded {len(portfolio)} holdings from {filepath}")
        return portfolio
        
    except FileNotFoundError:
        print(f"✗ Error: File not found: {filepath}")
        return None
    except Exception as e:
        print(f"✗ Error loading portfolio from CSV: {str(e)}")
        return None