import re

with open(r'd:\t4\cks ok.xdf', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

tables = content.split("%%TABLE%%")
print(f"Total tables: {len(tables)}")

keywords = ["driver", "wish", "pedal", "boost", "torque", "limiter", "smoke", "n75", "soi", "egr", "pump", "maf", "voltage"]

for t in tables[1:]:
    title_m = re.search(r'Title\s*="([^"]+)"', t, re.IGNORECASE)
    addr_m = re.search(r'Address\s*=0x([0-9A-Fa-f]+)', t, re.IGNORECASE)
    rows_m = re.search(r'Rows\s*=0x([0-9A-Fa-f]+)', t, re.IGNORECASE)
    cols_m = re.search(r'Cols\s*=0x([0-9A-Fa-f]+)', t, re.IGNORECASE)
    
    title = title_m.group(1) if title_m else "Unknown"
    addr = f"0x{addr_m.group(1)}" if addr_m else "N/A"
    rows = int(rows_m.group(1), 16) if rows_m else 0
    cols = int(cols_m.group(1), 16) if cols_m else 0
    
    # Filter by keywords or interesting map sizes
    if any(k in title.lower() for k in keywords) or (rows > 2 and cols > 2):
        print(f"Title: {title:<50} | Addr: {addr:<10} | Size: {rows}x{cols}")
