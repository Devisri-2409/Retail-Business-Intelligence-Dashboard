import random
from datetime import date, timedelta
from decimal import Decimal

# Set seed for reproducible generation
random.seed(42)

# 1. PRODUCTS (34 products across 4 categories)
PRODUCTS = [
    # Electronics (10)
    ("Wireless Ergonomic Mouse", "Electronics", Decimal("1499.00"), 45),
    ("Mechanical Gaming Keyboard", "Electronics", Decimal("4299.00"), 25),
    ("USB-C Dual Display Dock", "Electronics", Decimal("5999.00"), 12),
    ("Noise-Cancelling Headphones", "Electronics", Decimal("8999.00"), 18),
    ("27-inch 4K UHD Monitor", "Electronics", Decimal("24999.00"), 8),     # Low stock
    ("1080p Streaming Webcam", "Electronics", Decimal("3499.00"), 30),
    ("Portable Bluetooth Speaker", "Electronics", Decimal("2799.00"), 0),   # Out of stock
    ("1TB Ultra Portable SSD", "Electronics", Decimal("7499.00"), 15),
    ("Fitness Smartwatch Series 3", "Electronics", Decimal("6499.00"), 5),  # Low stock
    ("10-inch Productivity Tablet", "Electronics", Decimal("19999.00"), 0), # Out of stock

    # Furniture (8)
    ("Ergonomic Mesh Office Chair", "Furniture", Decimal("12999.00"), 14),
    ("Motorized Standing Desk 140cm", "Furniture", Decimal("28999.00"), 6), # Low stock
    ("5-Tier Wooden Bookshelf", "Furniture", Decimal("6499.00"), 20),
    ("3-Drawer Steel Filing Cabinet", "Furniture", Decimal("4999.00"), 9),  # Low stock
    ("Solid Wood Dual Monitor Stand", "Furniture", Decimal("2199.00"), 35),
    ("Executive Leather Chair", "Furniture", Decimal("16499.00"), 0),       # Out of stock
    ("Dimmable LED Desk Lamp", "Furniture", Decimal("1899.00"), 40),
    ("Under-Desk Ergonomic Footrest", "Furniture", Decimal("1299.00"), 50),

    # Accessories (8)
    ("Water-Resistant Laptop Sleeve 15in", "Accessories", Decimal("899.00"), 60),
    ("Cable Management Organizer Box", "Accessories", Decimal("599.00"), 75),
    ("Extended Desk Mat XXL", "Accessories", Decimal("799.00"), 4),         # Low stock
    ("Memory Foam Wrist Rest Set", "Accessories", Decimal("499.00"), 80),
    ("Adjustable Aluminum Laptop Stand", "Accessories", Decimal("1699.00"), 22),
    ("6-Outlet Surge Protector 2m", "Accessories", Decimal("1199.00"), 30),
    ("Anti-Theft Commuter Backpack", "Accessories", Decimal("2999.00"), 16),
    ("Braided USB-C Fast Charging Cable 2m", "Accessories", Decimal("399.00"), 110),

    # Stationery (8)
    ("Hardcover Executive Notebook A5", "Stationery", Decimal("349.00"), 120),
    ("Fine Gel Pen Set 10-Pack", "Stationery", Decimal("249.00"), 95),
    ("Color Pastel Sticky Notes Set", "Stationery", Decimal("149.00"), 150),
    ("Rotary Mesh Desk Organizer", "Stationery", Decimal("449.00"), 35),
    ("Expanding Document File Folder", "Stationery", Decimal("299.00"), 3), # Low stock
    ("Permanent Markers Assorted 8-Pack", "Stationery", Decimal("199.00"), 70),
    ("Heavy Duty Metal Stapler", "Stationery", Decimal("399.00"), 0),       # Out of stock
    ("Metal Ballpoint Luxury Pen", "Stationery", Decimal("899.00"), 28),
]

# 2. CUSTOMERS (60 realistic customers with varied ratings)
CUSTOMER_NAMES = [
    "Aarav Sharma", "Priya Patel", "Rahul Verma", "Ananya Iyer", "Vikram Singh",
    "Sneha Rao", "Rohan Gupta", "Neha Kulkarni", "Arjun Reddy", "Pooja Nair",
    "Aditya Joshi", "Kavya Menon", "Siddharth Deshmukh", "Meera Pillai", "Karan Malhotra",
    "Divya Sundaram", "Nikhil Chopra", "Ritu Bhatia", "Amit Saxena", "Tanvi Agarwal",
    "Manish Tiwari", "Swati Nambiar", "Varun Kapoor", "Shreya Sen", "Gaurav Mehta",
    "Preeti Hegde", "Suresh Kumar", "Deepika Varma", "Rajesh Pandey", "Sunita Biswas",
    "Kunal Chatterjee", "Anjali Roy", "Harish Natarajan", "Bhavna Jain", "Alok Bhatt",
    "Rupal Tripathi", "Tarun Kaushik", "Nandini Ghosh", "Deepak Pillai", "Isha Mukherjee",
    "Vivek Chauhan", "Jyoti Shukla", "Mohit Singhania", "Rekha Das", "Sanjay Prabhu",
    "Geeta Pillai", "Abhishek Yadav", "Monika Sethi", "Ashok Rajput", "Prachi Bansal",
    "Devendra Nayak", "Pallavi Mittal", "Chirag Thakkar", "Seema Somani", "Manoj Goswami",
    "Komal Parekh", "Satish Acharya", "Namrata Shenoy", "Hemant Khandelwal", "Shruti Barua"
]

# Generate ratings with natural distribution (mostly 4.0 - 5.0, some 3.0, few 2.0-2.5)
RATINGS = [
    5.0, 4.5, 4.0, 4.8, 3.5, 5.0, 4.2, 4.6, 3.8, 4.9,
    4.0, 5.0, 3.2, 4.7, 4.1, 4.5, 3.9, 5.0, 2.5, 4.3,
    4.8, 3.7, 4.4, 5.0, 4.2, 3.0, 4.6, 4.9, 4.0, 3.6,
    5.0, 4.7, 4.3, 3.8, 4.5, 4.1, 5.0, 2.8, 4.4, 4.9,
    3.5, 4.6, 4.2, 5.0, 3.9, 4.8, 4.0, 4.5, 3.4, 4.7,
    5.0, 4.3, 4.1, 4.9, 3.6, 4.4, 5.0, 4.2, 3.8, 4.7
]

CUSTOMERS = list(zip(CUSTOMER_NAMES, RATINGS))

# 3. SALES GENERATION (650 sales across 2024)
start_date = date(2024, 1, 1)
end_date = date(2024, 12, 31)
date_range_days = (end_date - start_date).days

sales_records = []
NUM_SALES = 650

for sale_id in range(1, NUM_SALES + 1):
    # Distribute sales across all 365 days of 2024
    day_offset = random.randint(0, date_range_days)
    sale_date = start_date + timedelta(days=day_offset)
    
    # Pick a random customer (1 to 60)
    customer_id = random.randint(1, len(CUSTOMERS))
    
    # Pick a random product (1 to 34)
    product_idx = random.randint(0, len(PRODUCTS) - 1)
    product_id = product_idx + 1
    unit_price = PRODUCTS[product_idx][2]
    
    # Realistic quantity (most purchases 1-3, stationery up to 8)
    category = PRODUCTS[product_idx][1]
    if category == "Stationery":
        quantity = random.choices([1, 2, 3, 4, 5, 8], weights=[30, 25, 20, 10, 10, 5])[0]
    elif category == "Accessories":
        quantity = random.choices([1, 2, 3, 4], weights=[50, 30, 15, 5])[0]
    elif category == "Furniture":
        quantity = random.choices([1, 2], weights=[85, 15])[0]
    else:  # Electronics
        quantity = random.choices([1, 2, 3], weights=[75, 20, 5])[0]
        
    total_amount = unit_price * quantity
    sales_records.append((sale_id, sale_date.isoformat(), customer_id, product_id, quantity, total_amount))

# Sort sales by sale_date
sales_records.sort(key=lambda s: s[1])
# Reassign consecutive sale_ids chronologically
sales_records = [
    (i + 1, s[1], s[2], s[3], s[4], s[5])
    for i, s in enumerate(sales_records)
]

# Generate seed_data.sql content
sql_lines = [
    "-- ========================================================",
    "-- DEMO DATASET: retail_dashboard",
    "-- Realistic Demo Retail Data — NOT Recovered Production Data",
    "-- Target: PostgreSQL 18+",
    "-- ========================================================",
    "",
    "BEGIN;",
    "",
    "-- Clear existing data cleanly and reset sequences",
    "TRUNCATE TABLE sales, customers, products RESTART IDENTITY CASCADE;",
    "",
    "-- 1. Populate Products",
    "INSERT INTO products (product_id, product_name, category, price, stock) VALUES"
]

prod_values = []
for i, (name, cat, price, stock) in enumerate(PRODUCTS, start=1):
    safe_name = name.replace("'", "''")
    prod_values.append(f"    ({i}, '{safe_name}', '{cat}', {price}, {stock})")
sql_lines.append(",\n".join(prod_values) + ";")

sql_lines.append("\n-- Adjust products identity sequence")
sql_lines.append(f"SELECT setval('products_product_id_seq', {len(PRODUCTS)}, true);")

sql_lines.append("\n-- 2. Populate Customers")
sql_lines.append("INSERT INTO customers (customer_id, customer_name, rate) VALUES")
cust_values = []
for i, (name, rate) in enumerate(CUSTOMERS, start=1):
    safe_name = name.replace("'", "''")
    cust_values.append(f"    ({i}, '{safe_name}', {rate:.2f})")
sql_lines.append(",\n".join(cust_values) + ";")

sql_lines.append("\n-- Adjust customers identity sequence")
sql_lines.append(f"SELECT setval('customers_customer_id_seq', {len(CUSTOMERS)}, true);")

sql_lines.append("\n-- 3. Populate Sales (650 transactions across 2024)")
sql_lines.append("INSERT INTO sales (sale_id, sale_date, customer_id, product_id, quantity, total_amount) VALUES")
sale_values = []
for (s_id, s_date, c_id, p_id, qty, amt) in sales_records:
    sale_values.append(f"    ({s_id}, '{s_date}', {c_id}, {p_id}, {qty}, {amt})")
sql_lines.append(",\n".join(sale_values) + ";")

sql_lines.append("\n-- Adjust sales identity sequence")
sql_lines.append(f"SELECT setval('sales_sale_id_seq', {len(sales_records)}, true);")

sql_lines.append("\nCOMMIT;")

seed_file = "database/seed_data.sql"
with open(seed_file, "w", encoding="utf-8") as f:
    f.write("\n".join(sql_lines) + "\n")

print(f"Generated {seed_file} with:")
print(f" - {len(PRODUCTS)} products across 4 categories")
print(f" - {len(CUSTOMERS)} customers with ratings")
print(f" - {len(sales_records)} sales transactions spanning 2024-01-01 to 2024-12-31")
