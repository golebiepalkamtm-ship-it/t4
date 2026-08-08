"""
Audit finalnego pliku - czy wyciagniety jest bezpieczny max?
Porownanie: cks ok (oryg) vs cks ok_stage1_lowend.bin (finalny)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"d:\t4")
from edc15_analyzer import ECUBinaryReader, MAP_DEFINITIONS

orig = ECUBinaryReader(r"d:\t4\cks ok")
final = ECUBinaryReader(r"d:\t4\cks ok_stage1_pro.bin")

# Absolutne limity sprzetowe (stock turbo K14/GT1749 + VP37 11mm)
HW_LIMITS = {
    "driver_wish":       {"safe_max": 65.0,  "hw_limit": 75.0,  "unit": "mg/hub"},
    "torque_limiter":    {"safe_max": 56.0,  "hw_limit": 65.0,  "unit": "mg/hub"},
    "smoke_limiter_0c":  {"safe_max": 64.0,  "hw_limit": 70.0,  "unit": "mg/hub"},
    "boost_target":      {"safe_max": 2200.0,"hw_limit": 2500.0,"unit": "mBar"},
    "boost_limiter":     {"safe_max": 2300.0,"hw_limit": 2600.0,"unit": "mBar"},
    "pump_voltage":      {"safe_max": 4.45,  "hw_limit": 4.5,   "unit": "V"},
}

SEP = "=" * 100
sep = "-" * 80

print(f"\n{SEP}")
print(f"  AUDIT MAX — czy wyciagniety jest bezpieczny max?")
print(f"  Stock turbo K14/GT1749 + VP37 pump 11mm + AXG 151hp")
print(f"{SEP}\n")
print(f"  {'MAPA':<35} {'ORYG':>8} {'TERAZ':>8} {'SAFE_MAX':>10} {'HW_LIM':>10} {'REZERWA':>10} {'STATUS'}")
print(f"  {'-'*35} {'-'*8} {'-'*8} {'-'*10} {'-'*10} {'-'*10} {'-'*20}")

for key, lim in HW_LIMITS.items():
    md = MAP_DEFINITIONS[key]
    orig_vals  = [v for row in orig.read_map(md,  codeblock=5) for v in row]
    final_vals = [v for row in final.read_map(md, codeblock=5) for v in row]

    orig_max  = max(orig_vals)
    final_max = max(final_vals)
    safe_max  = lim["safe_max"]
    hw_limit  = lim["hw_limit"]
    unit      = lim["unit"]

    rezerwa = safe_max - final_max
    pct_safe = (final_max / safe_max) * 100

    if pct_safe >= 99:
        status = "[MAX]  wyciagniety!"
    elif pct_safe >= 90:
        status = "[OK]   blisko max"
    elif pct_safe >= 75:
        status = "[OK]   jest rezerwa"
    else:
        status = "[LOW]  duzo rezerwy"

    print(f"  {md.name[:35]:<35} {orig_max:>8.2f} {final_max:>8.2f} {safe_max:>10.2f} {hw_limit:>10.2f} {rezerwa:>+10.2f} {status}  ({pct_safe:.1f}%)")

print(f"\n{SEP}")
print(f"  WNIOSKI:")

# Driver wish
dw_orig = max(v for row in orig.read_map(MAP_DEFINITIONS["driver_wish"], 5) for v in row)
dw_fin  = max(v for row in final.read_map(MAP_DEFINITIONS["driver_wish"], 5) for v in row)
print(f"  Driver Wish:  {dw_orig:.1f} -> {dw_fin:.1f} mg/hub  (safe max 65)  {'>>> WYCIAGNIETY!' if dw_fin >= 64 else f'rezerwa {65-dw_fin:.1f} mg'}")

bst_fin = max(v for row in final.read_map(MAP_DEFINITIONS["boost_target"], 5) for v in row)
print(f"  Boost Target: {bst_fin:.0f} mBar  (safe max 2200 dla stock turbo)  {'>>> NA LIMICIE!' if bst_fin >= 2190 else f'rezerwa {2200-bst_fin:.0f} mBar'}")

pmp_fin = max(v for row in final.read_map(MAP_DEFINITIONS["pump_voltage"], 5) for v in row if v > 0)
print(f"  Pump VP37:    {pmp_fin:.3f}V  (fizyczny limit 4.5V)  {'>>> NA LIMICIE!' if pmp_fin >= 4.44 else f'rezerwa {4.45-pmp_fin:.3f}V'}")

print(f"\n  ODPOWIEDZ: ", end="")
if dw_fin >= 64 and bst_fin >= 2190 and pmp_fin >= 4.44:
    print("TAK — wyciagniety jest bezpieczny max dla stock hardware!")
elif dw_fin >= 60 and bst_fin >= 2100:
    print("PRAWIE — ok 90-95% bezpiecznego max. Mozna jeszcze troche...")
else:
    print("NIE — jest jeszcze rezerwa do wykorzystania.")

print(f"{SEP}\n")
