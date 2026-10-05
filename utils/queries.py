# ============================================
# KPI Queries
# ============================================

TOTAL_REVENUE = """
SELECT COALESCE(SUM(total_amount), 0) AS revenue
FROM sales;
"""

TOTAL_ORDERS = """
SELECT COUNT(*) AS total_orders
FROM sales;
"""

TOTAL_PRODUCTS = """
SELECT COUNT(*) AS total_products
FROM products;
"""

TOTAL_CUSTOMERS = """
SELECT COUNT(*) AS total_customers
FROM customers;
"""

# ============================================
# Dashboard Queries
# ============================================

MONTHLY_SALES = """
SELECT
    TRIM(TO_CHAR(sale_date, 'Month')) AS Month,
    EXTRACT(MONTH FROM sale_date)::INTEGER AS MonthNo,
    COALESCE(SUM(total_amount), 0) AS Revenue
FROM sales
GROUP BY EXTRACT(MONTH FROM sale_date), TRIM(TO_CHAR(sale_date, 'Month'))
ORDER BY MonthNo;
"""

TOP_PRODUCTS = """
SELECT
    p.product_name,
    COALESCE(SUM(s.quantity), 0) AS UnitsSold
FROM sales s
JOIN products p
    ON s.product_id = p.product_id
GROUP BY p.product_name
ORDER BY UnitsSold DESC
LIMIT 10;
"""

CATEGORY_REVENUE = """
SELECT
    p.category,
    COALESCE(SUM(s.total_amount), 0) AS Revenue
FROM sales s
JOIN products p
    ON s.product_id = p.product_id
GROUP BY p.category
ORDER BY Revenue DESC;
"""

INVENTORY_STATUS = """
SELECT
    CASE
        WHEN stock = 0 THEN 'Out of Stock'
        WHEN stock <= 10 THEN 'Low Stock'
        ELSE 'In Stock'
    END AS status,
    COUNT(*) AS Total
FROM products
GROUP BY status;
"""

LOW_STOCK = """
SELECT
    product_name,
    category,
    stock
FROM products
WHERE stock <= 10
ORDER BY stock;
"""

RECENT_SALES = """
SELECT
    sale_id,
    sale_date,
    total_amount
FROM sales
ORDER BY sale_date DESC
LIMIT 10;
"""

# ============================================
# Customer Queries
# ============================================

CUSTOMER_RATING = """
SELECT
    ROUND(COALESCE(AVG(rate), 0)::NUMERIC, 2) AS avg_rating
FROM customers;
"""

TOP_CUSTOMERS = """
SELECT
    c.customer_name,
    COALESCE(SUM(s.total_amount), 0) AS TotalSpent
FROM sales s
JOIN customers c
    ON s.customer_id = c.customer_id
GROUP BY c.customer_name
ORDER BY TotalSpent DESC
LIMIT 10;
"""

# ============================================
# Inventory Queries
# ============================================

STOCK_BY_CATEGORY = """
SELECT
    category,
    COALESCE(SUM(stock), 0) AS Stock
FROM products
GROUP BY category;
"""

# ============================================
# OLAP Queries
# ============================================

YEARLY_REVENUE = """
SELECT
    EXTRACT(YEAR FROM sale_date)::INTEGER AS Year,
    COALESCE(SUM(total_amount), 0) AS Revenue
FROM sales
GROUP BY EXTRACT(YEAR FROM sale_date)
ORDER BY Year;
"""

MONTHLY_REVENUE = """
SELECT
    TRIM(TO_CHAR(sale_date, 'Month')) AS Month,
    EXTRACT(MONTH FROM sale_date)::INTEGER AS MonthNo,
    COALESCE(SUM(total_amount), 0) AS Revenue
FROM sales
GROUP BY EXTRACT(MONTH FROM sale_date), TRIM(TO_CHAR(sale_date, 'Month'))
ORDER BY MonthNo;
"""