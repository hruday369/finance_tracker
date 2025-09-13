import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st

class FinanceVisualizer:
    def __init__(self):
        self.colors = px.colors.qualitative.Set3
    
    def spending_by_category_pie(self, df):
        """Create a pie chart showing spending by category"""
        category_spending = df.groupby('category')['amount'].sum().reset_index()
        
        fig = px.pie(
            category_spending, 
            values='amount', 
            names='category',
            title='Spending by Category',
            color_discrete_sequence=self.colors
        )
        
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Amount: $%{value}<br>Percentage: %{percent}<extra></extra>'
        )
        
        return fig
    
    def spending_over_time(self, df):
        """Create a line chart showing spending over time"""
        # Ensure date column is datetime
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])  # Remove invalid dates

        daily_spending = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()

        fig = px.line(
            daily_spending, 
            x='date', 
            y='amount',
            title='Daily Spending Trend',
            labels={'amount': 'Amount ($)', 'date': 'Date'}
        )

        fig.update_traces(line_color='#1f77b4', line_width=2)
        fig.update_layout(hovermode='x unified')

        return fig

    def monthly_category_comparison(self, df):
        """Create a stacked bar chart comparing categories by month"""
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])  # Remove invalid dates
        df['month'] = df['date'].dt.to_period('M')
        
        monthly_category = df.groupby(['month', 'category'])['amount'].sum().reset_index()
        monthly_category['month'] = monthly_category['month'].astype(str)
        
        fig = px.bar(
            monthly_category, 
            x='month', 
            y='amount', 
            color='category',
            title='Monthly Spending by Category',
            labels={'amount': 'Amount ($)', 'month': 'Month'},
            color_discrete_sequence=self.colors
        )
        
        return fig

    
    def top_expenses_table(self, df, top_n=10):
        """Display top expenses in a formatted table"""
        top_expenses = df.nlargest(top_n, 'amount')[['date', 'description', 'amount', 'category']]
        return top_expenses
    
    def spending_summary_metrics(self, df):
        """Calculate and display key spending metrics"""
        total_spending = df['amount'].sum()
        avg_transaction = df['amount'].mean()
        num_transactions = len(df)
        top_category = df.groupby('category')['amount'].sum().idxmax()
        
        return {
            'total_spending': total_spending,
            'avg_transaction': avg_transaction,
            'num_transactions': num_transactions,
            'top_category': top_category
        }
    
    def category_breakdown_bar(self, df):
        """Create a horizontal bar chart for category breakdown"""
        category_spending = df.groupby('category')['amount'].sum().sort_values(ascending=True)
        
        fig = go.Figure(go.Bar(
            x=category_spending.values,
            y=category_spending.index,
            orientation='h',
            marker_color='lightblue'
        ))
        
        fig.update_layout(
            title='Spending by Category',
            xaxis_title='Amount ($)',
            yaxis_title='Category'
        )
        
        return fig
    
    def weekly_spending_pattern(self, df):
        """Show spending patterns by day of week"""
        df['date'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date'].dt.day_name()
        
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_avg = df.groupby('day_of_week')['amount'].mean().reindex(day_order)
        
        fig = px.bar(
            x=daily_avg.index,
            y=daily_avg.values,
            title='Average Spending by Day of Week',
            labels={'x': 'Day of Week', 'y': 'Average Amount ($)'}
        )
        
        return fig
