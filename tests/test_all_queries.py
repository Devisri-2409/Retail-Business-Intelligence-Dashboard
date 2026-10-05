import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
from utils.db import run_query
import utils.queries as q

print("==================================================")
print("RUNNING AUTOMATED TEST SUITE FOR POSTGRESQL QUERIES")
print("==================================================")

errors = []

def run_test(name, func):
    global errors
    try:
        res = func()
        print(f"[PASS] {name}")
        return res
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        errors.append((name, str(e)))
        return None

# Test 1: utils/queries.py
print("\n--- 1. Testing utils/queries.py ---")
run_test("KPI: TOTAL_REVENUE", lambda: run_query(q.TOTAL_REVENUE))
run_test("KPI: TOTAL_ORDERS", lambda: run_query(q.TOTAL_ORDERS))
run_test("KPI: TOTAL_PRODUCTS", lambda: run_query(q.TOTAL_PRODUCTS))
run_test("KPI: TOTAL_CUSTOMERS", lambda: run_query(q.TOTAL_CUSTOMERS))
run_test("Dashboard: MONTHLY_SALES", lambda: run_query(q.MONTHLY_SALES))
run_test("Dashboard: TOP_PRODUCTS", lambda: run_query(q.TOP_PRODUCTS))
run_test("Dashboard: CATEGORY_REVENUE", lambda: run_query(q.CATEGORY_REVENUE))
run_test("Dashboard: INVENTORY_STATUS", lambda: run_query(q.INVENTORY_STATUS))
run_test("Dashboard: LOW_STOCK", lambda: run_query(q.LOW_STOCK))
run_test("Dashboard: RECENT_SALES", lambda: run_query(q.RECENT_SALES))
run_test("Customer: CUSTOMER_RATING (rate col)", lambda: run_query(q.CUSTOMER_RATING))
run_test("Customer: TOP_CUSTOMERS", lambda: run_query(q.TOP_CUSTOMERS))
run_test("Inventory: STOCK_BY_CATEGORY", lambda: run_query(q.STOCK_BY_CATEGORY))
run_test("OLAP: YEARLY_REVENUE", lambda: run_query(q.YEARLY_REVENUE))
run_test("OLAP: MONTHLY_REVENUE", lambda: run_query(q.MONTHLY_REVENUE))

# Test 2: app.py queries
print("\n--- 2. Testing app.py queries ---")
run_test("app.py: Monthly Sales Trend", lambda: run_query("""
    SELECT
        EXTRACT(MONTH FROM sale_date)::INTEGER AS "MonthNo",
        TRIM(TO_CHAR(sale_date, 'Month')) AS "Month",
        COALESCE(SUM(total_amount), 0) AS "Revenue"
    FROM sales
    GROUP BY EXTRACT(MONTH FROM sale_date), TRIM(TO_CHAR(sale_date, 'Month'))
    ORDER BY "MonthNo";
"""))
run_test("app.py: Quarterly Revenue", lambda: run_query("""
    SELECT
        EXTRACT(YEAR FROM sale_date)::INTEGER AS "Year",
        CONCAT('Q', EXTRACT(QUARTER FROM sale_date)::INTEGER) AS "Quarter",
        COALESCE(SUM(total_amount), 0) AS "Revenue"
    FROM sales
    GROUP BY EXTRACT(YEAR FROM sale_date), EXTRACT(QUARTER FROM sale_date)
    ORDER BY "Year", "Quarter";
"""))
run_test("app.py: Best Seller Insights", lambda: run_query("""
    SELECT p.product_name, COALESCE(SUM(s.quantity), 0) AS "UnitsSold"
    FROM sales s JOIN products p ON s.product_id = p.product_id
    GROUP BY p.product_name ORDER BY "UnitsSold" DESC LIMIT 1;
"""))
run_test("app.py: Top Category Insights", lambda: run_query("""
    SELECT p.category, COALESCE(SUM(s.total_amount), 0) AS "Revenue"
    FROM sales s JOIN products p ON s.product_id = p.product_id
    GROUP BY p.category ORDER BY "Revenue" DESC LIMIT 1;
"""))

# Test 3: pages/1_Time_Analysis.py
print("\n--- 3. Testing 1_Time_Analysis.py ---")
run_test("Time Analysis: Year View", lambda: run_query("""
    SELECT EXTRACT(YEAR FROM sale_date)::INTEGER AS "Period", COALESCE(SUM(total_amount), 0) AS "Revenue"
    FROM sales GROUP BY EXTRACT(YEAR FROM sale_date) ORDER BY "Period";
"""))
run_test("Time Analysis: Quarter View", lambda: run_query("""
    SELECT EXTRACT(QUARTER FROM sale_date)::INTEGER AS "QuarterNo",
           CONCAT('Q', EXTRACT(QUARTER FROM sale_date)::INTEGER) AS "Period",
           COALESCE(SUM(total_amount), 0) AS "Revenue"
    FROM sales GROUP BY EXTRACT(QUARTER FROM sale_date) ORDER BY "QuarterNo";
"""))
run_test("Time Analysis: Month View", lambda: run_query("""
    SELECT TRIM(TO_CHAR(sale_date, 'Month')) AS "Period",
           EXTRACT(MONTH FROM sale_date)::INTEGER AS "MonthNo",
           COALESCE(SUM(total_amount), 0) AS "Revenue"
    FROM sales GROUP BY EXTRACT(MONTH FROM sale_date), TRIM(TO_CHAR(sale_date, 'Month'))
    ORDER BY "MonthNo";
"""))

# Test 4: pages/2_Product_Analysis.py
print("\n--- 4. Testing 2_Product_Analysis.py (Parameterized) ---")
run_test("Product Analysis: Categories list", lambda: run_query("SELECT DISTINCT category FROM products ORDER BY category;"))
run_test("Product Analysis: Filtered Revenue (Electronics)", lambda: run_query("""
    SELECT p.category, COALESCE(SUM(s.total_amount), 0) AS "Revenue"
    FROM sales s JOIN products p ON s.product_id = p.product_id
    WHERE p.category = :category GROUP BY p.category;
""", params={"category": "Electronics"}))
run_test("Product Analysis: Filtered Top Products (Furniture)", lambda: run_query("""
    SELECT p.product_name, COALESCE(SUM(s.quantity), 0) AS "UnitsSold"
    FROM sales s JOIN products p ON s.product_id = p.product_id
    WHERE p.category = :category GROUP BY p.product_name ORDER BY "UnitsSold" DESC LIMIT 10;
""", params={"category": "Furniture"}))
run_test("Product Analysis: Filtered Table (Stationery)", lambda: run_query("""
    SELECT p.product_name, p.category, COALESCE(SUM(s.quantity), 0) AS "UnitsSold", COALESCE(SUM(s.total_amount), 0) AS "Revenue"
    FROM sales s JOIN products p ON s.product_id = p.product_id
    WHERE p.category = :category GROUP BY p.product_name, p.category ORDER BY "Revenue" DESC;
""", params={"category": "Stationery"}))

# Test 5: pages/3_Customer_Analysis.py
print("\n--- 5. Testing 3_Customer_Analysis.py ---")
run_test("Customer Analysis: Repeat Customers", lambda: run_query("""
    SELECT COUNT(*) AS repeat_customers
    FROM (SELECT customer_id FROM sales GROUP BY customer_id HAVING COUNT(*) > 1) t;
"""))
run_test("Customer Analysis: Rating Distribution", lambda: run_query("""
    SELECT rate, COUNT(*) AS "Total" FROM customers GROUP BY rate ORDER BY rate;
"""))
run_test("Customer Analysis: Purchase Details Table", lambda: run_query("""
    SELECT c.customer_name, COUNT(s.sale_id) AS "Orders", COALESCE(SUM(s.total_amount), 0) AS "TotalSpent",
           ROUND(COALESCE(AVG(s.total_amount), 0)::NUMERIC, 2) AS "AvgPurchase"
    FROM customers c LEFT JOIN sales s ON c.customer_id = s.customer_id
    GROUP BY c.customer_name ORDER BY "TotalSpent" DESC;
"""))

# Test 6: pages/4_Inventory_Analysis.py
print("\n--- 6. Testing 4_Inventory_Analysis.py ---")
run_test("Inventory Analysis: Status Count", lambda: run_query("""
    SELECT status, COUNT(*) AS "Total" FROM (
        SELECT CASE WHEN stock = 0 THEN 'Out of Stock' WHEN stock <= 10 THEN 'Low Stock' ELSE 'In Stock' END AS status
        FROM products
    ) AS inventory_status GROUP BY status;
"""))
run_test("Inventory Analysis: Low Stock List", lambda: run_query("""
    SELECT product_id, product_name, category, stock FROM products WHERE stock <= 10 ORDER BY stock;
"""))
run_test("Inventory Analysis: Complete Inventory", lambda: run_query("""
    SELECT product_id, product_name, category, price, stock FROM products ORDER BY category;
"""))

# Test 7: pages/5_OLAP_Analysis.py (All 5 Operations)
print("\n--- 7. Testing 5_OLAP_Analysis.py (5 OLAP Operations) ---")
# 1. Roll-up
run_test("OLAP 1 - Roll-up (Year-wise)", lambda: run_query("""
    SELECT EXTRACT(YEAR FROM sale_date)::INTEGER AS "Year", COALESCE(SUM(total_amount), 0) AS "Revenue"
    FROM sales GROUP BY EXTRACT(YEAR FROM sale_date) ORDER BY "Year";
"""))
# 2. Drill-down
run_test("OLAP 2 - Drill-down (Month-wise)", lambda: run_query("""
    SELECT TRIM(TO_CHAR(sale_date, 'Month')) AS "Month", EXTRACT(MONTH FROM sale_date)::INTEGER AS "MonthNo",
           COALESCE(SUM(total_amount), 0) AS "Revenue"
    FROM sales GROUP BY EXTRACT(MONTH FROM sale_date), TRIM(TO_CHAR(sale_date, 'Month')) ORDER BY "MonthNo";
"""))
# 3. Slice
run_test("OLAP 3 - Slice (Category = Accessories)", lambda: run_query("""
    SELECT p.product_name, COALESCE(SUM(s.total_amount), 0) AS "Revenue"
    FROM sales s JOIN products p ON s.product_id = p.product_id
    WHERE p.category = :category GROUP BY p.product_name;
""", params={"category": "Accessories"}))
# 4. Dice
run_test("OLAP 4 - Dice (Category = Electronics AND Month = March)", lambda: run_query("""
    SELECT p.category, TRIM(TO_CHAR(s.sale_date, 'Month')) AS "Month", COALESCE(SUM(s.total_amount), 0) AS "Revenue"
    FROM sales s JOIN products p ON s.product_id = p.product_id
    WHERE p.category = :category AND TRIM(TO_CHAR(s.sale_date, 'Month')) = :month
    GROUP BY p.category, EXTRACT(MONTH FROM s.sale_date), TRIM(TO_CHAR(s.sale_date, 'Month'))
    ORDER BY EXTRACT(MONTH FROM s.sale_date);
""", params={"category": "Electronics", "month": "March"}))
# 5. Pivot
def test_pivot():
    df = run_query("""
        SELECT p.category, TRIM(TO_CHAR(s.sale_date, 'Month')) AS "Month",
               EXTRACT(MONTH FROM s.sale_date)::INTEGER AS "MonthNo", s.total_amount
        FROM sales s JOIN products p ON s.product_id = p.product_id
        ORDER BY "MonthNo";
    """)
    pivot = df.pivot_table(values="total_amount", index="category", columns="Month", aggfunc="sum", fill_value=0)
    assert not pivot.empty
    return pivot
run_test("OLAP 5 - Pivot Table (Category x Month)", test_pivot)

# Test 8: CSV Export Test
print("\n--- 8. Testing CSV Generation ---")
def test_csv_gen():
    df = run_query("SELECT sale_id, sale_date, customer_id, product_id, quantity, total_amount FROM sales ORDER BY sale_date DESC LIMIT 10;")
    csv_str = df.to_csv(index=False)
    assert "sale_id,sale_date,customer_id,product_id,quantity,total_amount" in csv_str
    return True
run_test("CSV Generation Test", test_csv_gen)

print("\n==================================================")
if errors:
    print(f"FAILED: {len(errors)} error(s) encountered:")
    for name, err in errors:
        print(f" - {name}: {err}")
    sys.exit(1)
else:
    print("ALL TESTS PASSED WITH 100% SUCCESS!")
print("==================================================")
