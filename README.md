# 💰 Personal Finance Tracker  

The **Personal Finance Tracker** is a Python web application built with **Streamlit** that helps you manage, analyze, and optimize your personal finances. You can upload bank statements, manually add expenses, and get **AI-powered insights** to better understand your spending habits and save more effectively.  

---

## 🚀 Features  

- 📂 **Upload Data**: Import CSV/Excel bank statements or add transactions manually.  
- 🏷️ **Auto-Categorization**: Classify expenses with rule-based logic or AI/ML models.  
- 📊 **Interactive Dashboards**:  
  - Spending pie charts  
  - Trend analysis with line charts  
  - Top vendors & categories  
- 🤖 **AI Insights**: Personalized spending analysis and savings suggestions using **OpenAI API** (or Hugging Face alternatives).  
- 📑 **Reports**: Export detailed reports in **PDF** or **CSV** formats.  
- 🗄️ **Persistent Storage**: Save data using **SQLite** or **Postgres**.  
- 🎨 **Simple UI**: Intuitive, user-friendly interface powered by **Streamlit**.  

---

## 🛠️ Tech Stack  

- **Backend & Data**: Python, Pandas, SQLite/Postgres, SQLAlchemy  
- **Frontend/UI**: Streamlit  
- **AI Layer**: OpenAI API / Hugging Face models  
- **Visualization**: Plotly, Matplotlib, Seaborn  
- **Deployment**: Streamlit Community Cloud, Render, Railway  

---

## ⚙️ Installation  

1. **Clone the repository**  
   ```bash
   git clone https://github.com/yourusername/finance-tracker.git
   cd finance-tracker
   ```

2. **Create and activate a virtual environment**  
   ```bash
   python -m venv env
   # Linux/Mac
   source env/bin/activate
   # Windows
   env\Scripts\activate
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**  
   Create a `.env` file in the root directory and add:  
   ```
   OPENAI_API_KEY=your_openai_key_here
   ```

5. **Run the application**  
   ```bash
   streamlit run app.py
   ```

---

## 📖 Usage  

1. **Add Transactions**: Upload bank statements or manually input expenses.  
2. **Analyze Spending**: View dashboards with categories, trends, and top vendors.  
3. **AI Insights**: Get smart recommendations for saving more.  
4. **Export Reports**: Generate detailed **PDF** or **CSV** reports.  

---

## 🤝 Contributing  

Contributions are welcome! 🎉  
To contribute:  
- Fork the repo  
- Create a new branch (`feature/your-feature-name`)  
- Commit changes  
- Submit a pull request  

---

## 📜 License  

This project is licensed under the **MIT License** – feel free to use and modify it.  

---

## ⭐ Support  

If you find this project useful, don’t forget to **star ⭐ the repository** and share it with others!  
