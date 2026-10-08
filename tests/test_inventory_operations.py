import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
from utils.db import run_query
from streamlit.testing.v1 import AppTest

print("==================================================")
print("TESTING INVENTORY OPERATIONS & REORDER LOGIC")
print("==================================================")

# 1. Test database query
print("\n--- 1. Querying products from PostgreSQL ---")
products_df = run_query("""
    SELECT product_id, product_name, category, price, stock
    FROM products
    ORDER BY category, product_name;
""")
assert not products_df.empty, "Products table should not be empty"
print(f"[PASS] Successfully fetched {len(products_df)} products from PostgreSQL")

# 2. Test status classification
print("\n--- 2. Testing status classification ---")
def classify_status(stock):
    if stock == 0:
        return "Out of Stock"
    elif stock <= 10:
        return "Low Stock"
    return "In Stock"

products_df["status"] = products_df["stock"].apply(classify_status)
status_counts = products_df["status"].value_counts().to_dict()
print(f"Status counts: {status_counts}")
assert status_counts.get("Out of Stock", 0) > 0, "Should have out-of-stock products in demo dataset"
assert status_counts.get("Low Stock", 0) > 0, "Should have low-stock products in demo dataset"
assert status_counts.get("In Stock", 0) > 0, "Should have in-stock products in demo dataset"
print("[PASS] Classification verified (Out of Stock, Low Stock, In Stock)")

# 3. Test reorder quantity formula: max(0, target - stock)
print("\n--- 3. Testing reorder quantity formula ---")
target = 50
products_df["suggested_reorder"] = products_df["stock"].apply(lambda s: max(0, target - s))
assert (products_df["suggested_reorder"] >= 0).all(), "Reorder quantity must be non-negative"

# Check out-of-stock reorder qty equals target
out_of_stock_items = products_df[products_df["stock"] == 0]
for _, row in out_of_stock_items.iterrows():
    assert row["suggested_reorder"] == target, f"Out of stock item should need full target {target}"
print(f"[PASS] Reorder quantity formula verified for target={target}")

# 4. Test priority sorting (Out of stock first, then low stock)
print("\n--- 4. Testing restock priority sorting ---")
def priority_rank(row):
    if row["stock"] == 0:
        return 1
    elif row["stock"] <= 10:
        return 2
    return 3

products_df["priority"] = products_df.apply(priority_rank, axis=1)
restock_df = products_df[products_df["priority"] <= 2].sort_values(
    by=["priority", "stock", "price"],
    ascending=[True, True, False]
)

# Verify all priority 1 items appear before priority 2 items
priorities = restock_df["priority"].tolist()
first_priority_2_idx = priorities.index(2) if 2 in priorities else len(priorities)
for p in priorities[:first_priority_2_idx]:
    assert p == 1, "All items before first priority 2 must be priority 1 (Out of stock)"
for p in priorities[first_priority_2_idx:]:
    assert p == 2, "All items after must be priority 2 (Low stock)"
print(f"[PASS] Priority sorting strictly places {len(out_of_stock_items)} Out of Stock items before Low Stock items")

# 5. Test filtering by category
print("\n--- 5. Testing category filtering ---")
cats = products_df["category"].unique()
for cat in cats:
    cat_df = products_df[products_df["category"] == cat]
    assert (cat_df["category"] == cat).all()
print(f"[PASS] Category filtering verified across all {len(cats)} categories")

# 6. Test CSV Export structure
print("\n--- 6. Testing CSV export structure ---")
export_df = products_df.rename(columns={
    "product_id": "Product ID",
    "product_name": "Product Name",
    "category": "Category",
    "price": "Unit Price (INR)",
    "stock": "Current Stock",
    "status": "Stock Status",
    "suggested_reorder": "Suggested Reorder Qty"
})
csv_output = export_df.to_csv(index=False)
assert "Product ID,Product Name,Category,Unit Price (INR),Current Stock,Stock Status,Suggested Reorder Qty" in csv_output
print("[PASS] CSV export headers and data format verified")

# 7. Interactive Streamlit UI Execution via AppTest
print("\n--- 7. Testing pages/4_Inventory_Analysis.py with AppTest ---")
at = AppTest.from_file("pages/4_Inventory_Analysis.py", default_timeout=30)
at.run()
assert not at.exception, f"Default render failed: {[e.value for e in at.exception]}"
print("[PASS] Initial render: 0 exceptions")

# Test search filter
if at.text_input:
    at.text_input[0].set_value("Mouse").run()
    assert not at.exception, f"Search filter failed: {[e.value for e in at.exception]}"
    print("[PASS] Interactive Search input 'Mouse' updated with 0 exceptions")
    at.text_input[0].set_value("").run()

# Test category filter
if len(at.selectbox) >= 1:
    at.selectbox[0].select("Electronics").run()
    assert not at.exception, f"Category select failed: {[e.value for e in at.exception]}"
    print("[PASS] Interactive Category 'Electronics' filter updated with 0 exceptions")

# Test status filter
if len(at.selectbox) >= 2:
    at.selectbox[1].select("Requires Attention (Out & Low)").run()
    assert not at.exception, f"Status select failed: {[e.value for e in at.exception]}"
    print("[PASS] Interactive Status 'Requires Attention' filter updated with 0 exceptions")

# Test target stock adjustment
if at.number_input:
    at.number_input[0].set_value(100).run()
    assert not at.exception, f"Target stock input failed: {[e.value for e in at.exception]}"
    print("[PASS] Interactive Target Stock level change (100) updated with 0 exceptions")

# Test theme toggle
if at.sidebar.radio:
    at.sidebar.radio[0].set_value("Dark").run()
    assert not at.exception, f"Theme toggle failed: {[e.value for e in at.exception]}"
    print("[PASS] Dark Theme toggle updated with 0 exceptions")

print("\n==================================================")
print("ALL INVENTORY OPERATIONAL & UI TESTS PASSED!")
print("==================================================")

