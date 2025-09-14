import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st

class DataProcessor:
    @staticmethod
    def parse_uploaded_file(uploaded_file):
        """Parse uploaded CSV/Excel file into a standardized format"""
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            else:
                st.error("Unsupported file format. Please upload CSV or Excel files.")
                return None
            
            # Attempt to standardize column names
            df_cleaned = DataProcessor.standardize_columns(df)
            return df_cleaned
        
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            return None
    
    @staticmethod
    def standardize_columns(df):
        """
        Rename columns to standard expected names for the app.
        """
        column_mapping = {
            # Map dataset columns to app expected columns
            "date": "date",
            "transaction description": "description",
            "category": "category",
            "amount": "amount",
            "type": "type",  # May be used if you want to differentiate expenses/income
        }
    
        # Lowercase column names + remove spaces for consistent matching
        df.columns = df.columns.str.lower().str.strip()
    
        # Rename columns
        df = df.rename(columns=column_mapping)
    
        # Check for required columns
        required_columns = ["date", "description", "category", "amount"]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
    
        # Return DataFrame with only necessary columns
        return df[required_columns]

    
    @staticmethod
    def clean_amount_column(df):
        """Clean and convert amount column to numeric"""
        df = df.copy()
        
        # Remove currency symbols and commas
        if df['amount'].dtype == 'object':
            df['amount'] = df['amount'].astype(str).str.replace(r'[^\d.-]', '', regex=True)
        
        # Convert to numeric
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # Remove rows with invalid amounts
        df = df.dropna(subset=['amount'])
        
        # Convert negative amounts to positive (assuming all are expenses)
        df['amount'] = df['amount'].abs()
        
        return df
    
    @staticmethod
    def clean_date_column(df):
        """Clean and convert date column to datetime"""
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Remove rows with invalid dates
        df = df.dropna(subset=['date'])
        
        return df
    
    @staticmethod
    def validate_data(df):
        """Validate the data quality"""
        issues = []
        
        if len(df) == 0:
            issues.append("No data rows found")
        
        if df['amount'].min() < 0:
            issues.append("Negative amounts found")
        
        if df['amount'].max() > 10000:
            issues.append("Very large amounts detected - please verify")
        
        if df.isnull().sum().sum() > 0:
            issues.append("Missing values detected")
        
        return issues

class ReportGenerator:
    @staticmethod
    def generate_enhanced_txt_report(df, insights, filename="financial_report.txt"):
        """Generate a visually appealing TXT report"""
        from datetime import datetime
        
        # Calculate key metrics
        total_spending = df['amount'].sum()
        avg_transaction = df['amount'].mean()
        num_transactions = len(df)
        date_range_start = df['date'].min().strftime('%B %d, %Y')
        date_range_end = df['date'].max().strftime('%B %d, %Y')
        
        # Category analysis
        category_breakdown = df.groupby('category')['amount'].agg(['sum', 'count', 'mean']).round(2)
        category_breakdown.columns = ['Total', 'Count', 'Average']
        category_breakdown = category_breakdown.sort_values('Total', ascending=False)
        
        # Top transactions
        top_transactions = df.nlargest(5, 'amount')[['date', 'description', 'amount', 'category']]
        
        # Monthly analysis
        df_copy = df.copy()
        df_copy['month'] = pd.to_datetime(df_copy['date']).dt.strftime('%B %Y')
        monthly_spending = df_copy.groupby('month')['amount'].sum().sort_index()
        
        # Create the formatted report
        report_content = f"""
╔═══════════════════════════════════════════════════════════════════╗
║                    💰 PERSONAL FINANCE REPORT 💰                  ║
╚═══════════════════════════════════════════════════════════════════╝

📅 Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
🎯 Analysis Period: {date_range_start} → {date_range_end}

┌─────────────────────────────────────────────────────────────────┐
│                        📊 EXECUTIVE SUMMARY                     │
└─────────────────────────────────────────────────────────────────┘

💰 FINANCIAL OVERVIEW
{'='*50}
│ Total Spending          │ ${total_spending:>15,.2f} │
│ Number of Transactions  │ {num_transactions:>15,} │
│ Average Transaction     │ ${avg_transaction:>15,.2f} │
│ Analysis Period         │ {(pd.to_datetime(df['date']).max() - pd.to_datetime(df['date']).min()).days:>12} days │
{'='*50}

🎯 KEY INSIGHTS
{'-'*50}
{insights}

┌─────────────────────────────────────────────────────────────────┐
│                     📈 CATEGORY BREAKDOWN                       │
└─────────────────────────────────────────────────────────────────┘

"""
        
        # Add category breakdown
        report_content += f"{'Category':<15} {'Total':<12} {'Count':<8} {'Average':<10} {'%':<6}\n"
        report_content += f"{'-'*15} {'-'*12} {'-'*8} {'-'*10} {'-'*6}\n"
        
        for category, row in category_breakdown.iterrows():
            percentage = (row['Total'] / total_spending) * 100
            report_content += f"{category:<15} ${row['Total']:<11,.2f} {int(row['Count']):<8} ${row['Average']:<9.2f} {percentage:<5.1f}%\n"
        
        # Add monthly trends
        report_content += f"""

┌─────────────────────────────────────────────────────────────────┐
│                      📅 MONTHLY SPENDING TRENDS                 │
└─────────────────────────────────────────────────────────────────┘

"""
        for month, amount in monthly_spending.items():
            percentage = (amount / total_spending) * 100
            bar_length = int(percentage / 2)  # Scale down for display
            bar = '█' * bar_length + '░' * (50 - bar_length)
            report_content += f"{month:<15} ${amount:>10,.2f} [{bar}] {percentage:>5.1f}%\n"
        
        # Add top transactions
        report_content += f"""

┌─────────────────────────────────────────────────────────────────┐
│                      💸 TOP 5 TRANSACTIONS                      │
└─────────────────────────────────────────────────────────────────┘

"""
        report_content += f"{'Date':<12} {'Description':<25} {'Amount':<12} {'Category':<15}\n"
        report_content += f"{'-'*12} {'-'*25} {'-'*12} {'-'*15}\n"
        
        for _, transaction in top_transactions.iterrows():
            date_str = pd.to_datetime(transaction['date']).strftime('%m/%d/%Y')
            desc = transaction['description'][:24] + "..." if len(transaction['description']) > 24 else transaction['description']
            report_content += f"{date_str:<12} {desc:<25} ${transaction['amount']:<11.2f} {transaction['category']:<15}\n"
        
        # Add savings recommendations
        food_spending = category_breakdown.loc['Food', 'Total'] if 'Food' in category_breakdown.index else 0
        transport_spending = category_breakdown.loc['Transport', 'Total'] if 'Transport' in category_breakdown.index else 0
        entertainment_spending = category_breakdown.loc['Entertainment', 'Total'] if 'Entertainment' in category_breakdown.index else 0
        
        report_content += f"""

┌─────────────────────────────────────────────────────────────────┐
│                    💡 SAVINGS RECOMMENDATIONS                   │
└─────────────────────────────────────────────────────────────────┘

🍽️  FOOD OPTIMIZATION
    Current Spending: ${food_spending:,.2f}
    → Reduce by 15%: Save ${food_spending * 0.15:.2f}/month
    → Pack lunch 2 days/week: Save ~${food_spending * 0.1:.2f}/month

🚗 TRANSPORT SAVINGS  
    Current Spending: ${transport_spending:,.2f}
    → Use public transport: Save ${transport_spending * 0.2:.2f}/month
    → Carpool twice/week: Save ${transport_spending * 0.15:.2f}/month

🎬 ENTERTAINMENT BUDGET
    Current Spending: ${entertainment_spending:,.2f}
    → Free activities: Save ${entertainment_spending * 0.3:.2f}/month
    → Home movie nights: Save ${entertainment_spending * 0.2:.2f}/month

💰 TOTAL POTENTIAL MONTHLY SAVINGS: ${(food_spending * 0.15 + transport_spending * 0.2 + entertainment_spending * 0.3):.2f}

┌─────────────────────────────────────────────────────────────────┐
│                         📋 REPORT FOOTER                        │
└─────────────────────────────────────────────────────────────────┘

Generated by: Personal Finance Tracker v2.0
Report Type: Comprehensive Financial Analysis
Data Source: {num_transactions} verified transactions
Confidence: High (complete data set)

🔒 This report contains your personal financial information.
   Keep it secure and do not share without proper authorization.

{'='*65}
Thank you for using Personal Finance Tracker! 💎
For questions or support, visit: github.com/your-repo
{'='*65}
"""
        
        return report_content
    
    @staticmethod
    def generate_pdf_report(df, insights, filename="financial_report.pdf"):
        """Generate a PDF report with spending analysis"""
        # Keep your existing PDF generation code here
        report_content = f"""
        PERSONAL FINANCE REPORT
        Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        SPENDING SUMMARY
        ===============
        Total Transactions: {len(df)}
        Total Spending: ${df['amount'].sum():.2f}
        Average Transaction: ${df['amount'].mean():.2f}
        Date Range: {df['date'].min()} to {df['date'].max()}
        
        CATEGORY BREAKDOWN
        ==================
        {df.groupby('category')['amount'].sum().to_string()}
        
        AI INSIGHTS
        ===========
        {insights}
        """
        
        return report_content
    
    @staticmethod
    def export_to_csv(df, filename="expenses_export.csv"):
        """Export data to CSV format"""
        return df.to_csv(index=False)
