import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from streamlit.testing.v1 import AppTest

print("==================================================")
print("TESTING STREAMLIT PAGES VIA STREAMLIT APPTEST")
print("==================================================")

pages = [
    ("Main Dashboard (app.py)", "app.py"),
    ("1. Time Analysis", "pages/1_Time_Analysis.py"),
    ("2. Product Analysis", "pages/2_Product_Analysis.py"),
    ("3. Customer Analysis", "pages/3_Customer_Analysis.py"),
    ("4. Inventory Analysis", "pages/4_Inventory_Analysis.py"),
    ("5. OLAP Analysis", "pages/5_OLAP_Analysis.py"),
]

all_passed = True
for name, path in pages:
    try:
        print(f"\nTesting page: {name} ({path})...")
        at = AppTest.from_file(path, default_timeout=30)
        at.run()
        if at.exception:
            print(f"[FAIL] Exception on {name}:")
            for exc in at.exception:
                print(f"  {exc.value}")
            all_passed = False
        else:
            print(f"[PASS] {name} rendered with 0 exceptions!")
    except Exception as e:
        print(f"[FAIL] Error testing {name}: {e}")
        all_passed = False

if all_passed:
    print("\n==================================================")
    print("ALL 6 STREAMLIT PAGES PASSED EXECUTION WITH ZERO EXCEPTIONS!")
    print("==================================================")
else:
    print("\nSome pages failed execution.")
    sys.exit(1)
