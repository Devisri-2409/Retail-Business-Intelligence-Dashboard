# 🛒 Retail Business Intelligence Dashboard

An interactive **Retail Business Intelligence Dashboard** built using **Python, Streamlit, PostgreSQL, Plotly, Pandas, and SQLAlchemy**. It provides real-time insights into sales, products, customers, inventory, and business performance through interactive visualizations and OLAP analysis.

## ✨ Features

- 📊 Dashboard Overview with KPI Cards
- 📈 Monthly & Quarterly Sales Analysis
- 🛍️ Product & Category Analysis
- 👥 Customer Analysis
- 📦 Inventory Monitoring
- 🧩 OLAP Operations (Roll-up, Drill-down, Slice, Dice & Pivot)
- 📥 Download Sales Reports

## 🛠️ Tech Stack

- Python 3.13
- Streamlit
- PostgreSQL
- psycopg (v3)
- Plotly
- Pandas
- SQLAlchemy

## 📂 Project Structure

```text
Retail-Business-Intelligence-Dashboard/
│── app.py
│── config.py (legacy MySQL configuration preserved)
│── requirements.txt
│── README.md
│── .env.example
│
├── assets/
│   └── logo.png
├── database/
│   ├── schema.sql
│   ├── seed_data.sql
│   ├── apply_schema.py
│   ├── apply_seed.py
│   └── verify_data_quality.py
├── pages/
│   ├── 1_Time_Analysis.py
│   ├── 2_Product_Analysis.py
│   ├── 3_Customer_Analysis.py
│   ├── 4_Inventory_Analysis.py
│   └── 5_OLAP_Analysis.py
├── tests/
│   ├── test_all_queries.py
│   └── test_streamlit_pages.py
└── utils/
    ├── db.py
    └── queries.py
```

## 🚀 Installation & Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure your local PostgreSQL database URL:

```env
DATABASE_URL=postgresql+psycopg://postgres:<PASSWORD>@localhost:5432/retail_dashboard
```

### 3. Initialize Database & Demo Dataset (Optional)

```bash
python database/apply_schema.py
python database/apply_seed.py
```

### 4. Run the dashboard

```bash
streamlit run app.py
```
