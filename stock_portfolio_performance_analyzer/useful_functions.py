import pandas as pd
import os
from datetime import datetime
from PDF_generate_ import ReportGenerator
from portfolio_analyzer import PortfolioAnalyzer
from visualize_ import PortfolioVisualization


def load_portfolio_from_csv(filepath):
    """
    Load portfolio from CSV file
    
    CSV format:
    ticker, shares, purchase_price, purchase_date
    AAPL, 10, 150.0, 2023-01-01
    GOOGL, 5, 100.0, 2023-01-01
    
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
        print(f"Error: File not found: {filepath}")
        return None
    except Exception as e:
        print(f"Error loading portfolio from CSV: {str(e)}")
        return None
    
def create_demo_portfolio_csv(filepath = 'data/demo_portfolio.csv'):
    """
    Create a sample portfolio CSV file for testing
    
    Args:
        filepath (str): Where to save the sample CSV
        
    Returns:
        str: Path to created file
    """
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok = True)

    # Sample portfolio data
    sample_data = {
        'ticker': ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN'],
        'shares': [10, 10, 10, 10, 10],
        'purchase_price': [150.0, 100.0, 250.0, 200.0, 120.0],
        'purchase_date': ['2023-01-01', '2023-01-01', '2023-01-01', '2023-01-01', '2023-01-01']
    }

    df = pd.DataFrame(sample_data)
    df.to_csv(filepath, index = False)

    print(f"Sample portfolio CSV created: {filepath}")
    return filepath

def display_portfolio(portfolio):
    """
    Display portfolio holdings in a readable format
    
    Args:
        portfolio (dict): Portfolio dictionary
    """
    print("\n" + "="*70)
    print("DEMO PORTFOLIO")
    print("="*70)
    print(f"{'Ticker':<10} {'Shares':>10} {'Purchase Price':>15} {'Purchase Date':>15}")
    print("-"*70)
    
    total_invested = 0
    for ticker, data in portfolio.items():
        purchase_value = data['shares'] * data['purchase_price']
        total_invested = total_invested + purchase_value
        print(f"{ticker:<10} {data['shares']:>10.0f} ${data['purchase_price']:>14,.2f} {data['purchase_date']:>15}")
    
    print("-"*70)
    print(f"{'TOTAL INVESTED':>40} ${total_invested:>14,.2f}")
    print("="*70)

def run_full_analysis(portfolio, benchmark='^GSPC', generate_pdf=True, show_charts=False):
    """
    Run complete portfolio analysis workflow
    
    This is the main function that orchestrates the entire analysis:
    1. Analyzes the portfolio (fetches data, calculates metrics)
    2. Creates visualizations (7 charts)
    3. Generates PDF report (optional)
    4. Shows summary
    
    Args:
        portfolio (dict): Portfolio holdings
        benchmark (str): Benchmark ticker (default: S&P 500)
        generate_pdf (bool): Whether to generate PDF report
        show_charts (bool): Whether to display charts interactively
        
    Returns:
        tuple: (analyzer, visualizer, report_path)
    """
    print("\n" + "="*70)
    print(" "*20 + "PORTFOLIO ANALYZER")
    print("="*70)
    
    # Display what we're analyzing
    display_portfolio(portfolio)
    
    # Step 1: Run portfolio analysis
    print("\n" + "="*70)
    print("[STEP 1/4] RUNNING PORTFOLIO ANALYSIS")
    print("="*70)
    analyzer = PortfolioAnalyzer(portfolio, benchmark=benchmark)
    analyzer.run_analysis()
    
    # Step 2: Create visualizations
    print("\n" + "="*70)
    print("[STEP 2/4] CREATING VISUALIZATIONS")
    print("="*70)
    visualizer = PortfolioVisualization()
    visualizer.create_all_charts(analyzer)
    
    # Step 3: Generate PDF report
    report_path = None
    if generate_pdf:
        print("\n" + "="*70)
        print("[STEP 3/4] GENERATING PDF REPORT")
        print("="*70)
        report_gen = ReportGenerator()
        report_path = report_gen.generate_report(analyzer)
    else:
        print("\n" + "="*70)
        print("[STEP 3/4] SKIPPING PDF GENERATION")
        print("="*70)
    
    # Step 4: Display summary
    print("\n" + "="*70)
    print("[STEP 4/4] ANALYSIS COMPLETE!")
    print("="*70)
    
    print("\n" + "="*70)
    print("OUTPUT FILES")
    print("="*70)
    print(f"📊 Charts saved to:   stock_portfolio_performance_analyzer/output/charts/")
    if report_path:
        print(f"📄 Report saved to:   {report_path}")
    print("="*70)
    
    # Optionally show charts
    if show_charts:
        print("\nDisplaying charts... (close chart windows to continue)")
        visualizer.show_all()
    
    return analyzer, visualizer, report_path

def interactive_mode():
    """
    Interactive mode for user input
    Guides the user through the process step-by-step
    """
    print("\n" + "="*70)
    print(" "*15 + "PORTFOLIO ANALYZER - INTERACTIVE MODE")
    print("="*70)
    
    # Step 1: Choose input method
    print("\n📋 How would you like to input your portfolio?")
    print("\n1. Load from CSV file")
    print("2. Use sample portfolio (for demo)")
    print("3. Manual entry (enter stocks one by one)")
    print("4. Exit")
    
    choice = input("\n👉 Enter choice (1-4): ").strip()
    
    portfolio = None
    
    # Option 1: Load from CSV
    if choice == '1':
        filepath = input("\n📁 Enter CSV file path (e.g., data/my_portfolio.csv): ").strip()
        portfolio = load_portfolio_from_csv(filepath)
        
        if portfolio is None:
            print("\n❌ Failed to load portfolio. Please check the file and try again.")
            return
    
    # Option 2: Sample portfolio
    elif choice == '2':
        print("\n🔄 Creating sample portfolio...")
        sample_path = create_demo_portfolio_csv()
        portfolio = load_portfolio_from_csv(sample_path)
    
    # Option 3: Manual entry
    elif choice == '3':
        print("\n✏️  Manual Portfolio Entry")
        print("Enter each stock position. Type 'done' when finished.\n")
        
        portfolio = {}
        
        while True:
            ticker = input("Enter ticker symbol (or 'done' to finish): ").strip().upper()
            
            if ticker == 'DONE':
                if len(portfolio) == 0:
                    print("\n❌ No stocks entered. Please add at least one position.")
                    continue
                break
            
            if ticker == '':
                continue
            
            try:
                shares = float(input(f"  Number of shares: "))
                purchase_price = float(input(f"  Purchase price per share: $"))
                purchase_date = input(f"  Purchase date (YYYY-MM-DD): ").strip()
                
                # Validate date format
                datetime.strptime(purchase_date, '%Y-%m-%d')
                
                portfolio[ticker] = {
                    'shares': shares,
                    'purchase_price': purchase_price,
                    'purchase_date': purchase_date
                }
                
                print(f"  ✅ Added {ticker} to portfolio\n")
                
            except ValueError as e:
                print(f"  ❌ Invalid input: {str(e)}. Please try again.\n")
                continue
    
    # Option 4: Exit
    elif choice == '4':
        print("\n👋 Goodbye!")
        return
    
    else:
        print("\n❌ Invalid choice. Please run the program again.")
        return
    
    # Check if we have a valid portfolio
    if portfolio is None or len(portfolio) == 0:
        print("\n❌ No portfolio to analyze. Exiting.")
        return
    
    # Step 2: Choose benchmark
    print("\n" + "="*70)
    print("📈 BENCHMARK SELECTION")
    print("="*70)
    print("\nCommon benchmarks:")
    print("  ^GSPC  - S&P 500 (US large cap)")
    print("  ^DJI   - Dow Jones Industrial Average")
    print("  ^IXIC  - NASDAQ Composite (tech-heavy)")
    print("  ^RUT   - Russell 2000 (small cap)")
    
    benchmark = input("\n👉 Enter benchmark ticker (default: ^GSPC): ").strip() or '^GSPC'
    
    # Step 3: PDF report option
    print("\n" + "="*70)
    print("📄 PDF REPORT")
    print("="*70)
    gen_pdf = input("\n👉 Generate PDF report? (y/n, default: y): ").strip().lower()
    generate_pdf = gen_pdf != 'n'
    
    # Step 4: Show charts option
    show = input("👉 Display charts interactively? (y/n, default: n): ").strip().lower()
    show_charts = show == 'y'
    
    # Run the analysis
    print("\n🚀 Starting analysis...\n")
    run_full_analysis(portfolio, benchmark=benchmark, 
                     generate_pdf=generate_pdf, show_charts=show_charts)


def quick_demo():
    """
    Quick demo with hardcoded sample portfolio
    Fastest way to see the tool in action
    """
    print("\n" + "="*70)
    print(" "*20 + "QUICK DEMO MODE")
    print("="*70)
    
    # Hardcoded sample portfolio
    portfolio = {
        'AAPL': {
            'shares': 10,
            'purchase_price': 150.0,
            'purchase_date': '2023-01-01'
        },
        'GOOGL': {
            'shares': 10,
            'purchase_price': 100.0,
            'purchase_date': '2023-01-01'
        },
        'MSFT': {
            'shares': 10,
            'purchase_price': 250.0,
            'purchase_date': '2023-01-01'
        }
    }
    
    print("\n📊 Running demo with sample portfolio...")
    print("(AAPL, GOOGL, MSFT purchased on 2023-01-01)")
    
    run_full_analysis(portfolio, benchmark='^GSPC', generate_pdf=True)

def print_help():
    """Print help/usage information"""
    print("\n" + "="*70)
    print(" "*20 + "PORTFOLIO ANALYZER - HELP")
    print("="*70)
    print("\nUSAGE:")
    print("\n1. Interactive mode (recommended for first-time users):")
    print("   python main.py")
    
    print("\n2. With CSV file:")
    print("   python main.py data/my_portfolio.csv")
    
    print("\n3. Quick demo:")
    print("   python main.py --demo")
    
    print("\n4. Show this help:")
    print("   python main.py --help")
    
    print("\n" + "="*70)
    print("CSV FILE FORMAT")
    print("="*70)
    print("\nYour CSV file should have these columns:")
    print("ticker,shares,purchase_price,purchase_date")
    print("\nExample:")
    print("AAPL,10,150.0,2023-01-01")
    print("GOOGL,5,100.0,2023-01-01")
    
    print("\n" + "="*70)
    print("OUTPUT")
    print("="*70)
    print("\nThe analyzer generates:")
    print("  📊 7 charts in stock_portfolio_performance_analyzer/output/charts/")
    print("  📄 PDF report in stock_portfolio_performance_analyzer/output/reports/")
    print("  📋 Console summary")
    
    print("\n" + "="*70)
    print("REQUIREMENTS")
    print("="*70)
    print("\nMake sure you've installed dependencies:")
    print("  pip install -r requirements.txt")
    
    print("\n" + "="*70 + "\n")