import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from database import DatabaseManager
from categorizer import ExpenseCategorizer
from visualizer import FinanceVisualizer
from insights import InsightGenerator
from utils import DataProcessor, ReportGenerator

# Page configuration
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-container {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

if 'categorizer' not in st.session_state:
    st.session_state.categorizer = ExpenseCategorizer()

if 'visualizer' not in st.session_state:
    st.session_state.visualizer = FinanceVisualizer()

if 'insight_generator' not in st.session_state:
    st.session_state.insight_generator = InsightGenerator()

# Sidebar navigation
st.sidebar.title("🏦 Finance Tracker")
page = st.sidebar.radio("Navigate to:", [
    "Dashboard", 
    "Add Transaction", 
    "Upload Data", 
    "AI Insights", 
    "Reports"
])

# Main header
st.markdown('<h1 class="main-header">💰 Personal Finance Tracker</h1>', unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    return st.session_state.db_manager.get_all_transactions()

# Dashboard Page
if page == "Dashboard":
    st.header("📊 Financial Dashboard")
    
    # Load transaction data
    df = load_data()
    
    if len(df) > 0:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_spending = df['amount'].sum()
        avg_transaction = df['amount'].mean()
        num_transactions = len(df)
        top_category = df.groupby('category')['amount'].sum().idxmax()
        
        with col1:
            st.metric("Total Spending", f"${total_spending:,.2f}")
        with col2:
            st.metric("Avg Transaction", f"${avg_transaction:.2f}")
        with col3:
            st.metric("Total Transactions", num_transactions)
        with col4:
            st.metric("Top Category", top_category)
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Spending by category pie chart
            fig_pie = st.session_state.visualizer.spending_by_category_pie(df)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Spending over time
            fig_line = st.session_state.visualizer.spending_over_time(df)
            st.plotly_chart(fig_line, use_container_width=True)
        
        # Monthly comparison
        fig_monthly = st.session_state.visualizer.monthly_category_comparison(df)
        st.plotly_chart(fig_monthly, use_container_width=True)
        
        # Recent transactions table
        st.subheader("Recent Transactions")
        recent_transactions = df.head(10)[['date', 'description', 'amount', 'category']]
        st.dataframe(recent_transactions, use_container_width=True)
        
    else:
        st.info("No transaction data available. Please add transactions or upload data.")

# Add Transaction Page
elif page == "Add Transaction":
    st.header("➕ Add New Transaction")
    
    with st.form("add_transaction"):
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Date", datetime.now())
            description = st.text_input("Description", placeholder="e.g., Lunch at restaurant")
            amount = st.number_input("Amount ($)", min_value=0.01, value=10.0, step=0.01)
        
        with col2:
            category = st.selectbox("Category", st.session_state.categorizer.categories)
            account = st.text_input("Account", value="default")
            
            # Auto-categorization option
            if st.checkbox("Auto-categorize using AI"):
                if description:
                    suggested_category = st.session_state.categorizer.categorize_transaction(
                        description, amount, method='openai'
                    )
                    st.info(f"Suggested category: {suggested_category}")
        
        submitted = st.form_submit_button("Add Transaction")
        
        if submitted:
            try:
                # Add to database
                transaction = st.session_state.db_manager.add_transaction(
                    date=datetime.combine(date, datetime.min.time()),
                    description=description,
                    amount=amount,
                    category=category,
                    account=account
                )
                st.success(f"Transaction added successfully! ID: {transaction.id}")
                
                # Clear cache to refresh data
                st.cache_data.clear()
                
            except Exception as e:
                st.error(f"Error adding transaction: {str(e)}")

# Upload Data Page
elif page == "Upload Data":
    st.header("📤 Upload Transaction Data")
    
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload your bank statement or transaction data"
    )
    
    if uploaded_file is not None:
        # Parse uploaded file
        df = DataProcessor.parse_uploaded_file(uploaded_file)
        
        if df is not None:
            st.success(f"File uploaded successfully! Found {len(df)} transactions.")
            
            # Show preview
            st.subheader("Data Preview")
            st.dataframe(df.head())
            
            # Clean data
            df = DataProcessor.clean_amount_column(df)
            df = DataProcessor.clean_date_column(df)
            
            # Validate data
            issues = DataProcessor.validate_data(df)
            if issues:
                st.warning("Data quality issues found:")
                for issue in issues:
                    st.write(f"- {issue}")
            
            # Categorization options
            st.subheader("Categorization Options")
            categorization_method = st.selectbox(
                "Choose categorization method:",
                ["Rule-based", "OpenAI API", "Machine Learning"]
            )
            
            if st.button("Process and Import Data"):
                with st.spinner("Processing transactions..."):
                    # Categorize transactions
                    method_mapping = {
                        "Rule-based": "rule",
                        "OpenAI API": "openai",
                        "Machine Learning": "ml"
                    }
                    
                    df_categorized = st.session_state.categorizer.batch_categorize(
                        df, method=method_mapping[categorization_method]
                    )
                    
                    # Import to database
                    try:
                        st.session_state.db_manager.bulk_insert_from_dataframe(df_categorized)
                        st.success(f"Successfully imported {len(df_categorized)} transactions!")
                        
                        # Show categorization results
                        category_counts = df_categorized['category'].value_counts()
                        st.bar_chart(category_counts)
                        
                        # Clear cache
                        st.cache_data.clear()
                        
                    except Exception as e:
                        st.error(f"Error importing data: {str(e)}")

# AI Insights Page
# AI Insights Page
# AI Insights Page
elif page == "AI Insights":
    st.header("🧠 AI-Powered Financial Insights")
    
    df = load_data()
    
    if len(df) > 0:
        st.success(f"✅ Found {len(df)} transactions")
        
        # Convert dates
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        
        # Simple analysis
        st.subheader("💡 Spending Analysis")
        
        total_spending = df['amount'].sum()
        avg_transaction = df['amount'].mean()
        num_transactions = len(df)
        
        # Display basic stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Spending", f"${total_spending:,.2f}")
        with col2:
            st.metric("Average Transaction", f"${avg_transaction:.2f}")
        with col3:
            st.metric("Total Transactions", num_transactions)
        
        # Category analysis
        if 'category' in df.columns:
            st.subheader("📊 Category Breakdown")
            category_totals = df.groupby('category')['amount'].sum().sort_values(ascending=False)
            
            # Show top category
            if len(category_totals) > 0:
                top_category = category_totals.index[0]
                top_amount = category_totals.iloc[0]
                percentage = (top_amount / total_spending) * 100
                
                st.info(f"🏆 **Top Category**: {top_category} - ${top_amount:,.2f} ({percentage:.1f}%)")
            
            # Show all categories
            for category, amount in category_totals.items():
                percentage = (amount / total_spending) * 100
                st.write(f"• **{category}**: ${amount:,.2f} ({percentage:.1f}%)")
        
        # Most frequent transaction
        if 'description' in df.columns:
            st.subheader("🔄 Most Frequent")
            frequent = df['description'].value_counts().head(3)
            for desc, count in frequent.items():
                st.write(f"• {desc}: {count} times")
        
    else:
        st.warning("📊 No transaction data found!")
        st.info("Please go to 'Add Transaction' or 'Upload Data' to add some transactions first.")


# Reports Page
# Reports Page
elif page == "Reports":
    st.header("📋 Financial Reports")
    
    df = load_data()
    
    if len(df) > 0:
        # Convert dates properly
        try:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
            
            if len(df) == 0:
                st.error("No valid dates found in the data.")
                st.stop()
                
        except Exception as e:
            st.error(f"Error processing dates: {str(e)}")
            st.stop()
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=df['date'].min().date())
        with col2:
            end_date = st.date_input("End Date", value=df['date'].max().date())
        
        # Filter data by date range
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date)
        
        mask = (df['date'] >= start_datetime) & (df['date'] <= end_datetime)
        filtered_df = df.loc[mask]
        
        if len(filtered_df) > 0:
            # Summary statistics
            st.subheader("📊 Summary Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Spending", f"${filtered_df['amount'].sum():,.2f}")
            with col2:
                st.metric("Number of Transactions", len(filtered_df))
            with col3:
                days_diff = (end_date - start_date).days
                daily_avg = filtered_df['amount'].sum() / max(days_diff, 1)
                st.metric("Daily Average", f"${daily_avg:.2f}")
            
            # Category breakdown
            st.subheader("📈 Category Breakdown")
            category_df = filtered_df.groupby('category').agg({
                'amount': ['sum', 'count', 'mean']
            }).round(2)
            category_df.columns = ['Total', 'Count', 'Average']
            st.dataframe(category_df, use_container_width=True)
            
            # Export options
            st.subheader("📤 Export Options")
            
            # Generate insights for reports
            insights = st.session_state.insight_generator.generate_spending_insights(filtered_df)
            
            # Create two columns for export buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Export to CSV", use_container_width=True):
                    csv = ReportGenerator.export_to_csv(filtered_df)
                    st.download_button(
                        label="💾 Download CSV File",
                        data=csv,
                        file_name=f"expenses_{start_date}_{end_date}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col2:
                if st.button("📋 Generate PDF Report", use_container_width=True):
                    report = ReportGenerator.generate_pdf_report(filtered_df, insights)
                    st.download_button(
                        label="📑 Download PDF Report",
                        data=report,
                        file_name=f"financial_report_{start_date}_{end_date}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            
            with col3:
                if st.button("📝 Generate TXT Report", use_container_width=True):
                    enhanced_report = ReportGenerator.generate_enhanced_txt_report(filtered_df, insights)
                    st.download_button(
                        label="📄 Download TXT Report",
                        data=enhanced_report,
                        file_name=f"enhanced_report_{start_date}_{end_date}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            
            # Preview section
            st.subheader("👁️ Report Preview")
            
            # Tabs for different previews
            tab1, tab2, tab3 = st.tabs(["📊 Data Preview", "📝 TXT Report Preview", "📋 Insights"])
            
            with tab1:
                st.dataframe(filtered_df.head(10), use_container_width=True)
            
            with tab2:
                preview_report = ReportGenerator.generate_enhanced_txt_report(filtered_df, insights)
                st.text_area("Report Preview", preview_report[:2000] + "...\n\n[Full report available in download]", height=400)
            
            with tab3:
                st.markdown(insights)
                
        else:
            st.warning("No data available for the selected date range.")
    else:
        st.info("No transaction data available for reporting.")


# In the main app, add this to train the ML model
if st.sidebar.button("Train ML Model"):
    df = load_data()
    if len(df) > 50:  # Need sufficient data
        success = st.session_state.categorizer.train_ml_model(df)
        if success:
            st.sidebar.success("ML model trained successfully!")
        else:
            st.sidebar.error("Insufficient data for ML training")


# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Built with ❤️ using Streamlit")
