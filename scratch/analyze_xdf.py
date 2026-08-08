import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

xdf_path = r"d:\t4\cks ok.xdf"
with open(xdf_path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

tables = content.split("%%TABLE%%")[1:]
print(f"Liczba wszystkich bloków tabel w cks ok.xdf: {len(tables)}")

named_tables = []
all_parsed = []

for t in tables:
    title_m = re.search(r'040005 Title\s*="(.*?)"', t)
    addr_m = re.search(r'040100 Address\s*=(0x[0-9A-Fa-f]+)', t)
    rows_m = re.search(r'040300 Rows\s*=0x([0-9A-Fa-f]+)', t)
    cols_m = re.search(r'040305 Cols\s*=0x([0-9A-Fa-f]+)', t)

    title = title_m.group(1) if title_m else ""
    addr_str = addr_m.group(1) if addr_m else "0x0"
    addr_int = int(addr_str, 16) if addr_str else 0
    rows = int(rows_m.group(1), 16) if rows_m else 0
    cols = int(cols_m.group(1), 16) if cols_m else 0

    all_parsed.append((title, addr_int, rows, cols, addr_str))
    if title and not title.startswith("3D ") and not title.startswith("2D "):
        named_tables.append((title, addr_str, f"{rows}x{cols}"))

print(f"Liczba zmapowanych (nazwanych) tabel: {len(named_tables)}")

# Porównaj z MAP_DEFINITIONS z edc15_analyzer
sys.path.insert(0, r"d:\t4")
from edc15_analyzer import MAP_DEFINITIONS

print("\n=== KORELACJA ADRESÓW PYTHON (MAP_DEFINITIONS) ↔ CKS OK.XDF ===")
print(f"  {'Klucz Pythona':<20} | {'CB5 Adres':<10} | {'XDF Tytuł (CB5)':<35} | {'CB2 Adres':<10} | {'XDF Tytuł (CB2)'}")
print("  " + "-" * 110)

for key, md in MAP_DEFINITIONS.items():
    match_cb5 = [t for t in all_parsed if t[1] == md.addr_cb5]
    match_cb2 = [t for t in all_parsed if t[1] == md.addr_cb2]

    t_cb5_title = match_cb5[0][0] if match_cb5 else "NIE ZMNALEZIONO W XDF"
    t_cb2_title = match_cb2[0][0] if match_cb2 else "NIE ZMNALEZIONO W XDF"

    print(f"  {key:<20} | {hex(md.addr_cb5):<10} | {t_cb5_title:<35} | {hex(md.addr_cb2):<10} | {t_cb2_title}")
