"""
EDC15VM+ STAGE 1 PRO — VW T4 2.5 TDI AXG 151KM
Plik bazowy: d:\t4\cks ok
Plik wyjsciowy: d:\t4\cks ok_stage1_pro.bin
"""

import sys, copy
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"d:\t4")
from edc15_analyzer import ECUBinaryReader, MAP_DEFINITIONS

INPUT_BIN  = r"d:\t4\cks ok"
OUTPUT_BIN = r"d:\t4\cks ok_stage1_pro.bin"

# Osie RPM z edc15_analyzer
RPM_AXIS_16 = [780,1000,1250,1500,1750,1900,2000,2250,2500,3000,3500,4000,4250,4500,4750,5000]
RPM_AXIS_23 = [450,470,600,780,1000,1250,1500,1750,1900,2000,2250,2500,3000,3250,3500,3750,3900,4000,4100,4250,4500,4750,5100]
MAF_AXIS_13 = [250, 300, 350, 400, 450, 490, 530, 580, 620, 650, 680, 750, 870] # To są przybliżone, patrzymy na r_idx
ATMOS_3     = [750,850,950]

ecu = ECUBinaryReader(INPUT_BIN)

SEP = "=" * 100
sep = "-" * 100
total_changes = 0

print(f"\n{SEP}")
print(f"  EDC15VM+ STAGE 1 PRO — VW T4 2.5 TDI AXG 151KM")
print(f"{SEP}\n")

# 1. SMOKE LIMITER - Obnizenie na niskim MAF (mniej dymu)
for smoke_key in ["smoke_limiter_0c", "smoke_limiter_15c", "smoke_limiter_30c"]:
    md = MAP_DEFINITIONS[smoke_key]
    matrix = ecu.read_map(md, codeblock=5)
    
    for r in range(md.rows):
        for c in range(md.cols):
            v = matrix[r][c]
            # Oceniamy po numerze wiersza, w edc15_analyzer:
            # 0-3 to bardzo niskie MAF (np. 250-400 mg)
            if r <= 3:
                matrix[r][c] = min(v, 20.0) # max 20mg na niskim
            elif r == 4:
                matrix[r][c] = min(v, 25.0)
            elif r == 5:
                matrix[r][c] = min(v, 30.0)
            # Górne wiersze (pelne load) lekko w góre aby nie limitowały Torque Limitera (55mg)
            elif r >= 9:
                if v < 56.0 and v > 40.0:
                    matrix[r][c] = min(v + 3.0, 58.0)
                    
    ecu.write_map(md, matrix, codeblock=5)
    ecu.write_map(md, matrix, codeblock=2)
    print(f"  Zaktualizowano: {md.name}")

# 2. N75 DUTY CYCLE - Mocniejsze domkniecie na dole
md_n75 = MAP_DEFINITIONS["n75_duty"]
matrix_n75 = ecu.read_map(md_n75, codeblock=5)
for r in range(md_n75.rows):
    for c in range(md_n75.cols):
        v = matrix_n75[r][c]
        if v > 100.0 or v < 0.5: continue
        
        # Load index: r. RPM index: c.
        if 4 <= r <= 6 and c <= 5: # 1000-2000 RPM, sredni load
            matrix_n75[r][c] = min(v + 10.0, 60.0)
        elif 7 <= r <= 9 and c <= 4:
            matrix_n75[r][c] = min(v + 5.0, 75.0)
ecu.write_map(md_n75, matrix_n75, codeblock=5)
ecu.write_map(md_n75, matrix_n75, codeblock=2)
print(f"  Zaktualizowano: {md_n75.name}")

# 3. TORQUE LIMITER - Wiecej momentu do 55mg!
md_tl = MAP_DEFINITIONS["torque_limiter"]
matrix_tl = ecu.read_map(md_tl, codeblock=5)
for r in range(md_tl.rows):
    for c in range(md_tl.cols):
        v = matrix_tl[r][c]
        if v < 1.0: continue
        # To jest 23 kolumn. Zrobmy manualne mapowanie:
        # Oryginal: 0 25 29 28 28 38 43 49 50 50 50 50 51 51 51 51 51 51 50 46 34 16 0
        if c == 5: matrix_tl[r][c] = 42.0   # 1100
        if c == 6: matrix_tl[r][c] = 48.0   # 1250
        if c == 7: matrix_tl[r][c] = 53.0   # 1500
        if c >= 8 and c <= 17: matrix_tl[r][c] = 55.0 # 1750 - 4000 RPM
        if c == 18: matrix_tl[r][c] = 53.0  # 4100
        if c == 19: matrix_tl[r][c] = 50.0  # 4250
        if c == 20: matrix_tl[r][c] = 45.0  # 4500
ecu.write_map(md_tl, matrix_tl, codeblock=5)
ecu.write_map(md_tl, matrix_tl, codeblock=2)
print(f"  Zaktualizowano: {md_tl.name} -> Max 55.00 mg")

# 4. BOOST TARGET - Zwiekszenie doladowania do 2250mbar
md_bt = MAP_DEFINITIONS["boost_target"]
matrix_bt = ecu.read_map(md_bt, codeblock=5)
for r in range(md_bt.rows):
    for c in range(md_bt.cols):
        v = matrix_bt[r][c]
        if v > 2050:
            # Plynnie dodajemy, max 2250
            matrix_bt[r][c] = min(v + 60, 2250.0)
ecu.write_map(md_bt, matrix_bt, codeblock=5)
ecu.write_map(md_bt, matrix_bt, codeblock=2)
print(f"  Zaktualizowano: {md_bt.name} -> Max 2250 mbar")

# 5. BOOST LIMITER - Podniesienie do 2350mbar 
md_bl = MAP_DEFINITIONS["boost_limiter"]
matrix_bl = ecu.read_map(md_bl, codeblock=5)
for r in range(md_bl.rows):
    for c in range(md_bl.cols):
        v = matrix_bl[r][c]
        if v > 2100:
            matrix_bl[r][c] = 2350.0
ecu.write_map(md_bl, matrix_bl, codeblock=5)
ecu.write_map(md_bl, matrix_bl, codeblock=2)
print(f"  Zaktualizowano: {md_bl.name} -> Max 2350 mbar")


print(f"\n{SEP}")
ecu.save_bin(OUTPUT_BIN)
print(f"  [SUKCES] STAGE 1 PRO GOTOWY: {OUTPUT_BIN}")
print(f"{SEP}\n")

