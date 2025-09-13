import sqlite3
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    description = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    account = Column(String(50), default='default')
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self, db_path="finance_tracker.db"):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def add_transaction(self, date, description, amount, category, account='default'):
        """Add a new transaction to the database"""
        transaction = Transaction(
            date=date,
            description=description,
            amount=amount,
            category=category,
            account=account
        )
        self.session.add(transaction)
        self.session.commit()
        return transaction
    
    def get_all_transactions(self):
        """Retrieve all transactions as a pandas DataFrame with proper date types"""
        query = "SELECT * FROM transactions ORDER BY date DESC"
        df = pd.read_sql_query(query, self.engine)
        
        # Convert date column to proper datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])  # Remove invalid dates
        
        return df

    
    def get_transactions_by_period(self, start_date, end_date):
        """Get transactions within a date range"""
        query = """
        SELECT * FROM transactions 
        WHERE date BETWEEN ? AND ? 
        ORDER BY date DESC
        """
        return pd.read_sql_query(query, self.engine, params=[start_date, end_date])
    
    def update_transaction_category(self, transaction_id, new_category):
        """Update the category of a specific transaction"""
        transaction = self.session.query(Transaction).filter_by(id=transaction_id).first()
        if transaction:
            transaction.category = new_category
            self.session.commit()
            return True
        return False
    
    def delete_transaction(self, transaction_id):
        """Delete a transaction by ID"""
        transaction = self.session.query(Transaction).filter_by(id=transaction_id).first()
        if transaction:
            self.session.delete(transaction)
            self.session.commit()
            return True
        return False
    
    def bulk_insert_from_dataframe(self, df):
        """Insert multiple transactions from a pandas DataFrame"""
        df.to_sql('transactions', self.engine, if_exists='append', index=False)
    
    def close(self):
        """Close the database session"""
        self.session.close()
# Add to database.py
class Budget(Base):
    __tablename__ = 'budgets'
    id = Column(Integer, primary_key=True)
    category = Column(String(50), nullable=False)
    monthly_limit = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
