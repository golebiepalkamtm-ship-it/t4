import os
import re
import struct

def read_xdf(xdf_path):
    with open(xdf_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    tables = []
    # Split by %%TABLE%%
    blocks = content.split("%%TABLE%%")[1:]
    for block in blocks:
        block = block.split("%%END%%")[0]
        
        table = {}
        title_m = re.search(r'040005 Title\s*="(.*?)"', block)
        addr_m = re.search(r'040100 Address\s*=(0x[0-9A-Fa-f]+)', block)
        rows_m = re.search(r'040300 Rows\s*=0x([0-9A-Fa-f]+)', block)
        cols_m = re.search(r'040305 Cols\s*=0x([0-9A-Fa-f]+)', block)
        
        if addr_m and rows_m and cols_m:
            table['title'] = title_m.group(1) if title_m else "Unknown"
            table['address'] = int(addr_m.group(1), 16)
            table['rows'] = int(rows_m.group(1), 16)
            table['cols'] = int(cols_m.group(1), 16)
            
            size_m = re.search(r'SizeInBits\s*=(0x[0-9A-Fa-f]+)', block)
            bits = int(size_m.group(1), 16) if size_m else 16
            table['bytes'] = bits // 8
            if table['bytes'] not in [1, 2]: table['bytes'] = 2
            
            tables.append(table)
            
    return tables

def read_map(data, address, rows, cols, bsize=2):
    matrix = []
    for r in range(rows):
        row = []
        for c in range(cols):
            offset = address + (r * cols + c) * bsize
            if offset + bsize <= len(data):
                if bsize == 2:
                    val = struct.unpack_from("<H", data, offset)[0]
                else:
                    val = data[offset]
                row.append(val)
        matrix.append(row)
    return matrix

def compare():
    xdf_path = r"c:\Users\manta\Desktop\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_A0FF.xdf"
    
    files = {
        "Original": r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_8D73.Original",
        "Stage 1": r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_A0FF.Stage1",
        "Stage 2": r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_3D43.Stage2",
        "Stage 3": r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_992F.Stage3"
    }
    
    tables = read_xdf(xdf_path)
    print(f"Zdekodowano {len(tables)} tabel z pliku XDF.")
    
    bins = {}
    for name, path in files.items():
        if os.path.exists(path):
            with open(path, "rb") as f:
                bins[name] = f.read()
    
    orig = bins.get("Original")
    if not orig:
        print("Brak pliku Original do bazy.")
        return

    modified_maps = []
    
    for t in tables:
        addr = t['address']
        rows = t['rows']
        cols = t['cols']
        bs = t['bytes']
        
        orig_map = read_map(orig, addr, rows, cols, bs)
        
        changed_stages = []
        for stage in ["Stage 1", "Stage 2", "Stage 3"]:
            if stage in bins:
                s_map = read_map(bins[stage], addr, rows, cols, bs)
                if s_map != orig_map:
                    sum_orig = sum(v for row in orig_map for v in row)
                    sum_s = sum(v for row in s_map for v in row)
                    diff = sum_s - sum_orig
                    pct = (diff / sum_orig * 100) if sum_orig != 0 else 0
                    changed_stages.append(f"{stage} ({pct:+.1f}%)")
                    
        if changed_stages:
            modified_maps.append({
                'title': t['title'],
                'addr': hex(addr),
                'size': f"{rows}x{cols}",
                'changes': ", ".join(changed_stages)
            })
            
    # Sort and print nicely
    print("\nZNALEZIONE MODYFIKACJE W STAGE'ACH WZGLĘDEM ORYGINAŁU:")
    print("=" * 110)
    print(f"{'Tytuł Mapy (z XDF)':<35} | {'Adres':<8} | {'Rozmiar':<7} | Zmiany")
    print("-" * 110)
    for m in modified_maps:
        title_cl = m['title'][:34]
        print(f"{title_cl:<35} | {m['addr']:<8} | {m['size']:<7} | {m['changes']}")

if __name__ == "__main__":
    compare()
