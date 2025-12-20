# report_generator.py

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import os

class ReportGenerator:
    """Generate PDF reports for portfolio analysis"""
    
    def __init__(self, output_dir='output/reports'):
        """
        Args:
            output_dir (str): Directory to save reports
        """
        # Get the directory where this file is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Create output path relative to the script directory
        self.output_dir = os.path.join(script_dir, output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set up styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#A23B72'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Metric label style
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))
        
        # Metric value style
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2E86AB'),
            alignment=TA_RIGHT,
            fontName='Helvetica'
        ))
    
    def _format_currency(self, value):
        """Format number as currency"""
        return f"${value:,.2f}"
    
    def _format_percentage(self, value):
        """Format number as percentage"""
        return f"{value:.2%}"
    
    def _create_header(self):
        """Create report header"""
        elements = []
        
        # Title
        title = Paragraph("Portfolio Performance Report", self.styles['CustomTitle'])
        elements.append(title)
        
        # Date
        date_text = f"Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        date_para = Paragraph(date_text, self.styles['Normal'])
        elements.append(date_para)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_summary_section(self, analyzer):
        """Create portfolio summary section"""
        elements = []
        
        # Section header
        header = Paragraph("Portfolio Summary", self.styles['SectionHeader'])
        elements.append(header)
        
        metrics = analyzer.metrics
        
        # Create summary table
        data = [
            ['Initial Value', self._format_currency(metrics['initial_value'])],
            ['Current Value', self._format_currency(metrics['final_value'])],
            ['Total Gain/Loss', self._format_currency(metrics['final_value'] - metrics['initial_value'])],
            ['', ''],
            ['Total Return', self._format_percentage(metrics['total_return'])],
            ['Annualized Return', self._format_percentage(metrics['annualized_return'])],
            ['', ''],
            ['Time Period', f"{metrics['days']} days ({metrics['years']:.2f} years)"],
        ]
        
        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2E86AB')),
            ('LINEBELOW', (0, 2), (-1, 2), 1, colors.grey),
            ('LINEBELOW', (0, 5), (-1, 5), 1, colors.grey),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_risk_metrics_section(self, analyzer):
        """Create risk metrics section"""
        elements = []
        
        # Section header
        header = Paragraph("Risk Metrics", self.styles['SectionHeader'])
        elements.append(header)
        
        metrics = analyzer.metrics
        
        # Create risk metrics table
        data = [
            ['Volatility (Annualized)', self._format_percentage(metrics['volatility'])],
            ['Sharpe Ratio', f"{metrics['sharpe_ratio']:.2f}"],
            ['Sortino Ratio', f"{metrics['sortino_ratio']:.2f}"],
            ['Maximum Drawdown', self._format_percentage(metrics['max_drawdown'])],
            ['Win Rate', self._format_percentage(metrics['win_rate'])],
        ]
        
        if metrics['beta'] is not None:
            data.append(['Beta', f"{metrics['beta']:.2f}"])
        
        if metrics['alpha'] is not None:
            data.append(['Alpha', self._format_percentage(metrics['alpha'])])
        
        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2E86AB')),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_holdings_section(self, analyzer):
        """Create individual holdings section"""
        elements = []
        
        # Section header
        header = Paragraph("Individual Holdings Performance", self.styles['SectionHeader'])
        elements.append(header)
        
        holdings_perf = analyzer.calculate_each_holding_performance()
        
        # Create holdings table
        data = [['Ticker', 'Shares', 'Purchase Price', 'Current Price', 
                'Current Value', 'Total Return', 'Weight']]
        
        for ticker, perf in sorted(holdings_perf.items(), 
                                   key=lambda x: x[1]['current_value'], 
                                   reverse=True):
            data.append([
                ticker,
                f"{perf['shares']:.0f}",
                f"${perf['purchase_price']:.2f}",
                f"${perf['current_price']:.2f}",
                f"${perf['current_value']:.2f}",
                self._format_percentage(perf['total_return']),
                self._format_percentage(perf['weight'])
            ])
        
        table = Table(data, colWidths=[0.8*inch, 0.7*inch, 1.1*inch, 1.1*inch, 
                                       1.2*inch, 1*inch, 0.8*inch])
        
        # Style the table
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_chart(self, elements, chart_path, title, width=6*inch):
        """Add a chart to the report"""
        if os.path.exists(chart_path):
            # Section header
            header = Paragraph(title, self.styles['SectionHeader'])
            elements.append(header)
            
            # Add image
            img = Image(chart_path, width=width, height=width*0.5)
            elements.append(img)
            elements.append(Spacer(1, 20))
        else:
            print(f"Warning: Chart not found: {chart_path}")
    
    def generate_report(self, analyzer, charts_dir=None,
                       filename='portfolio_report.pdf'):
        """
        Generate complete PDF report

        Args:
            analyzer (PortfolioAnalyzer): Portfolio analyzer object
            charts_dir (str): Directory containing chart images (default: output/charts relative to this script)
            filename (str): Output filename
        """
        # If charts_dir not specified, use default relative to this script
        if charts_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            charts_dir = os.path.join(script_dir, 'output/charts')

        # Create PDF file path
        filepath = os.path.join(self.output_dir, filename)
        
        # Create document
        doc = SimpleDocTemplate(filepath, pagesize=letter,
                              topMargin=0.75*inch, bottomMargin=0.75*inch,
                              leftMargin=0.75*inch, rightMargin=0.75*inch)
        
        # Build content
        elements = []
        
        # Header
        elements.extend(self._create_header())
        
        # Portfolio Summary
        elements.extend(self._create_summary_section(analyzer))
        
        # Risk Metrics
        elements.extend(self._create_risk_metrics_section(analyzer))
        
        # Holdings
        elements.extend(self._create_holdings_section(analyzer))
        
        # Page break before charts
        elements.append(PageBreak())
        
        # Add charts
        chart_title = Paragraph("Portfolio Visualizations", self.styles['CustomTitle'])
        elements.append(chart_title)
        elements.append(Spacer(1, 20))
        
        charts = [
            ('portfolio_value.png', 'Portfolio Value Over Time'),
            ('drawdown.png', 'Portfolio Drawdown'),
            ('allocation.png', 'Portfolio Allocation'),
            ('individual_performance.png', 'Individual Holdings Performance'),
            ('risk_return.png', 'Risk-Return Profile'),
            ('returns_distribution.png', 'Returns Distribution'),
            ('rolling_returns.png', 'Rolling Returns')
        ]
        
        for chart_file, chart_title in charts:
            chart_path = os.path.join(charts_dir, chart_file)
            if os.path.exists(chart_path):
                self._add_chart(elements, chart_path, chart_title)
                if chart_file != charts[-1][0]:  # Not the last chart
                    elements.append(PageBreak())
        # Build PDF
        doc.build(elements)
        
        print(f"PDF report generated: {filepath}")
        return filepath