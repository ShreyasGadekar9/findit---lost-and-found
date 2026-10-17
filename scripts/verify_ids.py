# scripts/verify_ids.py
import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

ids_called = re.findall(r"document\.getElementById\(['\"]([^'\"]+)['\"]\)", text)
ids_defined = set(re.findall(r"id=['\"]([^'\"]+)['\"]", text))

missing = [i for i in set(ids_called) if i not in ids_defined]

print(f"Total getElementById targets: {len(set(ids_called))}")
print(f"Total defined IDs: {len(ids_defined)}")
if missing:
    print("Missing IDs:", missing)
else:
    print("ALL IDs VALID AND FOUND!")
