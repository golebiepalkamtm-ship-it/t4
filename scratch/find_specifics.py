import re

XDF_FILE = r"d:\t4\cks ok.xdf"

tables = []
current = {}
with open(XDF_FILE, 'r', encoding='utf-8', errors='replace') as f:
    for line in f:
        line = line.strip()
        if line == '%%TABLE%%':
            current = {}
        elif line == '%%END%%':
            if current: tables.append(current)
            current = {}
        else:
            m = re.match(r'\d+ (\w+)\s+=\s*(.+)', line)
            if m:
                key, val = m.group(1), m.group(2).strip().strip('"')
                current[key] = val

print("MAPS 16x13 or 13x16 in 0x040000 - 0x060000:")
for t in tables:
    if 'Address' not in t: continue
    addr = int(t['Address'], 16)
    if not (0x40000 <= addr <= 0x60000): continue
    
    rows = int(t.get('Rows', '1'), 16)
    cols = int(t.get('Cols', '1'), 16)
    title = t.get('Title', 'Unknown')
    
    # N75 size
    if (rows==16 and cols==13) or (rows==13 and cols==16):
        print(f"0x{addr:06X} {rows}x{cols} '{title}'")
        
    # Driver wish usually 8x16, 16x8, 10x16, 16x10, etc
    if 'wish' in title.lower() or 'pedal' in title.lower():
        print(f"0x{addr:06X} {rows}x{cols} '{title}'")

