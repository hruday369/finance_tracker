import openai
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class InsightGenerator:
    def __init__(self):
        self.openai_client = None
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.openai_client = openai.OpenAI(api_key=openai_key)
    
    def generate_spending_insights(self, df):
        """Generate AI-powered insights about spending patterns"""
        if not self.openai_client:
            return self.generate_basic_insights(df)
        
        try:
            # Prepare spending summary for AI
            summary = self.prepare_spending_summary(df)
            
            prompt = f"""
            Analyze this financial data and provide 3-4 key insights about spending patterns:
            
            {summary}
            
            Please provide insights in a conversational tone, focusing on:
            1. Spending patterns and trends
            2. Category-wise analysis
            3. Actionable recommendations for saving money
            4. Any concerning spending habits
            
            Format the response as bullet points.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial advisor providing insights on personal spending."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"OpenAI insights error: {e}")
            return self.generate_basic_insights(df)
    
    def prepare_spending_summary(self, df):
        """Prepare a summary of spending data for AI analysis"""
        total_spending = df['amount'].sum()
        category_spending = df.groupby('category')['amount'].sum().to_dict()
        avg_daily = df['amount'].sum() / len(df['date'].unique()) if len(df) > 0 else 0
        
        # Recent vs older spending comparison
        df['date'] = pd.to_datetime(df['date'])
        cutoff_date = df['date'].max() - timedelta(days=30)
        recent_spending = df[df['date'] > cutoff_date]['amount'].sum()
        older_spending = df[df['date'] <= cutoff_date]['amount'].sum()
        
        summary = f"""
        Total Spending: ${total_spending:.2f}
        Average Daily Spending: ${avg_daily:.2f}
        Recent 30-day Spending: ${recent_spending:.2f}
        Older Spending: ${older_spending:.2f}
        
        Category Breakdown:
        {chr(10).join([f"- {cat}: ${amount:.2f}" for cat, amount in category_spending.items()])}
        """
        
        return summary
    
    def generate_basic_insights(self, df):
        """Generate simple, clean insights"""
        if len(df) == 0:
            return "No transaction data available for analysis."
        
        total = df['amount'].sum()
        avg_transaction = df['amount'].mean()
        num_transactions = len(df)
        
        # Get top category
        top_category = df.groupby('category')['amount'].sum().idxmax()
        top_amount = df.groupby('category')['amount'].sum().max()
        
        # Get most frequent transaction
        most_frequent = df['description'].value_counts().index[0]
        frequency = df['description'].value_counts().iloc[0]
        
        # Calculate food savings if applicable
        food_spending = df[df['category'] == 'Food']['amount'].sum()
        food_savings = food_spending * 0.1 if food_spending > 0 else 0
        
        # Format the insights
        insights_text = f"""
    **💰 SPENDING SUMMARY**
    • Total spent: ${total:,.2f} across {num_transactions} transactions
    • Average per transaction: ${avg_transaction:.2f}
    
    **📊 TOP INSIGHTS**
    • Your highest spending category is **{top_category}** with ${top_amount:,.2f}
    • Most frequent transaction: **{most_frequent}** (appears {frequency} times)
    
    **💡 SAVINGS OPPORTUNITY**
    • Reduce food expenses by 10% to save ${food_savings:.2f} per month
    • Current food spending: ${food_spending:,.2f}
        """
        
        return insights_text
    
    
    
    def generate_savings_suggestions(self, df):
        """Generate specific savings suggestions"""
        suggestions = []
        
        category_totals = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        for category, amount in category_totals.head(3).items():
            if amount > 100:  # Only suggest for significant spending
                reduction = amount * 0.15  # 15% reduction
                suggestions.append({
                    'category': category,
                    'current_spending': amount,
                    'suggested_reduction': reduction,
                    'percentage': 15
                })
        
        return suggestions
    
    def detect_spending_anomalies(self, df):
        """Detect unusual spending patterns"""
        df['date'] = pd.to_datetime(df['date'])
        
        # Calculate spending statistics
        mean_spending = df['amount'].mean()
        std_spending = df['amount'].std()
        threshold = mean_spending + (2 * std_spending)
        
        # Find anomalies
        anomalies = df[df['amount'] > threshold]
        
        return anomalies[['date', 'description', 'amount', 'category']]
# Add to insights.py
def detect_recurring_transactions(self, df):
    """Detect potential recurring transactions"""
    recurring = df.groupby(['description', 'amount']).size()
    return recurring[recurring > 2]  # Transactions that appear 3+ times
