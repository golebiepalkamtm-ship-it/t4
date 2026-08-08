"""
Odczyt kluczowych map z pliku cks ok (Stage 1) do diagnozy problemu:
- czarny dym na wolnych
- muli z dolu
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"d:\t4")
from edc15_analyzer import ECUBinaryReader, MAP_DEFINITIONS

ecu = ECUBinaryReader(r"d:\t4\cks ok")

RPM16 = [750,1000,1250,1500,1750,2000,2250,2500,2750,3000,3250,3500,3750,4000,4250,4500]
RPM23 = [600,700,800,900,1000,1100,1250,1500,1750,2000,2250,2500,2750,3000,3250,3500,3750,4000,4250,4500,4750,5000,5250]
MAF13 = [0,8,17,25,34,42,51,59,67,76,84,93,101]
ATMOS3 = [750,1013,1100]
PEDAL9 = [0,10,20,30,40,50,60,70,80]

SEP = "=" * 120

# --- SMOKE LIMITER 0C ---
print(f"\n{SEP}")
print("  SMOKE LIMITER 0C (mg/suw) — cks ok (Stage 1)")
print(SEP)
md = MAP_DEFINITIONS["smoke_limiter_0c"]
matrix = ecu.read_map(md, codeblock=5)
header = "MAF\\RPM"
print(f"  {header:>7}", end="")
for rpm in RPM16[:md.cols]:
    print(f"{rpm:>7}", end="")
print()
print("  " + "-" * (7 + 7 * md.cols))
for r, row in enumerate(matrix):
    label = MAF13[r] if r < len(MAF13) else r
    print(f"  {label:>7}", end="")
    for v in row:
        print(f"{v:>7.1f}", end="")
    print()

# --- N75 DUTY ---
print(f"\n{SEP}")
print("  N75 DUTY CYCLE (%) — cks ok (Stage 1)")
print(SEP)
md2 = MAP_DEFINITIONS["n75_duty"]
matrix2 = ecu.read_map(md2, codeblock=5)
header2 = "LD\\RPM"
print(f"  {header2:>7}", end="")
for rpm in RPM16[:md2.cols]:
    print(f"{rpm:>7}", end="")
print()
print("  " + "-" * (7 + 7 * md2.cols))
for r, row in enumerate(matrix2):
    label = MAF13[r] if r < len(MAF13) else r
    print(f"  {label:>7}", end="")
    for v in row:
        print(f"{v:>7.1f}", end="")
    print()

# --- TORQUE LIMITER ---
print(f"\n{SEP}")
print("  TORQUE LIMITER (mg/suw) — cks ok (Stage 1)")
print(SEP)
md3 = MAP_DEFINITIONS["torque_limiter"]
matrix3 = ecu.read_map(md3, codeblock=5)
header3 = "ATM\\RPM"
print(f"  {header3:>7}", end="")
for rpm in RPM23[:md3.cols]:
    print(f"{rpm:>7}", end="")
print()
print("  " + "-" * (7 + 7 * md3.cols))
for r, row in enumerate(matrix3):
    label = ATMOS3[r] if r < len(ATMOS3) else r
    print(f"  {label:>7}", end="")
    for v in row:
        print(f"{v:>7.2f}", end="")
    print()

# --- DRIVER WISH ---
print(f"\n{SEP}")
print("  DRIVER WISH (mg/suw) — cks ok (Stage 1)")
print(SEP)
md4 = MAP_DEFINITIONS["driver_wish"]
matrix4 = ecu.read_map(md4, codeblock=5)
header4 = "PED\\RPM"
print(f"  {header4:>7}", end="")
for rpm in RPM16[:md4.cols]:
    print(f"{rpm:>7}", end="")
print()
print("  " + "-" * (7 + 7 * md4.cols))
for r, row in enumerate(matrix4):
    label = PEDAL9[r] if r < len(PEDAL9) else r
    print(f"  {label:>7}", end="")
    for v in row:
        print(f"{v:>7.1f}", end="")
    print()

# --- BOOST TARGET ---
print(f"\n{SEP}")
print("  BOOST TARGET (mbar) — cks ok (Stage 1)")
print(SEP)
md5 = MAP_DEFINITIONS["boost_target"]
matrix5 = ecu.read_map(md5, codeblock=5)
LOAD10 = [0,8,17,25,34,42,51,59,67,76]
header5 = "LD\\RPM"
print(f"  {header5:>7}", end="")
for rpm in RPM16[:md5.cols]:
    print(f"{rpm:>7}", end="")
print()
print("  " + "-" * (7 + 7 * md5.cols))
for r, row in enumerate(matrix5):
    label = LOAD10[r] if r < len(LOAD10) else r
    print(f"  {label:>7}", end="")
    for v in row:
        print(f"{v:>7.0f}", end="")
    print()

print(f"\n{SEP}")
