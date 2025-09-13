import openai
import pandas as pd
import numpy as np
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

class ExpenseCategorizer:
    def __init__(self):
        self.openai_client = None
        self.ml_model = None
        self.vectorizer = None
        self.categories = [
            'Food', 'Transport', 'Entertainment', 'Shopping', 
            'Utilities', 'Healthcare', 'Education', 'Others'
        ]
        
        # Initialize OpenAI if API key is available
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.openai_client = openai.OpenAI(api_key=openai_key)
        
        # Rule-based patterns
        self.category_patterns = {
            'Food': ['restaurant', 'food', 'cafe', 'starbucks', 'mcdonald', 'pizza', 'grocery', 'supermarket'],
            'Transport': ['uber', 'taxi', 'gas', 'fuel', 'parking', 'metro', 'bus', 'train'],
            'Entertainment': ['netflix', 'spotify', 'movie', 'cinema', 'game', 'concert', 'theater'],
            'Shopping': ['amazon', 'mall', 'store', 'shop', 'purchase', 'buy', 'clothes'],
            'Utilities': ['electric', 'water', 'internet', 'phone', 'rent', 'bill'],
            'Healthcare': ['hospital', 'doctor', 'pharmacy', 'medical', 'dental', 'health'],
            'Education': ['school', 'college', 'course', 'book', 'education', 'tuition'],
        }
    
    def rule_based_categorization(self, description):
        """Categorize transaction using rule-based approach"""
        description_lower = description.lower()
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if pattern in description_lower:
                    return category
        return 'Others'
    
    def openai_categorization(self, description, amount=None):
        """Categorize transaction using OpenAI API"""
        if not self.openai_client:
            return self.rule_based_categorization(description)
        
        try:
            prompt = f"""
            Categorize this expense transaction into one of these categories:
            {', '.join(self.categories)}
            
            Transaction description: "{description}"
            {f'Amount: ${amount}' if amount else ''}
            
            Return only the category name, nothing else.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial assistant that categorizes expenses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0
            )
            
            category = response.choices[0].message.content.strip()
            return category if category in self.categories else 'Others'
        
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self.rule_based_categorization(description)
    
    def train_ml_model(self, df):
        """Train a machine learning model for categorization"""
        if len(df) < 20:  # Need sufficient data
            return False
        
        # Prepare features and labels
        X = df['description'].astype(str)
        y = df['category']
        
        # Create TF-IDF features
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        X_vectorized = self.vectorizer.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_vectorized, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.ml_model = MultinomialNB()
        self.ml_model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.ml_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"ML Model Accuracy: {accuracy:.2f}")
        
        return True
    
    def ml_categorization(self, description):
        """Categorize using trained ML model"""
        if not self.ml_model or not self.vectorizer:
            return self.rule_based_categorization(description)
        
        try:
            # Vectorize the description
            desc_vectorized = self.vectorizer.transform([description])
            
            # Predict category
            prediction = self.ml_model.predict(desc_vectorized)[0]
            return prediction
        
        except Exception as e:
            print(f"ML prediction error: {e}")
            return self.rule_based_categorization(description)
    
    def categorize_transaction(self, description, amount=None, method='rule'):
        """Main categorization function with multiple methods"""
        if method == 'openai' and self.openai_client:
            return self.openai_categorization(description, amount)
        elif method == 'ml' and self.ml_model:
            return self.ml_categorization(description)
        else:
            return self.rule_based_categorization(description)
    
    def batch_categorize(self, df, method='rule'):
        """Categorize multiple transactions at once"""
        df_copy = df.copy()
        df_copy['category'] = df_copy.apply(
            lambda row: self.categorize_transaction(
                row['description'], 
                row.get('amount'), 
                method
            ), axis=1
        )
        return df_copy
