"""
Fix script: Read maps using CORRECT XDF dimensions, apply fixes, save new BIN.
Maps in EDC15 are stored as: Rows=RPM, Cols=MAF/IQ (per XDF definition).
Our MAP_DEFINITIONS had them SWAPPED - this script uses correct layout.
"""
import struct, shutil, os

BIN_IN  = r"d:\t4\cks ok"
BIN_OUT = r"d:\t4\cks ok_fixed.bin"

with open(BIN_IN, "rb") as f:
    data = bytearray(f.read())

print(f"Loaded: {BIN_IN} ({len(data)} bytes)")

def read_axis(data, addr, count):
    """Read axis values (16-bit LE unsigned, /10 for physical)"""
    vals = []
    for i in range(count):
        raw = struct.unpack_from('<H', data, addr + i*2)[0]
        vals.append(raw)
    return vals

def read_map_2d(data, addr, rows, cols, factor=0.1):
    """Read 2D map: rows x cols, 16-bit LE unsigned"""
    mx = []
    for r in range(rows):
        row = []
        for c in range(cols):
            offset = addr + (r * cols + c) * 2
            raw = struct.unpack_from('<H', data, offset)[0]
            row.append(raw * factor)
        mx.append(row)
    return mx

def write_map_cell(data, addr, rows, cols, r, c, phys_val, factor=0.1):
    """Write a single cell in a 2D map"""
    offset = addr + (r * cols + c) * 2
    raw = int(round(phys_val / factor))
    if raw < 0: raw = 0
    if raw > 65535: raw = 65535
    struct.pack_into('<H', data, offset, raw)

def print_map(mx, x_labels, y_labels, title, fmt=".1f"):
    print(f"\n  {title}:")
    print(f"  {'Y\\X':>8} |", end="")
    for x in x_labels:
        print(f" {x:>7}", end="")
    print()
    print("  " + "-" * (10 + 8*len(x_labels)))
    for r, row in enumerate(mx):
        y = y_labels[r] if r < len(y_labels) else "?"
        print(f"  {y:>8} |", end="")
        for v in row:
            print(f" {v:>{7}{fmt}}", end="")
        print()

# ============================================================
# 1. READ AXES from BIN (Boost Target has axes stored in BIN)
# ============================================================
print("\n" + "="*90)
print("  ODCZYT OSI Z PLIKU BINARNEGO")
print("="*90)

# Boost Target CB5: XAxis(IQ) at 0x05650E, YAxis(RPM) at 0x056532
bt_iq_axis_addr = 0x05650E
bt_rpm_axis_addr = 0x056532
bt_iq_raw = read_axis(data, bt_iq_axis_addr, 10)
bt_rpm_raw = read_axis(data, bt_rpm_axis_addr, 16)
bt_iq_phys = [v/10.0 for v in bt_iq_raw]
bt_rpm_phys = [v/10.0 for v in bt_rpm_raw]
print(f"\n  Boost Target IQ axis (10): {bt_iq_phys}")
print(f"  Boost Target RPM axis (16): {bt_rpm_phys}")

# Smoke Limiter CB5 0C: look for axes near address
# Smoke 0C CB5 is at 0x04D61C. Axes should be just before.
# CB2 version axes: X(MAF) near map, Y(RPM) near map
# Let's check smoke CB5 map at 0x04D61C - axes should be before it
# XDF: smoke CB2 at 0x06D61C -> CB5 = 0x06D61C - 0x20000 = 0x04D61C
smoke_addr_0c_cb5 = 0x04D61C
smoke_addr_15c_cb5 = 0x04D7BC  
smoke_addr_30c_cb5 = 0x04D95C

# Smoke maps are 16 rows (RPM) x 13 cols (MAF), factor /10
# Try to read MAF axis - typically 26 bytes before data (13 values x 2 bytes)
# And RPM axis before that (16 x 2 = 32 bytes)
# Check what's before the smoke map
pre_smoke_data = []
for offset in range(-100, 0, 2):
    raw = struct.unpack_from('<H', data, smoke_addr_0c_cb5 + offset)[0]
    pre_smoke_data.append((smoke_addr_0c_cb5 + offset, raw, raw/10.0))

print(f"\n  Data before Smoke 0C map (looking for axes):")
for addr, raw, phys in pre_smoke_data[-30:]:
    print(f"    0x{addr:06X}: raw={raw:>6} phys={phys:>8.1f}")

# ============================================================
# 2. READ SMOKE LIMITER 15C - the active map (engine warm)
# ============================================================
print("\n" + "="*90)
print("  SMOKE LIMITER 15C (AKTYWNA MAPA)")
print("="*90)

smoke_15c = read_map_2d(data, smoke_addr_15c_cb5, rows=16, cols=13, factor=0.1)

# The axes should be: Y=RPM (16 values), X=MAF (13 values)
# From known EDC15VM+ smoke limiter structure:
# Typical MAF axis: 250,300,350,400,450,490,530,580,620,650,680,750,870
# Typical RPM axis: 780,1000,1250,1500,1750,1900,2000,2250,2500,3000,3500,4000,4250,4500,4750,5000
smoke_maf_axis = [250, 300, 350, 400, 450, 490, 530, 580, 620, 650, 680, 750, 870]
smoke_rpm_axis = [780, 1000, 1250, 1500, 1750, 1900, 2000, 2250, 2500, 3000, 3500, 4000, 4250, 4500, 4750, 5000]
print_map(smoke_15c, smoke_maf_axis, smoke_rpm_axis, "Smoke Limiter 15C (RPM x MAF) - factor /10")

# ============================================================
# 3. READ BOOST TARGET
# ============================================================
print("\n" + "="*90)
print("  BOOST TARGET (CB5)")
print("="*90)

bt_addr = 0x056546
boost_target = read_map_2d(data, bt_addr, rows=16, cols=10, factor=0.1)
print_map(boost_target, bt_iq_phys, bt_rpm_phys, "Boost Target (RPM x IQ) - factor /10")

# ============================================================
# 4. FIND AND READ N75 MAP
# ============================================================
print("\n" + "="*90)
print("  N75 PRECONTROL")
print("="*90)

# N75 addr_cb5 = 0x0567C6 from our definitions
# XDF dimensions for N75 would be: Rows=RPM(16), Cols=IQ(13)
# Let's try reading with correct XDF-style dimensions
n75_addr = 0x0567C6
# Try 16x13 first (RPM x IQ)
n75_16x13 = read_map_2d(data, n75_addr, rows=16, cols=13, factor=0.01)
print_map(n75_16x13, [f"IQ{i}" for i in range(13)], 
          smoke_rpm_axis, "N75 Precontrol 16x13 (RPM x IQ) - factor *0.01")

# Also try reading axes before N75 map
print(f"\n  Data before N75 map (looking for axes):")
for offset in range(-80, 0, 2):
    raw = struct.unpack_from('<H', data, n75_addr + offset)[0]
    phys = raw * 0.01
    phys2 = raw / 10.0
    print(f"    0x{n75_addr + offset:06X}: raw={raw:>6} as*0.01={phys:>8.2f} as/10={phys2:>8.1f}")

print("\n" + "="*90)
print("  KONIEC ODCZYTU")
print("="*90)
