import pandas as pd
from portfolio_analyzer import PortfolioAnalyzer
from visualize_ import PortfolioVisualization
from PDF_generate_ import ReportGenerator
import os
import sys
from datetime import datetime
from useful_functions import *

def main():
    """
    Main entry point
    
    Handles different modes:
    - Command line with CSV file
    - Interactive mode
    - Quick demo
    - Help
    """
    
    # Print welcome banner
    print("\n" + "="*70)
    print(" "*15 + "STOCK PORTFOLIO PERFORMANCE ANALYZER")
    print(" "*25 + "Version 1.0")
    print("="*70)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        # Help
        if arg in ['--help', '-h', 'help']:
            print_help()
            return
        
        # Demo mode
        elif arg in ['--demo', '-d', 'demo']:
            quick_demo()
            return
        
        # CSV file path
        else:
            csv_path = sys.argv[1]
            print(f"\n📁 Loading portfolio from: {csv_path}")
            
            portfolio = load_portfolio_from_csv(csv_path)
            
            if portfolio:
                # Ask for options
                gen_pdf = input("\n👉 Generate PDF report? (y/n, default: y): ").strip().lower()
                generate_pdf = gen_pdf != 'n'
                
                run_full_analysis(portfolio, generate_pdf=generate_pdf)
            else:
                print("\n❌ Could not load portfolio. Use --help for usage information.")
                return
    
    else:
        # No arguments: run interactive mode
        interactive_mode()
    
    print("💡 Tips:")
    print("  - Save your portfolio in CSV format for easy reuse")
    print("  - Check stock_portfolio_performance_analyzer/output/reports/ for your PDF report")
    print("  - Charts are saved in stock_portfolio_performance_analyzer/output/charts/")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ An error occurred: {str(e)}")
        print("\nFor help, run: python main.py --help")
        sys.exit(1)