import struct

with open(r"d:\t4\cks ok", "rb") as f:
    cks_data = f.read()

with open(r"d:\t4\VW_T4_2.5_TDI_2000_Turbodiesel___110.3KWKW_Bosch_0281010461_074906018AJ_360079_8D73.Original", "rb") as f:
    orig_360079 = f.read()

with open(r"d:\t4\VW_T4_2.5_TDI_1999_Turbodiesel___110.3KWKW_Bosch_0281001764_074906021M__356867-868_D28E.Original", "rb") as f:
    orig_21M = f.read()

print(f"cks ok (SW: 362445) size: {len(cks_data)}")
print(f"018AJ  (SW: 360079) size: {len(orig_360079)}")
print(f"021M   (SW: 330055) size: {len(orig_21M)}")

# Szukamy naglowkow osi Driver Wish (np. 9x16 lub 16x9: rows=9 cols=16)
def find_map_headers(data, name):
    print(f"\n--- Wyszukiwanie wzorcow w {name} ---")
    # W EDC15 mapy maja zazwyczaj naglowki osi X/Y przed danymi
    # Szukamy przykladowo osi RPM: 780, 1000, 1250, 1500, 1750...
    rpm_bytes = struct.pack('<HHHH', 780, 1000, 1250, 1500)
    pos = 0
    while True:
        idx = data.find(rpm_bytes, pos)
        if idx == -1:
            break
        print(f"  Znaleziono os RPM (780, 1000, ...) na adresie HEX: {hex(idx)}")
        pos = idx + 1

find_map_headers(cks_data, "cks ok (SW: 362445)")
find_map_headers(orig_360079, "074906018AJ (SW: 360079)")
find_map_headers(orig_21M, "074906021M (SW: 330055)")
