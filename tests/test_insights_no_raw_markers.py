import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from streamlit.testing.v1 import AppTest
import re

print("==================================================")
print("VERIFYING EXECUTIVE BUSINESS INSIGHTS MARKDOWN")
print("==================================================")

at = AppTest.from_file("app.py", default_timeout=30)
at.run()
assert not at.exception, f"App execution failed: {at.exception}"

# Find the markdown elements corresponding to the insights
insight_markdowns = []
for m in at.markdown:
    # Check if this markdown is one of the insights
    if "Category Leadership:" in m.value or "Top Performing SKU:" in m.value or "Inventory Alert:" in m.value or "Transaction Volume:" in m.value or "Sales Momentum:" in m.value:
        insight_markdowns.append(m.value)

print(f"Found {len(insight_markdowns)} insight markdown blocks in app.py.")
assert len(insight_markdowns) == 4, f"Expected 4 insight blocks, found {len(insight_markdowns)}"

for i, text in enumerate(insight_markdowns, 1):
    print(f"\n--- Insight {i} ---")
    print("Content:", text.encode("ascii", "replace").decode("ascii"))
    
    # Verify that it is NOT wrapped in raw HTML div like <div class="insight-card">...</div>
    assert not text.startswith("<div"), f"Insight {i} must not be wrapped in raw HTML div! Found: {text[:30]}"
    assert not text.endswith("</div>"), f"Insight {i} must not end with raw HTML div!"
    
    # Verify it has valid markdown bold syntax that markdown parsers convert to <strong>
    bold_tokens = re.findall(r"\*\*(.+?)\*\*", text)
    print("Bold tokens correctly identified:", [b.encode("ascii", "replace").decode("ascii") for b in bold_tokens])
    assert len(bold_tokens) >= 2, f"Expected bold tokens in insight {i}, found {len(bold_tokens)}"

print("\n==================================================")
print("SUCCESS: All 4 insights are pure, valid Markdown!")
print("==================================================")
