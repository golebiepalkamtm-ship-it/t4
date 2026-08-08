"""
EDC15VM+ LOW-END TORQUE FIX — VW T4 2.5 TDI AXG
Problem: brak momentu na "dole" (1200-2000 RPM, 3. bieg)
Rozwiazanie: Wieksze skalowanie w niskich kolumnach RPM (cols 0-5 = 750-2000 RPM)

Baza:    d:\t4\cks ok_stage1_pro.bin  (Stage 1 Pro juz zastosowany)
Wyjscie: d:\t4\cks ok_stage1_lowend.bin

Metoda:
  - Driver Wish:   +15% na cols 0-5 (750-2000 RPM), +5% na cols 6-10
  - Smoke Lim:     +12% na cols 0-5 (wiecej paliwa na dole)
  - Boost Target:  +8%  na cols 0-6 (szybsze sprezenie turbo)
  - Torque Lim:    +8%  na cols 0-5 (odblokowujemy moment na dole)
  - Pump Voltage:  +5%  na komorkach medium-high load (row 5-13, col 0-6)
"""

import sys, copy
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"d:\t4")
from edc15_analyzer import ECUBinaryReader, MAP_DEFINITIONS

# Baza: Stage 1 Pro (juz zastosowany poprzednio)
INPUT_BIN  = r"d:\t4\cks ok_stage1_pro.bin"
OUTPUT_BIN = r"d:\t4\cks ok_stage1_lowend.bin"

# Osie RPM (16 kolumn)
RPM_AXIS = [750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000, 3250, 3500, 3750, 4000, 4250, 4500]

# "DOL" = cols gdzie RPM <= 2000 (indeksy 0-5)
# "SRODEK" = cols 6-10 (2250-3000 RPM)
LOW_RPM_MAX_COL  = 5   # do 2000 RPM (wlacznie)
MID_RPM_MAX_COL  = 10  # do 3000 RPM (wlacznie)

ecu = ECUBinaryReader(INPUT_BIN)
SEP = "=" * 100
sep = "-" * 100

print(f"\n{SEP}")
print(f"  EDC15VM+ LOW-END TORQUE FIX — VW T4 2.5 TDI AXG")
print(f"  Problem: brak momentu na 3. biegu (dol obrotow 750-2000 RPM)")
print(f"  Baza:    {INPUT_BIN}")
print(f"  Wyjscie: {OUTPUT_BIN}")
print(f"{SEP}\n")

total_changes = 0

def scale_map_by_col(ecu, key, md, low_scale, mid_scale, min_val, abs_max):
    """Skaluje mape z roznym wspolczynnikiem dla dolnych i srednich RPM."""
    matrix_orig = ecu.read_map(md, codeblock=5)
    matrix_new  = copy.deepcopy(matrix_orig)
    changed = []

    for r in range(md.rows):
        for c in range(md.cols):
            v = matrix_orig[r][c]
            if v < min_val:
                continue

            if c <= LOW_RPM_MAX_COL:
                scale = 1.0 + low_scale / 100.0
            elif c <= MID_RPM_MAX_COL:
                scale = 1.0 + mid_scale / 100.0
            else:
                scale = 1.0  # gorne RPM bez zmian

            v_new = round(v * scale, 3)
            if v_new > abs_max:
                v_new = abs_max

            if abs(v_new - v) > 0.001:
                changed.append((r, c, v, v_new))
                matrix_new[r][c] = v_new

    return matrix_new, changed


# ─── 1. DRIVER WISH (B1) ─────────────────────────────────────────────────────
md = MAP_DEFINITIONS["driver_wish"]
matrix_new, changed = scale_map_by_col(ecu, "driver_wish", md,
    low_scale=15.0, mid_scale=5.0, min_val=1.0, abs_max=67.0)
print(f"{sep}")
print(f"  DRIVER WISH [B1] — dol +15%, srodek +5%")
orig = ecu.read_map(md, codeblock=5)
orig_max = max(v for row in orig for v in row)
new_max  = max(v for row in matrix_new for v in row)
print(f"  Przed max: {orig_max:.2f} mg/hub  ->  Po max: {new_max:.2f} mg/hub")
print(f"  Zmienionych komorek: {len(changed)} / {md.rows*md.cols}")
for r, c, v_o, v_n in changed[:6]:
    print(f"    RPM~{RPM_AXIS[c] if c < len(RPM_AXIS) else '?':>4}  Row {r}:  {v_o:.2f} -> {v_n:.2f}  (+{v_n-v_o:.2f} mg/hub)")
if len(changed) > 6: print(f"    ... i {len(changed)-6} wiecej ...")
ecu.write_map(md, matrix_new, codeblock=5)
ecu.write_map(md, matrix_new, codeblock=2)
total_changes += len(changed)

# ─── 2. TORQUE LIMITER (LC) ──────────────────────────────────────────────────
md = MAP_DEFINITIONS["torque_limiter"]
matrix_new, changed = scale_map_by_col(ecu, "torque_limiter", md,
    low_scale=8.0, mid_scale=3.0, min_val=1.0, abs_max=58.0)
print(f"\n{sep}")
print(f"  TORQUE LIMITER [LC] — dol +8%, srodek +3%")
orig = ecu.read_map(md, codeblock=5)
new_max = max(v for row in matrix_new for v in row)
print(f"  Przed max: {max(v for row in orig for v in row):.2f} mg/hub  ->  Po max: {new_max:.2f} mg/hub")
print(f"  Zmienionych komorek: {len(changed)} / {md.rows*md.cols}")
for r, c, v_o, v_n in changed[:6]:
    print(f"    Col {c}:  {v_o:.2f} -> {v_n:.2f}  (+{v_n-v_o:.2f} mg/hub)")
ecu.write_map(md, matrix_new, codeblock=5)
ecu.write_map(md, matrix_new, codeblock=2)
total_changes += len(changed)

# ─── 3. SMOKE LIMITER 0C, 15C, 30C ──────────────────────────────────────────
for smoke_key in ["smoke_limiter_0c", "smoke_limiter_15c", "smoke_limiter_30c"]:
    md = MAP_DEFINITIONS[smoke_key]
    matrix_new, changed = scale_map_by_col(ecu, smoke_key, md,
        low_scale=12.0, mid_scale=4.0, min_val=5.0, abs_max=64.0)
    orig = ecu.read_map(md, codeblock=5)
    print(f"\n{sep}")
    print(f"  {md.name} [{md.dimsport_code}] — dol +12%, srodek +4%")
    new_max = max(v for row in matrix_new for v in row)
    print(f"  Przed max: {max(v for row in orig for v in row):.2f}  ->  Po max: {new_max:.2f} mg/hub")
    print(f"  Zmienionych komorek: {len(changed)} / {md.rows*md.cols}")
    ecu.write_map(md, matrix_new, codeblock=5)
    ecu.write_map(md, matrix_new, codeblock=2)
    total_changes += len(changed)

# ─── 4. BOOST TARGET (BS) — podciagnij dol ───────────────────────────────────
md = MAP_DEFINITIONS["boost_target"]
matrix_new, changed = scale_map_by_col(ecu, "boost_target", md,
    low_scale=8.0, mid_scale=3.0, min_val=1300.0, abs_max=2400.0)
print(f"\n{sep}")
print(f"  BOOST TARGET [BS] — dol +8% (szybsze spiecie turbo na nizszych RPM)")
orig = ecu.read_map(md, codeblock=5)
new_max = max(v for row in matrix_new for v in row)
print(f"  Przed max: {max(v for row in orig for v in row):.0f} mBar  ->  Po max: {new_max:.0f} mBar")
print(f"  Zmienionych komorek: {len(changed)} / {md.rows*md.cols}")
for r, c, v_o, v_n in changed[:8]:
    print(f"    RPM~{RPM_AXIS[c] if c < len(RPM_AXIS) else '?':>4}  Row {r}:  {v_o:.0f} -> {v_n:.0f} mBar  (+{v_n-v_o:.0f})")
if len(changed) > 8: print(f"    ... i {len(changed)-8} wiecej ...")
ecu.write_map(md, matrix_new, codeblock=5)
ecu.write_map(md, matrix_new, codeblock=2)
total_changes += len(changed)

# ─── 5. PUMP VOLTAGE — wiecej paliwa na dole pod obciazeniem ─────────────────
md = MAP_DEFINITIONS["pump_voltage"]
matrix_orig = ecu.read_map(md, codeblock=5)
matrix_new  = copy.deepcopy(matrix_orig)
pump_changed = []
for r in range(md.rows):
    for c in range(md.cols):
        v = matrix_orig[r][c]
        if v < 2.5:          # tylko komorki mid-high load
            continue
        if c > MID_RPM_MAX_COL:  # tylko dol i srodek RPM
            continue
        v_new = round(v * 1.05, 3)  # +5%
        if v_new > 4.45:
            v_new = 4.45
        if abs(v_new - v) > 0.001:
            pump_changed.append((r, c, v, v_new))
            matrix_new[r][c] = v_new

print(f"\n{sep}")
print(f"  PUMP VOLTAGE [PUMP] — dol/srodek RPM +5% (komorki >2.5V)")
orig_max = max(v for row in matrix_orig for v in row if v > 0)
new_max  = max(v for row in matrix_new for v in row if v > 0)
print(f"  Przed max: {orig_max:.3f}V  ->  Po max: {new_max:.3f}V")
print(f"  Zmienionych komorek: {len(pump_changed)} / {md.rows*md.cols}")
for r, c, v_o, v_n in pump_changed[:6]:
    print(f"    RPM~{RPM_AXIS[c] if c < len(RPM_AXIS) else '?':>4}  Row {r}:  {v_o:.3f}V -> {v_n:.3f}V")
ecu.write_map(md, matrix_new, codeblock=5)
ecu.write_map(md, matrix_new, codeblock=2)
total_changes += len(pump_changed)

# ─── PODSUMOWANIE ─────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print(f"  PODSUMOWANIE LOW-END FIX:")
print(f"  Lacznie zmienionych komorek: {total_changes}")
print()
print(f"  Spodziewany efekt:")
print(f"    - Wiecej momentu przy 1000-2000 RPM (3. bieg nie bedzie 'szedl')")
print(f"    - Szybsze spiecie turbo (boost wchodzi wczesniej)")
print(f"    - Lepsze przyspieszenie z niskich obrotow")
print(f"    - Wiecej paliwa przy partial throttle na dole")
print(f"{SEP}\n")

ecu.save_bin(OUTPUT_BIN)
print(f"  [SUKCES] Zapisano: {OUTPUT_BIN}")
print(f"  [UWAGA]  Przelicz sume kontrolna przed wgraniem! (WinOLS / TunerPro)")
print()
