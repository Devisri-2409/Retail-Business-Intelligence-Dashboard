import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from streamlit.testing.v1 import AppTest
from datetime import date

print("==================================================")
print("TESTING INTERACTIVE FILTER BEHAVIOR ON APP.PY")
print("==================================================")

at = AppTest.from_file("app.py", default_timeout=30)
at.run()
assert not at.exception, f"Initial run failed: {at.exception}"
print("[PASS] Initial render with defaults passed.")

# Test changing Category to 'Electronics'
try:
    # Selectbox 0: Year, Selectbox 1: Category
    at.selectbox[1].select("Electronics")
    at.run()
    assert not at.exception, f"Exception after category change: {at.exception}"
    print("[PASS] Filter category = 'Electronics' updated successfully.")
except Exception as e:
    print(f"[FAIL] Category filter test: {e}")
    sys.exit(1)

# Test changing Category to 'Furniture'
try:
    at.selectbox[1].select("Furniture")
    at.run()
    assert not at.exception, f"Exception after category change to Furniture: {at.exception}"
    print("[PASS] Filter category = 'Furniture' updated successfully.")
except Exception as e:
    print(f"[FAIL] Category filter test: {e}")
    sys.exit(1)

# Test changing Date Range (H2 2024 to test period comparison)
try:
    at.date_input[0].set_value(date(2024, 7, 1))
    at.date_input[1].set_value(date(2024, 12, 31))
    at.run()
    assert not at.exception, f"Exception after date range change: {at.exception}"
    print("[PASS] Date range filter (H2 2024) updated successfully with period comparison.")
except Exception as e:
    print(f"[FAIL] Date range filter test: {e}")
    sys.exit(1)

# Test Theme Toggle to Dark
try:
    at.sidebar.radio[0].set_value("Dark")
    at.run()
    assert not at.exception, f"Exception after theme toggle to Dark: {at.exception}"
    print("[PASS] Theme toggle to 'Dark' mode updated successfully.")
except Exception as e:
    print(f"[FAIL] Theme toggle test: {e}")
    sys.exit(1)

print("\n==================================================")
print("ALL INTERACTIVE FILTER & THEME TESTS PASSED 100%!")
print("==================================================")
