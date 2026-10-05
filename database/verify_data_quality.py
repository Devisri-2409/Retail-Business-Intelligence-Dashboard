import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.db import run_query

print("=== 1. ROW COUNTS ===")
prod_cnt = run_query("SELECT COUNT(*) AS c FROM products").iloc[0]["c"]
cust_cnt = run_query("SELECT COUNT(*) AS c FROM customers").iloc[0]["c"]
sale_cnt = run_query("SELECT COUNT(*) AS c FROM sales").iloc[0]["c"]
print(f"Products count: {prod_cnt}")
print(f"Customers count: {cust_cnt}")
print(f"Sales count:    {sale_cnt}")

print("\n=== 2. ORPHAN INTEGRITY CHECKS ===")
orphan_cust = run_query("""
    SELECT COUNT(*) AS c FROM sales s 
    LEFT JOIN customers c ON s.customer_id = c.customer_id 
    WHERE c.customer_id IS NULL
""").iloc[0]["c"]
orphan_prod = run_query("""
    SELECT COUNT(*) AS c FROM sales s 
    LEFT JOIN products p ON s.product_id = p.product_id 
    WHERE p.product_id IS NULL
""").iloc[0]["c"]
print(f"Orphan customer sales: {orphan_cust} (Expected: 0)")
print(f"Orphan product sales:  {orphan_prod} (Expected: 0)")

print("\n=== 3. DOMAIN CONSTRAINTS & LOGICAL INTEGRITY ===")
neg_stock = run_query("SELECT COUNT(*) AS c FROM products WHERE stock < 0").iloc[0]["c"]
neg_sales = run_query("SELECT COUNT(*) AS c FROM sales WHERE total_amount < 0").iloc[0]["c"]
inv_ratings = run_query("SELECT COUNT(*) AS c FROM customers WHERE rate < 1.0 OR rate > 5.0").iloc[0]["c"]
inv_qty = run_query("SELECT COUNT(*) AS c FROM sales WHERE quantity <= 0").iloc[0]["c"]
calc_mismatch = run_query("""
    SELECT COUNT(*) AS c FROM sales s 
    JOIN products p ON s.product_id = p.product_id 
    WHERE s.total_amount != (s.quantity * p.price)
""").iloc[0]["c"]
print(f"Negative stock products: {neg_stock} (Expected: 0)")
print(f"Negative sales amounts:  {neg_sales} (Expected: 0)")
print(f"Invalid ratings (<1 or >5): {inv_ratings} (Expected: 0)")
print(f"Invalid quantities (<=0): {inv_qty} (Expected: 0)")
print(f"Sales calculation mismatches (amount != qty * price): {calc_mismatch} (Expected: 0)")

print("\n=== 4. DATE COVERAGE & MONTHLY DISTRIBUTION ===")
date_info = run_query("""
    SELECT 
        MIN(sale_date) AS min_date,
        MAX(sale_date) AS max_date,
        COUNT(DISTINCT EXTRACT(MONTH FROM sale_date)) AS distinct_months
    FROM sales
""")
print(f"Date range: {date_info.iloc[0]['min_date']} to {date_info.iloc[0]['max_date']}")
print(f"Distinct months with sales: {date_info.iloc[0]['distinct_months']} of 12")

months_df = run_query("""
    SELECT 
        EXTRACT(MONTH FROM sale_date)::INTEGER AS month_no,
        TRIM(TO_CHAR(sale_date, 'Month')) AS month_name,
        COUNT(*) AS tx_count,
        SUM(total_amount) AS revenue
    FROM sales
    GROUP BY EXTRACT(MONTH FROM sale_date), TRIM(TO_CHAR(sale_date, 'Month'))
    ORDER BY month_no
""")
print(months_df.to_string(index=False))

print("\n=== 5. CATEGORY COVERAGE ===")
cat_df = run_query("""
    SELECT 
        p.category,
        COUNT(s.sale_id) AS sales_count,
        SUM(s.quantity) AS units_sold,
        SUM(s.total_amount) AS revenue
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY p.category
    ORDER BY revenue DESC
""")
print(cat_df.to_string(index=False))

print("\n=== 6. INVENTORY STATUS BREAKDOWN ===")
inv_status = run_query("""
    SELECT
        CASE
            WHEN stock = 0 THEN 'Out of Stock'
            WHEN stock <= 10 THEN 'Low Stock'
            ELSE 'In Stock'
        END AS status,
        COUNT(*) AS product_count
    FROM products
    GROUP BY 1
    ORDER BY product_count DESC
""")
print(inv_status.to_string(index=False))
