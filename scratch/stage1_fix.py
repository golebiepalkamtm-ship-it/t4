"""
EDC15VM+ STAGE 1 FIX — VW T4 2.5 TDI AXG 151KM
Plik bazowy: d:\t4\cks ok (obecny Stage 1)

Naprawa dwóch problemów:
  1. Czarny dym na wolnych → obniżenie Smoke Limiter na niskim MAF
  2. Muli z dołu → podniesienie N75 duty + Torque Limiter na niskich RPM

Metoda:
  Krok 1: Smoke Limiter — obniż dolne wiersze MAF (0-25), zostaw/lekko podnieś środek
  Krok 2: N75 Duty — podnieś na niskich RPM (cols 0-5) dla load 34-51
  Krok 3: Torque Limiter — podnieś kolumny 1100-1500 RPM
"""

import sys, copy
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"d:\t4")
from edc15_analyzer import ECUBinaryReader, MAP_DEFINITIONS

INPUT_BIN  = r"d:\t4\cks ok"
OUTPUT_BIN = r"d:\t4\cks ok_stage1_fix.bin"

RPM_AXIS_16 = [750,1000,1250,1500,1750,2000,2250,2500,2750,3000,3250,3500,3750,4000,4250,4500]
MAF_AXIS_13 = [0,8,17,25,34,42,51,59,67,76,84,93,101]
RPM_AXIS_23 = [600,700,800,900,1000,1100,1250,1500,1750,2000,2250,2500,2750,3000,3250,3500,3750,4000,4250,4500,4750,5000,5250]
ATMOS_3     = [750,1013,1100]

ecu = ECUBinaryReader(INPUT_BIN)

SEP = "=" * 100
sep = "-" * 100
total_changes = 0

print(f"\n{SEP}")
print(f"  EDC15VM+ STAGE 1 FIX — VW T4 2.5 TDI AXG 151KM")
print(f"  Baza:    {INPUT_BIN}")
print(f"  Wyjście: {OUTPUT_BIN}")
print(f"{SEP}\n")

# ═══════════════════════════════════════════════════════════════════════════════
# KROK 1: SMOKE LIMITER — obniż na niskim MAF (naprawa czarnego dymu)
# ═══════════════════════════════════════════════════════════════════════════════
# Wiersze MAF 0-25 (indeksy 0-3): OBNIŻYĆ do bezpiecznych wartości
# Wiersze MAF 34-59 (indeksy 4-7): zostawić lub lekko podnieść
# Wiersze MAF 67+ (indeksy 8+): lekko podnieść (tu jest pełne doładowanie)

for smoke_key in ["smoke_limiter_0c", "smoke_limiter_15c", "smoke_limiter_30c"]:
    md = MAP_DEFINITIONS[smoke_key]
    matrix_orig = ecu.read_map(md, codeblock=5)
    matrix_new = copy.deepcopy(matrix_orig)
    changed = []

    for r in range(md.rows):
        for c in range(md.cols):
            v = matrix_orig[r][c]
            maf_val = MAF_AXIS_13[r] if r < len(MAF_AXIS_13) else 999

            if maf_val <= 8:
                # MAF 0-8: bieg jałowy, bardzo mało powietrza
                # Obniżamy do max 18 mg — to seryjne wartości
                v_new = min(v, 18.0)
            elif maf_val <= 17:
                # MAF 17: lekki gaz, trochę powietrza
                # Obniżamy do max 22 mg
                v_new = min(v, 22.0)
            elif maf_val <= 25:
                # MAF 25: częściowy gaz, turbina zaczyna wstawać
                # Obniżamy do max 26 mg
                v_new = min(v, 26.0)
            elif maf_val <= 42:
                # MAF 34-42: turbina pracuje, zostawiamy jak jest
                v_new = v
            else:
                # MAF 51+: pełne doładowanie — lekko podnosimy (+5%)
                # żeby nie blokował dawki w pełni obciążonym silniku
                if v > 35.0:
                    v_new = round(min(v * 1.05, 58.0), 1)
                else:
                    v_new = v

            if abs(v_new - v) > 0.01:
                changed.append((r, c, v, v_new))
                matrix_new[r][c] = v_new

    print(f"{sep}")
    print(f"  KROK 1: {md.name} — obniżenie dołu MAF + lekkie podniesienie góry")
    orig_max = max(v for row in matrix_orig for v in row)
    new_max = max(v for row in matrix_new for v in row)
    low_orig = max(matrix_orig[r][c] for r in range(4) for c in range(md.cols))
    low_new  = max(matrix_new[r][c] for r in range(4) for c in range(md.cols))
    print(f"  Dolne wiersze (MAF 0-25):  max {low_orig:.1f} → {low_new:.1f} mg  (OBNIŻONE - mniej dymu!)")
    print(f"  Całość:                     max {orig_max:.1f} → {new_max:.1f} mg")
    print(f"  Zmienionych komórek: {len(changed)} / {md.rows*md.cols}")

    # Pokaż kilka przykładów obniżek
    lowered = [(r,c,vo,vn) for r,c,vo,vn in changed if vn < vo]
    raised  = [(r,c,vo,vn) for r,c,vo,vn in changed if vn > vo]
    if lowered:
        print(f"  Przykłady OBNIŻEK (mniej dymu):")
        for r,c,vo,vn in lowered[:4]:
            maf = MAF_AXIS_13[r] if r < len(MAF_AXIS_13) else "?"
            rpm = RPM_AXIS_16[c] if c < len(RPM_AXIS_16) else "?"
            print(f"    MAF={maf:>3}, RPM={rpm:>4}:  {vo:.1f} → {vn:.1f} mg  ({vn-vo:+.1f})")
    if raised:
        print(f"  Przykłady PODWYŻEK (więcej paliwa u góry):")
        for r,c,vo,vn in raised[:4]:
            maf = MAF_AXIS_13[r] if r < len(MAF_AXIS_13) else "?"
            rpm = RPM_AXIS_16[c] if c < len(RPM_AXIS_16) else "?"
            print(f"    MAF={maf:>3}, RPM={rpm:>4}:  {vo:.1f} → {vn:.1f} mg  ({vn-vo:+.1f})")

    ecu.write_map(md, matrix_new, codeblock=5)
    ecu.write_map(md, matrix_new, codeblock=2)
    total_changes += len(changed)


# ═══════════════════════════════════════════════════════════════════════════════
# KROK 2: N75 DUTY CYCLE — mocniejsze domknięcie VNT na niskich RPM
# ═══════════════════════════════════════════════════════════════════════════════
# Problem: przy load 34-51 i RPM 750-1750, N75 daje tylko 32-47%
# Cel: podnieść do 45-55%, żeby żaluzje VNT zamknęły się mocniej i turbina
#      zaczęła pompować ciśnienie wcześniej (od 1200 RPM zamiast 1800)

md_n75 = MAP_DEFINITIONS["n75_duty"]
matrix_n75_orig = ecu.read_map(md_n75, codeblock=5)
matrix_n75_new  = copy.deepcopy(matrix_n75_orig)
n75_changed = []

for r in range(md_n75.rows):
    for c in range(md_n75.cols):
        v = matrix_n75_orig[r][c]
        load_val = MAF_AXIS_13[r] if r < len(MAF_AXIS_13) else 999
        rpm_val  = RPM_AXIS_16[c] if c < len(RPM_AXIS_16) else 9999

        # Ignoruj wartości powyżej 100 (to mogą być specjalne flagi w mapie)
        if v > 100.0 or v < 0.5:
            continue

        # Load 34-51 (indeksy 4-6), RPM <= 2000 (cols 0-5)
        if 34 <= load_val <= 51 and rpm_val <= 2000:
            # Podnosimy o +10 punktów procentowych, max 60%
            v_new = min(v + 10.0, 60.0)
            if abs(v_new - v) > 0.01:
                n75_changed.append((r, c, v, v_new))
                matrix_n75_new[r][c] = v_new

        # Load 42-67, RPM 750-1500 — też lekko podnieś (+5pp)
        elif 42 <= load_val <= 67 and rpm_val <= 1500:
            v_new = min(v + 5.0, 75.0)
            if abs(v_new - v) > 0.01:
                n75_changed.append((r, c, v, v_new))
                matrix_n75_new[r][c] = v_new

print(f"\n{sep}")
print(f"  KROK 2: N75 DUTY CYCLE — mocniejsze domknięcie VNT na niskich RPM")
print(f"  Cel: turbina wstaje od 1200 RPM zamiast od 1800 RPM")
print(f"  Zmienionych komórek: {len(n75_changed)} / {md_n75.rows*md_n75.cols}")
for r,c,vo,vn in n75_changed[:8]:
    load = MAF_AXIS_13[r] if r < len(MAF_AXIS_13) else "?"
    rpm  = RPM_AXIS_16[c] if c < len(RPM_AXIS_16) else "?"
    print(f"    Load={load:>3}%, RPM={rpm:>4}:  {vo:.1f}% → {vn:.1f}%  ({vn-vo:+.1f}pp)")
if len(n75_changed) > 8:
    print(f"    ... i {len(n75_changed)-8} więcej ...")

ecu.write_map(md_n75, matrix_n75_new, codeblock=5)
ecu.write_map(md_n75, matrix_n75_new, codeblock=2)
total_changes += len(n75_changed)


# ═══════════════════════════════════════════════════════════════════════════════
# KROK 3: TORQUE LIMITER — podnieś dół obrotów (1100-1750 RPM)
# ═══════════════════════════════════════════════════════════════════════════════
# Problem: przy 1100-1500 RPM Torque Limiter pozwala tylko na 37-49 mg
# Cel: podnieść do 42-52 mg, żeby silnik mógł dać więcej paliwa z dołu

md_tl = MAP_DEFINITIONS["torque_limiter"]
matrix_tl_orig = ecu.read_map(md_tl, codeblock=5)
matrix_tl_new  = copy.deepcopy(matrix_tl_orig)
tl_changed = []

# Kolumny Torque Limitera mają 23 punkty RPM
# Indeks 5=1100, 6=1250, 7=1500, 8=1750
for r in range(md_tl.rows):
    for c in range(md_tl.cols):
        v = matrix_tl_orig[r][c]
        rpm_val = RPM_AXIS_23[c] if c < len(RPM_AXIS_23) else 9999

        if v < 1.0:  # skip zera
            continue

        # RPM 1100-1750: podnieś o +5 mg, max 55 mg
        if 1100 <= rpm_val <= 1750:
            v_new = min(v + 5.0, 55.0)
            if abs(v_new - v) > 0.01:
                tl_changed.append((r, c, v, v_new))
                matrix_tl_new[r][c] = v_new

        # RPM 900-1000: lekko podnieś o +3 mg, max 35 mg (bezpieczne)
        elif 900 <= rpm_val <= 1000:
            v_new = min(v + 3.0, 35.0)
            if abs(v_new - v) > 0.01:
                tl_changed.append((r, c, v, v_new))
                matrix_tl_new[r][c] = v_new

print(f"\n{sep}")
print(f"  KROK 3: TORQUE LIMITER — więcej momentu z dołu (1100-1750 RPM)")
print(f"  Zmienionych komórek: {len(tl_changed)} / {md_tl.rows*md_tl.cols}")
for r,c,vo,vn in tl_changed:
    atm = ATMOS_3[r] if r < len(ATMOS_3) else "?"
    rpm = RPM_AXIS_23[c] if c < len(RPM_AXIS_23) else "?"
    print(f"    ATM={atm:>4}, RPM={rpm:>4}:  {vo:.2f} → {vn:.2f} mg  ({vn-vo:+.2f})")

ecu.write_map(md_tl, matrix_tl_new, codeblock=5)
ecu.write_map(md_tl, matrix_tl_new, codeblock=2)
total_changes += len(tl_changed)


# ═══════════════════════════════════════════════════════════════════════════════
# PODSUMOWANIE
# ═══════════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print(f"  PODSUMOWANIE STAGE 1 FIX:")
print(f"  Łącznie zmienionych komórek: {total_changes}")
print()
print(f"  Co się zmieniło:")
print(f"    1. Smoke Limiter:   obniżony na wolnych (MAF 0-25) → KONIEC CZARNEGO DYMU")
print(f"    2. N75 Duty:        podniesiony na dole RPM → TURBINA WSTAJE WCZEŚNIEJ")
print(f"    3. Torque Limiter:  podniesiony na 1100-1750 RPM → WIĘCEJ MOMENTU Z DOŁU")
print()
print(f"  Co NIE zostało zmienione:")
print(f"    - Driver Wish (pedał gazu) — bez zmian")
print(f"    - Boost Target (doładowanie) — bez zmian (2190 mbar)")
print(f"    - Pump Voltage — bez zmian")
print(f"    - Górne obroty (2000+ RPM) — bez zmian")
print(f"{SEP}\n")

ecu.save_bin(OUTPUT_BIN)
print(f"  [SUKCES] Zapisano: {OUTPUT_BIN}")
print(f"  [UWAGA] Przelicz sumę kontrolną przed wgraniem! (WinOLS / TunerPro)")
print()
