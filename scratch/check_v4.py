import sys
sys.path.insert(0, r"d:\t4")
from edc15_analyzer import ECUBinaryReader, MAP_DEFINITIONS

BIN_ORIG = r"d:\t4\cks ok"
BIN_FIXED = r"d:\t4\cks ok_fixed_v4.bin"

ecu_orig = ECUBinaryReader(BIN_ORIG)
ecu_fixed = ECUBinaryReader(BIN_FIXED)

print("="*60)
print("RAPORT V4 CLEAN - POTWIERDZENIE ZMIAN")
print("="*60)

# Check Pump voltage sync
sync_pv = True
for r in range(14):
    for c in range(16):
        if ecu_fixed.read_map(MAP_DEFINITIONS['pump_voltage'], 5)[r][c] != ecu_fixed.read_map(MAP_DEFINITIONS['pump_voltage'], 2)[r][c]:
            sync_pv = False
print(f"1. Pump Voltage zsynchronizowane CB5 = CB2: {'TAK' if sync_pv else 'NIE'}")

# Check EGR
egr_max = max([v for row in ecu_fixed.read_map(MAP_DEFINITIONS['egr'], 5) for v in row])
print(f"2. EGR Wylaczony (wszystkie komorki 0%): {'TAK' if egr_max == 0 else 'NIE (max ' + str(egr_max) + '%)'}")

# Check N75 max
n75_max = ecu_fixed.get_map_summary(MAP_DEFINITIONS["n75_duty"], 5)['max']
print(f"3. N75 Max (bylo 599.7%): {n75_max:.1f}%")

# Check SOI max
soi_max = ecu_fixed.get_map_summary(MAP_DEFINITIONS["soi_map"], 5)['max']
print(f"4. SOI Max (bylo 655.4): {soi_max:.1f} deg")

# Check MAF max
maf_max = ecu_fixed.get_map_summary(MAP_DEFINITIONS["maf_linearization"], 5)['max']
print(f"5. MAF Lin. Max (bylo 6553.3): {maf_max:.1f} kg/h")

# Check Boost Limiter
bl = ecu_fixed.get_map_summary(MAP_DEFINITIONS["boost_limiter"], 5)
print(f"6. Boost Limiter: max={bl['max']:.0f} mBar, min={bl['min']:.0f} mBar (gorski krzywa zachowana)")

# Check Out of Map bytes
map_ranges = []
for key, md in MAP_DEFINITIONS.items():
    for cb in [5, 2]:
        base = md.addr_cb5 if cb == 5 else md.addr_cb2
        end = base + md.rows * md.cols * 2
        map_ranges.append((base, end))

diff_outside = 0
for i in range(len(ecu_orig.data)):
    if ecu_orig.data[i] != ecu_fixed.data[i]:
        if not any(b <= i < e for b, e in map_ranges):
            diff_outside += 1

print(f"7. Bajty zmienione poza mapami: {diff_outside}")
