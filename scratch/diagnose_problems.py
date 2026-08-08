"""
Diagnostyka 3 problemów:
1. Dymienie na wolnych obrotach
2. Turbo lag / dziura na dole
3. Brak reakcji na gaz

Na bazie cks ok_stage1_pro.bin + 5 logów VCDS
"""
import sys, os, json
sys.path.insert(0, r"d:\t4")
from edc15_analyzer import (
    ECUBinaryReader, VCDSLogParser, EDC15Analyzer,
    MAP_DEFINITIONS, MAP_AXES,
    RPM_AXIS_16, RPM_AXIS_23, PEDAL_AXIS_9, LOAD_AXIS_13, LOAD_AXIS_14,
    SMOKE_MAF_AXIS_13, LOAD_AXIS_10
)

BIN_FILE = r"d:\t4\cks ok"
CSV_FILES = [
    r"d:\t4\LOG-01-002-004-008.CSV",
    r"d:\t4\LOG-01-003-005-002.CSV",
    r"d:\t4\LOG-01-011-010-009.CSV",
    r"d:\t4\LOG-01-014-013-012.CSV",
    r"d:\t4\LOG-01-023-019-010.CSV",
]

ecu = ECUBinaryReader(BIN_FILE)
vcds = VCDSLogParser(CSV_FILES)

print("="*90)
print("  DIAGNOSTYKA PROBLEMOW: DYMIENIE / LAG / BRAK REAKCJI NA GAZ")
print("="*90)

# ============================================================
# 1. ANALIZA DYMIENIA - Smoke Limiter Map vs MAF na dole
# ============================================================
print("\n" + "="*90)
print("  [1] DYMIENIE NA WOLNYCH OBROTACH - ANALIZA SMOKE LIMITER vs MAF")
print("="*90)

# Read all 3 smoke limiter maps
for smoke_key, temp in [("smoke_limiter_0c", "0C"), ("smoke_limiter_15c", "15C"), ("smoke_limiter_30c", "30C")]:
    smoke_def = MAP_DEFINITIONS[smoke_key]
    smoke_mx = ecu.read_map(smoke_def, codeblock=5)
    print(f"\n  Smoke Limiter {temp} ({smoke_def.rows}x{smoke_def.cols}):")
    print(f"  Y(MAF mg/hub): {SMOKE_MAF_AXIS_13}")
    print(f"  X(RPM):        {RPM_AXIS_16}")
    
    # Show first 8 columns (low-mid RPM area)
    print(f"  {'MAF':>6} |", end="")
    for c in range(min(10, smoke_def.cols)):
        print(f" {RPM_AXIS_16[c]:>6}", end="")
    print()
    print("  " + "-"*80)
    
    for r in range(smoke_def.rows):
        maf_val = SMOKE_MAF_AXIS_13[r] if r < len(SMOKE_MAF_AXIS_13) else "?"
        print(f"  {maf_val:>6} |", end="")
        for c in range(min(10, smoke_def.cols)):
            val = smoke_mx[r][c]
            # Highlight critical low values at low RPM
            marker = ""
            if c <= 5 and val < 20:  # Below 2000 RPM and low limit
                marker = "!"
            elif c <= 5 and val < 30:
                marker = "*"
            print(f" {val:>5.1f}{marker}", end="")
        print()

# Show what MAF the log actually sees at low RPM
print("\n  MAF z logow na niskich obrotach (< 2200 RPM):")
print(f"  {'RPM':>6} | {'MAFreq':>8} | {'MAFact':>8} | {'Stosunek':>8} | {'IQsmoke':>8} | {'IQdrv':>8} | {'IQtorq':>8} | Aktywny Limiter")
print("  " + "-"*100)
for dp in vcds.data_points:
    if dp.rpm < 2200 and dp.rpm > 1300:
        limiter = "?"
        iqs = {"DRV": dp.iq_driver, "TRQ": dp.iq_torque, "SMK": dp.iq_smoke}
        active = {k: v for k, v in iqs.items() if v > 0}
        if active:
            limiter = min(active, key=active.get)
            limiter_val = min(active.values())
        else:
            limiter_val = 0
        
        ratio = f"{dp.maf_actual/dp.maf_req*100:.0f}%" if dp.maf_req > 0 else "-"
        print(f"  {dp.rpm:>6.0f} | {dp.maf_req:>8.0f} | {dp.maf_actual:>8.0f} | {ratio:>8} | {dp.iq_smoke:>8.1f} | {dp.iq_driver:>8.1f} | {dp.iq_torque:>8.1f} | {limiter}={limiter_val:.1f}mg")

# ============================================================
# 2. ANALIZA TURBO LAG - Boost + N75 na dole
# ============================================================
print("\n" + "="*90)
print("  [2] TURBO LAG / DZIURA - ANALIZA BOOST + N75 NA DOLE")
print("="*90)

# Boost Target Map - show low RPM area
boost_def = MAP_DEFINITIONS["boost_target"]
boost_mx = ecu.read_map(boost_def, codeblock=5)
print(f"\n  Boost Target Map (mBar) - niskie obroty:")
print(f"  Y(IQ mg/hub): {LOAD_AXIS_10}")
print(f"  {'IQ':>6} |", end="")
for c in range(min(10, boost_def.cols)):
    print(f" {RPM_AXIS_16[c]:>6}", end="")
print()
print("  " + "-"*80)
for r in range(boost_def.rows):
    iq_val = LOAD_AXIS_10[r] if r < len(LOAD_AXIS_10) else "?"
    print(f"  {iq_val:>6} |", end="")
    for c in range(min(10, boost_def.cols)):
        print(f" {boost_mx[r][c]:>6.0f}", end="")
    print()

# N75 Precontrol Map - show low RPM area  
n75_def = MAP_DEFINITIONS["n75_duty"]
n75_mx = ecu.read_map(n75_def, codeblock=5)
print(f"\n  N75 Precontrol Map (%) - niskie obroty:")
print(f"  Y(IQ mg/hub): {LOAD_AXIS_13}")
print(f"  {'IQ':>6} |", end="")
for c in range(min(10, n75_def.cols)):
    print(f" {RPM_AXIS_16[c]:>6}", end="")
print()
print("  " + "-"*80)
for r in range(n75_def.rows):
    iq_val = LOAD_AXIS_13[r] if r < len(LOAD_AXIS_13) else "?"
    print(f"  {iq_val:>6} |", end="")
    for c in range(min(10, n75_def.cols)):
        print(f" {n75_mx[r][c]:>5.1f}", end="")
    print()

# Show boost data from logs at low RPM
print("\n  Boost z logow (< 2500 RPM):")
print(f"  {'RPM':>6} | {'BoostReq':>9} | {'BoostAct':>9} | {'Delta':>7} | {'N75':>6} | {'IQdrv':>6}")
print("  " + "-"*70)
for dp in vcds.data_points:
    if dp.rpm < 2500 and dp.boost_req > 0:
        delta = dp.boost_act - dp.boost_req
        marker = " <<<< LAG!" if delta < -100 else (" << spike" if delta > 80 else "")
        print(f"  {dp.rpm:>6.0f} | {dp.boost_req:>9.0f} | {dp.boost_act:>9.0f} | {delta:>+7.0f} | {dp.n75_duty:>5.1f}% | {dp.iq_driver:>6.1f}{marker}")

# ============================================================
# 3. ANALIZA REAKCJI NA GAZ - Driver Wish Map
# ============================================================
print("\n" + "="*90)
print("  [3] BRAK REAKCJI NA GAZ - ANALIZA DRIVER WISH MAP")
print("="*90)

dw_def = MAP_DEFINITIONS["driver_wish"]
dw_mx = ecu.read_map(dw_def, codeblock=5)
print(f"\n  Driver Wish Map (mg/hub) - Zyczenie kierowcy:")
print(f"  Y(Pedal %): {PEDAL_AXIS_9}")
print(f"  {'Pedal':>6} |", end="")
for c in range(min(10, dw_def.cols)):
    print(f" {RPM_AXIS_16[c]:>6}", end="")
print()
print("  " + "-"*80)
for r in range(dw_def.rows):
    pedal_val = PEDAL_AXIS_9[r] if r < len(PEDAL_AXIS_9) else "?"
    print(f"  {pedal_val:>6} |", end="")
    for c in range(min(10, dw_def.cols)):
        val = dw_mx[r][c]
        print(f" {val:>6.1f}", end="")
    print()

# Show full DW map (all 16 columns)
print(f"\n  Driver Wish FULL (16 kolumn):")
print(f"  {'Pedal':>6} |", end="")
for c in range(dw_def.cols):
    print(f" {RPM_AXIS_16[c]:>5}", end="")
print()
print("  " + "-"*100)
for r in range(dw_def.rows):
    pedal_val = PEDAL_AXIS_9[r] if r < len(PEDAL_AXIS_9) else "?"
    print(f"  {pedal_val:>6} |", end="")
    for c in range(dw_def.cols):
        print(f" {dw_mx[r][c]:>5.1f}", end="")
    print()

# Torque Limiter map
lc_def = MAP_DEFINITIONS["torque_limiter"]
lc_mx = ecu.read_map(lc_def, codeblock=5)
print(f"\n  Torque Limiter Map (mg/hub):")
print(f"  Y(Atm mBar): [750, 850, 950]")
print(f"  {'Atm':>6} |", end="")
for c in range(lc_def.cols):
    print(f" {RPM_AXIS_23[c]:>5}", end="")
print()
print("  " + "-"*140)
for r in range(lc_def.rows):
    atm = [750, 850, 950][r] if r < 3 else "?"
    print(f"  {atm:>6} |", end="")
    for c in range(lc_def.cols):
        print(f" {lc_mx[r][c]:>5.1f}", end="")
    print()

# ============================================================
# 4. POROWNANIE Z PLIKIEM ORYGINALNYM (cks ok)
# ============================================================
print("\n" + "="*90)
print("  [4] POROWNANIE: cks ok (obecny) vs cks ok_stage1_pro.bin")
print("="*90)

try:
    ecu_orig = ECUBinaryReader(r"d:\t4\cks ok")
    
    for map_key, map_name in [("driver_wish", "DRIVER WISH"), ("torque_limiter", "TORQUE LIMITER"), 
                               ("boost_target", "BOOST TARGET"), ("smoke_limiter_15c", "SMOKE LIMITER 15C"),
                               ("n75_duty", "N75 PRECONTROL")]:
        md = MAP_DEFINITIONS[map_key]
        orig = ecu_orig.read_map(md, codeblock=5)
        mod = ecu.read_map(md, codeblock=5)
        
        diffs = []
        for r in range(md.rows):
            for c in range(md.cols):
                if abs(orig[r][c] - mod[r][c]) > 0.01:
                    axes = MAP_AXES[map_key]
                    x_val = axes['x'][c] if c < len(axes['x']) else "?"
                    y_val = axes['y'][r] if r < len(axes['y']) else "?"
                    diffs.append((r, c, x_val, y_val, orig[r][c], mod[r][c], mod[r][c] - orig[r][c]))
        
        if diffs:
            print(f"\n  {map_name}: {len(diffs)} zmian")
            for r, c, x, y, old, new, delta in diffs[:20]:
                pct = (delta/old*100) if old != 0 else 0
                print(f"    [{r:>2}][{c:>2}] X={x}, Y={y}: {old:>8.2f} -> {new:>8.2f} ({delta:>+8.2f}, {pct:>+.0f}%)")
            if len(diffs) > 20:
                print(f"    ... i {len(diffs)-20} wiecej zmian")
        else:
            print(f"\n  {map_name}: BEZ ZMIAN")
            
except Exception as e:
    print(f"  Blad porownania: {e}")

print("\n" + "="*90)
print("  KONIEC DIAGNOSTYKI")
print("="*90)
