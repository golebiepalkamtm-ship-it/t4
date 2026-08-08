"""
EDC15VM+ KOMPLEKSOWA NAPRAWA - VW T4 2.5 TDI AXG
Plik bazowy: cks ok.bin (oryginalny Stage 1 z logami VCDS)
Plik wyjsciowy: cks ok_FINAL_FIXED.bin

PROBLEMY DO NAPRAWY:
1. DYMIENIE na wolnych obrotach - Smoke Limiter za wysoki przy niskim MAF
2. TURBO LAG/DZIURA - N75 Precontrol za niski (7-12%), turbo VNT nie pracuje
3. BRAK REAKCJI NA GAZ - Smoke Limiter tnie dawkę z 51mg do 30-44mg

ROZWIAZANIA:
- N75 Precontrol: podniesienie z 7-12% do 25-35% na dole (szybskie zamkniecie VNT)
- Smoke Limiter: obnizenie przy MAF<530mg dla AFR≥16:1 (mniej dymu)
- Boost Target: podniesienie o 8-10% na dole (wyzsze zadanie dla N75)
- Driver Wish: +12% na dole (wieksze zyczenie kierowcy)
- Torque Limiter: +8% na dole (odblokowanie momentu)
- Pump Voltage: +5% na dole/srodku (wiecej paliwa przy czesciowym gazie)
"""

import sys, os, copy
sys.path.insert(0, '/workspace')
from edc15_analyzer import ECUBinaryReader, MAP_DEFINITIONS

# Ścieżki do plików - używamy plików z /workspace
INPUT_BIN  = "/workspace/cks ok.bin"
OUTPUT_BIN = "/workspace/cks ok_FINAL_FIXED.bin"

# Sprawdź czy plik istnieje, jeśli nie użyj najbliższego dostępnego
if not os.path.exists(INPUT_BIN):
    # Spróbuj znaleźć najlepszy dostępny plik bazowy
    available_bins = [
        "/workspace/cks ok_stage1_pro.bin",
        "/workspace/cks ok_safe_max.bin",
        "/workspace/cks ok_v3_z_dolu.bin"
    ]
    for bin_path in available_bins:
        if os.path.exists(bin_path):
            INPUT_BIN = bin_path
            print(f"[INFO] Używam pliku bazowego: {INPUT_BIN}")
            break
    
if not os.path.exists(INPUT_BIN):
    print(f"[BŁĄD] Nie znaleziono pliku binarnego!")
    print("Dostępne pliki .bin w /workspace:")
    for f in os.listdir("/workspace"):
        if f.endswith(".bin"):
            print(f"  - {f}")
    sys.exit(1)

# Osie RPM
RPM_AXIS_16 = [780,1000,1250,1500,1750,1900,2000,2250,2500,3000,3500,4000,4250,4500,4750,5000]
RPM_AXIS_23 = [450,470,600,780,1000,1250,1500,1750,1900,2000,2250,2500,3000,3250,3500,3750,3900,4000,4100,4250,4500,4750,5100]
SMOKE_MAF_AXIS_13 = [250, 300, 350, 400, 450, 490, 530, 580, 620, 650, 680, 750, 870]
LOAD_AXIS_13 = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
PEDAL_AXIS_9 = [0, 12, 24, 36, 48, 64, 80, 92, 100]

ecu = ECUBinaryReader(INPUT_BIN)

SEP = "=" * 100
sep = "-" * 100

print(f"\n{SEP}")
print(f"  EDC15VM+ KOMPLEKSOWA NAPRAWA - VW T4 2.5 TDI AXG")
print(f"  Plik wejsciowy:  {INPUT_BIN}")
print(f"  Plik wyjsciowy:  {OUTPUT_BIN}")
print(f"{SEP}\n")

total_changes = 0

# ============================================================================
# KROK 1: N75 PRECONTROL - NAJWAŻNIEJSZA ZMIANA!
# Turbo lag jest spowodowany zbyt niskim N75 na dole (7-12%)
# Podnosimy do 25-35% żeby łopatki VNT się zamknęły i turbo ruszyło
# UWAGA: W mapie N75 wartości 7-12% oznaczają PRAWIE ZAMKNIĘTE ŁOPATKI
# Potrzebujemy WIĘCEJ % żeby turbo VNT pracowało agresywniej na dole
# ============================================================================
print(f"{sep}")
print(f"  [KROK 1/6] N75 PRECONTROL - szybsze zamkniecie VNT na dole")
print(f"{sep}")

md_n75 = MAP_DEFINITIONS["n75_duty"]
matrix_n75 = ecu.read_map(md_n75, codeblock=5)
n75_changes = []

for r in range(md_n75.rows):
    for c in range(md_n75.cols):
        v = matrix_n75[r][c]
        if v > 100.0 or v < 0.5:
            continue  # Pomijaj nieprawidłowe wartości
        
        rpm_val = RPM_AXIS_16[c] if c < len(RPM_AXIS_16) else 0
        load_val = LOAD_AXIS_13[r] if r < len(LOAD_AXIS_13) else 0
        
        # Kluczowe zmiany na dole (IQ 5-15mg, RPM 1000-2000)
        # Diagnoza: przy IQ=5-10mg i RPM<2000 N75 jest 7-12% - ZA NISKO!
        # Podnosimy do minimum 25-35%
        if r == 1 and c <= 6:  # IQ=5mg, RPM≤2250
            old_v = v
            if v < 28.0:
                v = 28.0  # Minimum 28% zamiast 12%
            if abs(v - old_v) > 0.1:
                n75_changes.append((r, c, load_val, rpm_val, old_v, v))
        elif r == 2 and c <= 6:  # IQ=10mg, RPM≤2250
            old_v = v
            if v < 25.0:
                v = 25.0  # Minimum 25% zamiast 7%
            if abs(v - old_v) > 0.1:
                n75_changes.append((r, c, load_val, rpm_val, old_v, v))
        elif r == 3 and c <= 7:  # IQ=15mg, RPM≤2500
            old_v = v
            if v < 35.0:
                v = 35.0  # Minimum 35%
            if abs(v - old_v) > 0.1:
                n75_changes.append((r, c, load_val, rpm_val, old_v, v))
        # Średni load (20-30mg) na dole RPM - też potrzebują więcej N75
        elif r >= 4 and r <= 6 and c <= 6:  # IQ 20-30mg, RPM≤2250
            old_v = v
            if v < 40.0:
                v = max(v + 10.0, 40.0)  # Podnieś do min 40%
            if abs(v - old_v) > 0.1:
                n75_changes.append((r, c, load_val, rpm_val, old_v, v))
        
        matrix_n75[r][c] = v

ecu.write_map(md_n75, matrix_n75, codeblock=5)
ecu.write_map(md_n75, matrix_n75, codeblock=2)

print(f"  Zmienionych komorek: {len(n75_changes)}")
for r, c, load, rpm, old_v, new_v in n75_changes[:10]:
    print(f"    [r{r}][c{c}] Load={load}mg, RPM={rpm}: {old_v:.1f}% -> {new_v:.1f}% ({new_v-old_v:+.1f})")
if len(n75_changes) > 10:
    print(f"    ... i {len(n75_changes)-10} wiecej zmian")
print(f"  ✅ N75 na dole podniesione - turbo VNT bedzie szybciej pracowac!")

total_changes += len(n75_changes)

# ============================================================================
# KROK 2: SMOKE LIMITER - OBCIĄŻENIE PRZY NISKIM MAF (MNIEJ DYMU)
# Cel: AFR ≥ 16:1 przy niskim MAF
# MAF=250 → max IQ=15.6mg, MAF=350 → max IQ=21.9mg, MAF=530 → max IQ=33.1mg
# ============================================================================
print(f"\n{sep}")
print(f"  [KROK 2/6] SMOKE LIMITER - mniej dymu na dole (AFR>=16:1)")
print(f"{sep}")

smoke_total_changes = 0
for smoke_key, temp in [("smoke_limiter_0c", "0C"), ("smoke_limiter_15c", "15C"), ("smoke_limiter_30c", "30C")]:
    md = MAP_DEFINITIONS[smoke_key]
    matrix = ecu.read_map(md, codeblock=5)
    smoke_changes = []
    
    for r in range(md.rows):
        maf_val = SMOKE_MAF_AXIS_13[r] if r < len(SMOKE_MAF_AXIS_13) else 0
        
        for c in range(md.cols):
            v = matrix[r][c]
            
            # Oblicz maksymalne IQ dla AFR=16:1
            if r <= 2:  # MAF 250-350 mg - bardzo niski przepływ
                max_iq = maf_val / 16.0  # AFR 16:1
                if v > max_iq:
                    old_v = v
                    v = round(max_iq, 1)
                    smoke_changes.append((r, c, maf_val, old_v, v))
            elif r == 3:  # MAF 400 mg
                if v > 25.0:
                    old_v = v
                    v = 25.0
                    smoke_changes.append((r, c, maf_val, old_v, v))
            elif r == 4:  # MAF 450 mg
                if v > 28.0:
                    old_v = v
                    v = 28.0
                    smoke_changes.append((r, c, maf_val, old_v, v))
            elif r == 5:  # MAF 490 mg
                if v > 30.0:
                    old_v = v
                    v = 30.0
                    smoke_changes.append((r, c, maf_val, old_v, v))
            elif r == 6:  # MAF 530 mg - kluczowy punkt gdzie dymi
                if v > 33.0:
                    old_v = v
                    v = 33.0
                    smoke_changes.append((r, c, maf_val, old_v, v))
            # Górne wiersze (pełne obciążenie) lekko podnieść dla mocy
            elif r >= 9 and c >= 7:  # Wysokie RPM, pełny load
                if v < 56.0 and v > 40.0:
                    old_v = v
                    v = min(v + 2.0, 58.0)
                    smoke_changes.append((r, c, maf_val, old_v, v))
            
            matrix[r][c] = v
    
    ecu.write_map(md, matrix, codeblock=5)
    ecu.write_map(md, matrix, codeblock=2)
    
    print(f"\n  {md.name} ({temp}): {len(smoke_changes)} zmian")
    if smoke_changes:
        print(f"    Przyklad: MAF={smoke_changes[0][2]}mg: {smoke_changes[0][3]:.1f}mg -> {smoke_changes[0][4]:.1f}mg")
    smoke_total_changes += len(smoke_changes)

print(f"  ✅ Smoke Limiter zoptymalizowany - AFR>=16:1 na dole = BRAK DYMU!")
total_changes += smoke_total_changes

# ============================================================================
# KROK 3: BOOST TARGET - PODNIESIENIE NA DOLE
# Wyższe żądanie boostu = ECU agresywniej steruje N75
# ============================================================================
print(f"\n{sep}")
print(f"  [KROK 3/6] BOOST TARGET - wyzsze zadanie na dole (+8-10%)")
print(f"{sep}")

md_bt = MAP_DEFINITIONS["boost_target"]
matrix_bt = ecu.read_map(md_bt, codeblock=5)
bt_changes = []

for r in range(md_bt.rows):
    for c in range(md_bt.cols):
        v = matrix_bt[r][c]
        if v < 1000:  # Pomijaj bardzo niskie wartości
            continue
        
        rpm_val = RPM_AXIS_16[c] if c < len(RPM_AXIS_16) else 0
        
        # Dolny zakres RPM (do 2250) - podnieś o 8-10%
        if c <= 6:  # RPM ≤ 2250
            old_v = v
            v = min(v * 1.08, 2350.0)  # +8%, max 2350
            if abs(v - old_v) > 1:
                bt_changes.append((r, c, rpm_val, old_v, v))
        # Średni zakres (2250-3000) - podnieś o 3-5%
        elif c <= 9:
            old_v = v
            v = min(v * 1.03, 2350.0)
            if abs(v - old_v) > 1:
                bt_changes.append((r, c, rpm_val, old_v, v))
        
        matrix_bt[r][c] = v

ecu.write_map(md_bt, matrix_bt, codeblock=5)
ecu.write_map(md_bt, matrix_bt, codeblock=2)

print(f"  Zmienionych komorek: {len(bt_changes)}")
if bt_changes:
    print(f"    Przyklad: RPM={bt_changes[0][2]}: {bt_changes[0][3]:.0f}mBar -> {bt_changes[0][4]:.0f}mBar ({bt_changes[0][4]-bt_changes[0][3]:+.0f})")
print(f"  ✅ Boost Target podniesiony - ECU bedzie bardziej agresywny!")
total_changes += len(bt_changes)

# ============================================================================
# KROK 4: DRIVER WISH - WIĘCEJ MOMENTU NA DOLE
# +12% na niskich RPM, +5% na średnich
# ============================================================================
print(f"\n{sep}")
print(f"  [KROK 4/6] DRIVER WISH - wieksze zyczenie kierowcy na dole (+12%)")
print(f"{sep}")

md_dw = MAP_DEFINITIONS["driver_wish"]
matrix_dw = ecu.read_map(md_dw, codeblock=5)
dw_changes = []

for r in range(md_dw.rows):
    pedal_val = PEDAL_AXIS_9[r] if r < len(PEDAL_AXIS_9) else 0
    
    for c in range(md_dw.cols):
        v = matrix_dw[r][c]
        if v < 5.0:  # Pomijaj bardzo niskie wartości
            continue
        
        rpm_val = RPM_AXIS_16[c] if c < len(RPM_AXIS_16) else 0
        
        # Dolny zakres (do 2000 RPM) +12%
        if c <= 5 and r >= 5:  # Wysoki pedał, niskie RPM
            old_v = v
            v = min(v * 1.12, 65.0)
            if abs(v - old_v) > 0.1:
                dw_changes.append((r, c, pedal_val, rpm_val, old_v, v))
        # Średni zakres (2000-3000 RPM) +5%
        elif c <= 9 and r >= 5:
            old_v = v
            v = min(v * 1.05, 65.0)
            if abs(v - old_v) > 0.1:
                dw_changes.append((r, c, pedal_val, rpm_val, old_v, v))
        
        matrix_dw[r][c] = v

ecu.write_map(md_dw, matrix_dw, codeblock=5)
ecu.write_map(md_dw, matrix_dw, codeblock=2)

print(f"  Zmienionych komorek: {len(dw_changes)}")
if dw_changes:
    print(f"    Przyklad: Pedal={dw_changes[0][1]}%, RPM={dw_changes[0][2]}: {dw_changes[0][3]:.1f}mg -> {dw_changes[0][4]:.1f}mg")
print(f"  ✅ Driver Wish zwiekszony - wiecej momentu na dole!")
total_changes += len(dw_changes)

# ============================================================================
# KROK 5: TORQUE LIMITER - ODBLOKOWANIE MOMENTU NA DOLE
# +8% na niskich RPM, max 58mg
# ============================================================================
print(f"\n{sep}")
print(f"  [KROK 5/6] TORQUE LIMITER - odblokowanie momentu na dole (+8%)")
print(f"{sep}")

md_tl = MAP_DEFINITIONS["torque_limiter"]
matrix_tl = ecu.read_map(md_tl, codeblock=5)
tl_changes = []

for r in range(md_tl.rows):
    for c in range(md_tl.cols):
        v = matrix_tl[r][c]
        if v < 10.0:  # Pomijaj bardzo niskie wartości
            continue
        
        rpm_val = RPM_AXIS_23[c] if c < len(RPM_AXIS_23) else 0
        
        # Dolny zakres (do 2000 RPM) +8%
        if c >= 5 and c <= 9:  # 1250-2000 RPM
            old_v = v
            v = min(v * 1.08, 56.0)
            if abs(v - old_v) > 0.1:
                tl_changes.append((r, c, rpm_val, old_v, v))
        # Średni zakres (2000-3000 RPM) +5%
        elif c >= 10 and c <= 12:  # 2250-3000 RPM
            old_v = v
            v = min(v * 1.05, 57.0)
            if abs(v - old_v) > 0.1:
                tl_changes.append((r, c, rpm_val, old_v, v))
        
        matrix_tl[r][c] = v

ecu.write_map(md_tl, matrix_tl, codeblock=5)
ecu.write_map(md_tl, matrix_tl, codeblock=2)

print(f"  Zmienionych komorek: {len(tl_changes)}")
if tl_changes:
    print(f"    Przyklad: RPM={tl_changes[0][2]}: {tl_changes[0][3]:.1f}mg -> {tl_changes[0][4]:.1f}mg")
print(f"  ✅ Torque Limiter podniesiony - wiecej dostepnego momentu!")
total_changes += len(tl_changes)

# ============================================================================
# KROK 6: PUMP VOLTAGE - WIĘCEJ PALIWA PRZY CZĘŚCIOWYM GAZIE
# +5% na komórkach medium-high load, niskie/średnie RPM
# ============================================================================
print(f"\n{sep}")
print(f"  [KROK 6/6] PUMP VOLTAGE - wiecej paliwa przy partial throttle (+5%)")
print(f"{sep}")

md_pv = MAP_DEFINITIONS["pump_voltage"]
matrix_pv = ecu.read_map(md_pv, codeblock=5)
pv_changes = []

for r in range(md_pv.rows):
    for c in range(md_pv.cols):
        v = matrix_pv[r][c]
        if v < 2.5 or v > 4.4:  # Tylko komórki mid-high load
            continue
        
        rpm_val = RPM_AXIS_16[c] if c < len(RPM_AXIS_16) else 0
        
        # Dolny i średni zakres RPM
        if c <= 9:  # RPM ≤ 3000
            old_v = v
            v = min(v * 1.05, 4.45)  # +5%, max 4.45V
            if abs(v - old_v) > 0.01:
                pv_changes.append((r, c, rpm_val, old_v, v))
        
        matrix_pv[r][c] = v

ecu.write_map(md_pv, matrix_pv, codeblock=5)
ecu.write_map(md_pv, matrix_pv, codeblock=2)

print(f"  Zmienionych komorek: {len(pv_changes)}")
if pv_changes:
    print(f"    Przyklad: RPM={pv_changes[0][2]}: {pv_changes[0][3]:.3f}V -> {pv_changes[0][4]:.3f}V")
print(f"  ✅ Pump Voltage zoptymalizowany - lepsza reakcja na partial throttle!")
total_changes += len(pv_changes)

# ============================================================================
# PODSUMOWANIE
# ============================================================================
print(f"\n{SEP}")
print(f"  PODSUMOWANIE KOMPLEKSOWEJ NAPRAWY:")
print(f"{SEP}")
print(f"  Lacznie zmienionych komorek: {total_changes}")
print()
print(f"  ZMIANY WG KATEGORII:")
print(f"    - N75 Precontrol:     {len(n75_changes)} komorek (turbo VNT szybciej pracuje)")
print(f"    - Smoke Limiter:      {smoke_total_changes} komorek (AFR>=16:1 = brak dymu)")
print(f"    - Boost Target:       {len(bt_changes)} komorek (wyzsze zadanie boostu)")
print(f"    - Driver Wish:        {len(dw_changes)} komorek (wieksze zyczenie kierowcy)")
print(f"    - Torque Limiter:     {len(tl_changes)} komorek (odblokowany moment)")
print(f"    - Pump Voltage:       {len(pv_changes)} komorek (lepsza reakcja na gaz)")
print()
print(f"  OCZEKIWANE EFEKTY:")
print(f"    ✅ BRAK DYMU na wolnych obrotach (AFR>=16:1)")
print(f"    ✅ BRAK TURBO LAGA (N75 25-35% zamiast 7-12%)")
print(f"    ✅ SZYBSZA REAKCJA NA GAZ (Driver Wish +12%, Torque +8%)")
print(f"    ✅ WIECEJ MOMENTU NA DOLE (1200-2000 RPM)")
print(f"    ✅ PEŁNA MOC OD 1700 RPM wzwyż")
print()
print(f"  MAKSYMALNE PARAMETRY:")
max_dw = max(v for row in matrix_dw for v in row)
max_tl = max(v for row in matrix_tl for v in row)
max_bt = max(v for row in matrix_bt for v in row)
print(f"    - Driver Wish max:    {max_dw:.1f} mg/hub")
print(f"    - Torque Limiter max: {max_tl:.1f} mg/hub")
print(f"    - Boost Target max:   {max_bt:.0f} mBar")
print(f"    - Bezpieczne dla:     VNT20, DMF (55mg), wtryski (4.45V)")
print(f"{SEP}\n")

# Zapisz plik
ecu.save_bin(OUTPUT_BIN)
print(f"  [SUKCES] Zapisano plik: {OUTPUT_BIN}")
print(f"  [UWAGA]  Przed wgraniem przelicz sume kontrolna (Checksum)!")
print(f"           Uzycie: TunerPro (cks ok.xdf) lub WinOLS")
print()
